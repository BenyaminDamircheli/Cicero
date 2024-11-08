from typing import Annotated, Any, Dict, List, Sequence, TypedDict
from langgraph.graph import Graph, StateGraph
from langchain_core.messages import BaseMessage, FunctionMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.utilities.tavily_search import TavilySearchAPIWrapper
from langchain.tools.tavily_search import TavilySearchResults
from langchain_core.tools import BaseTool
from dataclasses import dataclass
from agents.Tools.poi_finder import POIFinderAgent
from agents.Tools.zoning_checker import ZoningCheckerAgent
from agents.Tools.policy_researcher import PolicyResearcherAgent
from agents.Tools.proposal_writer import ProposalWriterAgent
from agents.Tools.poi_ranker import POIRankerAgent
import json
from dotenv import load_dotenv
import os

load_dotenv()

class State(TypedDict):
    location: str  # @TODO I think I still need to retrieve this from the database on the frontend when I call the agent. 
    coordinates: List[float]
    summary: str
    solution_outline: str
    messages: Sequence[BaseMessage]
    next_action: str
    zoning_info: Dict[str, Any]
    pois: List[Dict[str, Any]]
    ranked_pois: List[Dict[str, Any]]
    zoning_policies: List[Dict[str, Any]]
    research_results: List[Dict[str, Any]]
    research_plan: Dict[str, Any]

@dataclass
class ProposalSupervisor:
    def __init__(self):
        search = TavilySearchAPIWrapper(tavily_api_key=os.getenv("TAVILY_API_KEY"))
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.tavily_search = TavilySearchResults(api_wrapper=search, include_answer=True, max_results=5)
        self.zone_policy_researcher = PolicyResearcherAgent()
        self.poi_finder = POIFinderAgent()
        self.poi_ranker = POIRankerAgent()
        self.zoning_checker = ZoningCheckerAgent()
        #self.proposal_writer = ProposalWriterAgent()

    async def determine_research_path(self, state: State) -> State:
        """
        Determine whether zoning research is required.
        """
        prompt = f"""
        Given the following information about a complaint and a brief solution outline:
        {state["summary"]}
        {state["solution_outline"]}

        Determine if this requires:
        1. Zoning analysis (for location-specific development proposals)
        2. Web research ONLY (for non-location specific development proposals that do not require land use analysis)

        Consider:
         Consider:
        - Is this about a specific location/development?
        - Does it involve land use or building regulations?

        Reply with either:
        "NEEDS_ZONING" or "NEEDS_WEB_RESEARCH"
        """

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        if "NEEDS_ZONING" in response.content:
            state["next_action"] = "check_zoning"
        else:
            state["next_action"] = "web_research"

        return state
    
    async def check_zoning(self, state: State) -> State:
        """
        Check zoning for the given coordinates.
        """
        zoning_info = await self.zoning_checker.process(state["coordinates"])
        state["zoning_info"] = zoning_info
        state["next_action"] = "rank_pois"
        return state
    
    async def research_zoning_policies(self, state: State) -> State:
        """
        Research zoning policies for the complaint location.
        """
        policies = await self.zone_policy_researcher.process({
            "bylaw_section": state["zoning_info"]["bylaw_section"],
            "zone_type": state["zoning_info"]["zone_type"]
        })
        state["zoning_policies"] = policies
        state["next_action"] = "find_pois"
        return state
    
    async def find_pois(self, state: State) -> State:
        """
        Find POIs near the given coordinates.
        """
        pois = await self.poi_finder.process(state["location"])
        state["pois"] = pois
        state["next_action"] = "rank_pois"
        return state
    
    async def rank_pois(self, state: State) -> State:
        """
        Rank POIs based on zoning compatibility.
        """
        ranked_pois = await self.poi_ranker.process({
            "zoning_info": state["zoning_info"],
            "points_of_interest": state["pois"]
        })
        state["ranked_pois"] = ranked_pois["ranked_locations"]
        state["next_action"] = "research_plan"
        return state

    async def research_plan(self, state: State) -> State:
        """
        Create a research plan for web search that will be used to gather data that will be used in the proposal.
        """
        if state["ranked_pois"]:
            prompt = f"""
            Imagine you are a research planner for a municipal proposal that aims to address the following complaint.
            
            Complaint: {state["summary"]} 
            Location: {state["location"]}, Toronto, Canada
            Rough solution outline: {state["solution_outline"]}

            Also consider the following zoning information and potential locations that should be mentioned in the proposal:
            Zoning: {json.dumps(state['zoning_info'], indent=2)}
            Policies: {json.dumps(state['zoning_policies'], indent=2)}
            Ranked Locations: {json.dumps(state['ranked_pois'], indent=2)}

            Current research: {state["research_results"]}

            Write a set of search queries (max. 5) for important topics to gather data and information that will be used in the proposal.

            Things you should consider:
            1. Demographics in the area.
            2. Relevant data about main issues in the complaint.
            3. Similar projects/initiatives in Toronto
            4. Studies in Toronto related to the issue.
            5. Environmental impact in the area.
            6. Economic impact in the area.

            Be very specific in your search queries. YOU MUST format your response as a JSON object with the following keys:
            - topics: LIST of topics to research (4 words max per topic)
            - search_queries: LIST of search queries based on the topics.
            """
        else:
            prompt = f"""
            Imagine you are a research planner for a municipal proposal that aims to address the following complaint.
            
            Complaint: {state["summary"]} 
            Location: {state["location"]}, Toronto, Canada
            Rough solution outline: {state["solution_outline"]}
            
            Write a set of search queries for important topics to gather data and information that will be used in the proposal.

            Things you should consider:
            1. Demographics in the area.
            2. Relevant data about main issues in the complaint.
            3. Similar projects/initiatives in Toronto
            4. Studies in Toronto related to the issue.
            5. Environmental impact in the area.
            6. Economic impact in the area.

            Be very specific in your search queries. YOU MUST format your response as a JSON object with the following keys:
            - topics: LIST of topics to research (4 words max per topic)
            - search_queries: LIST of search queries based on the topics.
            """
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        state["research_plan"] = json.loads(response.content)
        state["next_action"] = "conduct_research"
        return state

    
    async def conduct_research(self, state: State) -> State:
        """
        Conduct research based on the research plan.
        """
        research_results = state["research_results"]
        for query in state["research_plan"]["search_queries"]:
            results = await self.tavily_search.ainvoke(query)
            research_results.append(results)
        
        state["research_results"] = research_results
        state["next_action"] = "evaluate_research"
        return state
    
    async def evaluate_research(self, state: State) -> State:
        """
        Evaluate the research results and determine if the research is sufficient to write a proposal.
        """
        prompt = f"""
        Evaluate if we have sufficient information for a strong proposal:

        Core Information:
        - Location: {state["location"]}
        - Zoning: {json.dumps(state['zoning_info'], indent=2)}
        - Policies: {json.dumps(state['policies'], indent=2)}
        - Ranked Locations: {json.dumps(state['ranked_pois'], indent=2)}

        Additional Research:
        {json.dumps(state['research_results'], indent=2)}

        Do we have (some but not all of the following):
        1. Demographics in the area.
        2. Relevant data about main issues in the complaint.
        3. Similar projects/initiatives in Toronto
        4. Studies in Toronto related to the issue.
        5. Environmental impact in the area.
        6. Economic impact in the area.

        Reply with either:
        "COMPLETE" if research is sufficient
        "NEEDS_MORE_RESEARCH" if additional research needed (specify gaps)
        """
        
        evaluation = await self.llm.ainvoke([HumanMessage(content=prompt)])
        
        if "needs_more_research" in evaluation.content.lower():
            state["next"] = "determine_research_needs"
        else:
            state["next"] = "end"
        
        return state

    
    def create_graph(self) -> Graph:
        graph = StateGraph(State)

        #@TODO add the proposal writer agent here
        # all nodes
        graph.add_node("determine_research_path", self.determine_research_path)
        graph.add_node("check_zoning", self.check_zoning)
        graph.add_node("get_policies", self.research_zoning_policies)
        graph.add_node("find_pois", self.find_pois)
        graph.add_node("rank_pois", self.rank_pois)
        graph.add_node("research_plan", self.research_plan)
        graph.add_node("conduct_research", self.conduct_research)
        graph.add_node("evaluate_research", self.evaluate_research)
        graph.add_node("web_research", self.web_research)
        graph.add_node("evaluate_web_research", self.evaluate_web_research)
        graph.add_node("end", lambda x: x)
        
        # entry point
        graph.set_entry_point("determine_research_path")
        
        # conditional path to determine whether we need zoning research or web research
        graph.add_conditional_edges(
            "determine_research_path",
            lambda x: x["next"],
            {
                "check_zoning": "check_zoning",
                "web_research": "web_research",
                "end": "end"
            }
        )
        
        # edges for the zoning analysis path
        graph.add_edge("check_zoning", "get_policies")
        graph.add_edge("get_policies", "find_pois")
        graph.add_edge("find_pois", "rank_pois")
        graph.add_edge("rank_pois", "research_plan")
        graph.add_edge("research_plan", "conduct_research")
        graph.add_edge("conduct_research", "evaluate_research")
        
        # edges for the web research path
        graph.add_edge("web_research", "evaluate_web_research")
        
        # conditional edges from evaluations
        graph.add_conditional_edges(
            "evaluate_research",
            lambda x: x["next"],
            {
                "research_plan": "research_plan",
                "end": "end"
            }
        )
        
        
        return graph.compile()
 
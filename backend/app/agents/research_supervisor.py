from typing import Annotated, Any, Dict, List, Sequence, TypedDict
from langgraph.graph import Graph, StateGraph, END, START
from langchain_core.messages import BaseMessage, FunctionMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from fastapi import WebSocket
from tavily import TavilyClient
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
from datetime import datetime
from websocket_manager import manager
load_dotenv()

class State(TypedDict):
    location: Annotated[str, "location"]  
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
    proposal: Dict[str, Any]
    research_feedback: str
@dataclass
class ProposalSupervisor:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.zone_policy_researcher = PolicyResearcherAgent()
        self.poi_finder = POIFinderAgent()
        self.poi_ranker = POIRankerAgent()
        self.zoning_checker = ZoningCheckerAgent()
        self.proposal_writer = ProposalWriterAgent()
    
    async def emit_status(self, task_type: str, action: str, status: str, data: Any = None):
        try:
            message = {
                "type": task_type,
                "action": action,
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "status": status
            }
            print(f"Emitting status: {message}")
            await manager.send_message(self.client_id, message)
        except Exception as e:
            print(f"Error emitting status: {e}")


    async def determine_research_path(self, state: State) -> State:
        print("\n=== DETERMINING RESEARCH PATH ===")
        print(f"Summary: {state['summary'][:100]}...")
        print(f"Solution: {state['solution_outline'][:100]}...")
        print(f"Location: {state['location']}")
        print(state)
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
        - Is this about a specific location/development?
        - Does it involve land use or building regulations?

        NOTE: you should almost always recommend zoning research, unless it really, really, really does not require zoning analysis.
        Reply with either:
        "NEEDS_ZONING" or "NEEDS_WEB_RESEARCH"
        """
        await self.emit_status(task_type="init", action="Determining Research Path", status="pending")
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        if "NEEDS_ZONING" in response.content:
            state["next_action"] = "check_zoning"
        else:
            state["next_action"] = "web_research"
        await self.emit_status(task_type="update", action="Determining Research Path", status="success")
        print(f"Next action: {state['next_action']}")

        return state
    
    async def check_zoning(self, state: State) -> State:
        print("\n=== CHECKING ZONING ===")
        print(f"Location: {state['location']}")
        print(f"Coordinates: {state['coordinates']}")
        """
        Check zoning for the given coordinates.
        """
        await self.emit_status(task_type="init", action="Checking Zoning", status="pending")
        zoning_info = await self.zoning_checker.process(state["coordinates"])
        state["zoning_info"] = zoning_info
        state["next_action"] = "rank_pois"
        await self.emit_status(task_type="update", action="Checking Zoning", status="success", data=zoning_info)
        print(f"Zoning info: {state['zoning_info']}")
        return state
    
    async def research_zoning_policies(self, state: State) -> State:
        """
        Research zoning policies for the complaint location.
        """
        await self.emit_status(task_type="init", action="Researching Zoning Policies", status="pending")
        policies = await self.zone_policy_researcher.process({
            "bylaw_section": state["zoning_info"]["bylaw_section"],
            "zone_type": state["zoning_info"]["zone_type"]
        })
        state["zoning_policies"] = policies
        state["next_action"] = "find_pois"
        await self.emit_status(task_type="update", action="Researching Zoning Policies", status="success", data=policies)
        print(f"Zoning policies: {state['zoning_policies']}")
        return state
    
    async def find_pois(self, state: State) -> State:
        """
        Find POIs near the given coordinates.
        """
        await self.emit_status(task_type="init", action="Finding POIs", status="pending")
        pois = await self.poi_finder.process(state["location"], state["zoning_info"], state["summary"], state["solution_outline"])
        state["pois"] = pois
        state["next_action"] = "rank_pois"
        await self.emit_status(task_type="update", action="Finding POIs", status="success", data=pois)
        print(f"POIs: {state['pois']}")
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
        state["next_action"] = "create_research_plan"
        await self.emit_status(task_type="update", action="POIs Found", status="success", data=state["ranked_pois"])
        print(f"Ranked POIs: {state['ranked_pois']}")
        return state

    async def create_research_plan(self, state: State) -> State:
        print("\n=== CREATING RESEARCH PLAN ===")
        print(f"Current research results count: {len(state['research_results'])}")
        print(f"Has ranked POIs: {bool(state['ranked_pois'])}")
        policies_text = state['zoning_policies']['policies']
        if state["ranked_pois"]:
            prompt = f"""
            You are a research planner for a municipal proposal addressing this complaint:
            
            Complaint: {state["summary"]} 
            Location: {state["location"]}, Toronto, Canada
            Solution outline: {state["solution_outline"]}
            Current research (may be empty): {json.dumps(state['research_results'], indent=2)}

            You may or may not have been given some feedback on your previous research. Here it is (if any):
            {state["research_feedback"]}

            Consider this zoning info:
            {json.dumps(state['zoning_info'], indent=2)}
            {policies_text}
            Ranked Locations: {json.dumps(state['ranked_pois'], indent=2)}

            You should write the queries as questions, not statements (Ex. "What is the homelessness rate in Toronto?" not "Homelessness rate in Toronto")
            Try to be specific to the location and write queries that are likely to return useful data and results.
            
            Return a JSON object with these exact keys:
            {{
                "topics": ["topic1", "topic2", ...],  // max 4 words per topic
                "search_queries": ["query1", "query2", ...]  // specific Toronto-focused queries
            }}

            Focus on:
            - Demographics
            - Toronto data about complaint issues
            - Economic impact
            - Similar Toronto projects
            - Toronto studies
            - Environmental impact
            """
        else:
            prompt = f"""
            You are a research planner for a municipal proposal addressing this complaint:
            
            Complaint: {state["summary"]} 
            Location: {state["location"]}, Toronto, Canada
            Solution outline: {state["solution_outline"]}
            Current research (may be empty): {json.dumps(state['research_results'], indent=2)}

            You should write the queries as questions, not statements (Ex. "What is the homelessness rate in Toronto?" not "Homelessness rate in Toronto").
            Try to be specific to the location and write queries that are likely to return useful data and results.

            Return a JSON object with these exact keys:
            {{
                "topics": ["topic1", "topic2", ...],  // max 4 words per topic
                "search_queries": ["query1", "query2", ...]  // specific Toronto-focused queries
            }}

            Focus on:
            - Demographics
            - Toronto data about complaint issues
            - Economic impact
            - Similar Toronto projects
            - Toronto studies
            - Environmental impact
            """
        await self.emit_status(task_type="init", action="Creating Research Plan", status="pending")
        response = await self.llm.ainvoke([
            SystemMessage(content="You are a JSON ONLY response bot. ONLY output valid JSON."),
            HumanMessage(content=prompt)
        ])    
        try:
            state["research_plan"] = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback plan if JSON parsing fails
            state["research_plan"] = {
                "topics": ["Toronto demographics", "Economic impact", "Similar projects"],
                "search_queries": [
                    f"What is the demographics of {state['location']} Toronto",
                    f"What is the economic impact of {state['location']} Toronto",
                    f"What are similar projects in {state['location']} Toronto"
                ]
            }
        await self.emit_status(task_type="update", action="Research Plan Created", status="success", data=state["research_plan"])
        state["next_action"] = "conduct_research"
        print(f"Research plan: {state['research_plan']}")
        return state

    
    async def conduct_research(self, state: State) -> State:
        print("\n=== CONDUCTING RESEARCH ===")
        print(f"Number of queries to process: {len(state['research_plan']['search_queries'])}")
        print("Queries:", json.dumps(state['research_plan']['search_queries'], indent=2))
        """
        Conduct research based on the research plan.
        """
        research_results = state["research_results"]
        await self.emit_status(task_type="init", action="Researching", status="pending")
        for query in state["research_plan"]["search_queries"]:
            print(f"\nProcessing query: {query}")
            results = self.tavily_client.search(query, include_answer=True, max_results=5)
            print(f"Tavily results for query: {query}")
            research_results.append({
                "query": query,
                "answer": results['answer'],
                "results": results['results'],
                "sources": [result['title'] for result in results['results']]
            })
        
        state["research_results"] = research_results
        await self.emit_status(task_type="update", action="Researching", status="success")
        state["next_action"] = "evaluate_research"
        print(f"Research results: {research_results}")
        return state
    
    async def evaluate_research(self, state: State) -> State:
        print("\n=== EVALUATING RESEARCH ===")
        print(f"Research results count: {len(state['research_results'])}")
        print(f"Zoning info exists: {bool(state['zoning_info'])}")
        """
        Evaluate the research results and determine if the research is sufficient to write a proposal.
        """
        prompt = f"""
        Evaluate if we have sufficient information for a strong proposal:

        Core Information:
        - Location: {state["location"]}
        - Zoning: {json.dumps(state['zoning_info'], indent=2)}
        - Policies: {json.dumps(state['zoning_policies'], indent=2)}
        - Ranked Locations: {json.dumps(state['ranked_pois'], indent=2)}

        Additional Research:
        {json.dumps(state['research_results'], indent=2)}

        Do we have (DON'T BE TOO STRICT if it has some of the following, it is enough):
        1. Demographics in the area (can be small details).
        2. Relevant data about main issues in the complaint.
        3. Similar projects/initiatives in Toronto
        4. Studies in Toronto related to the issue.
        5. Environmental impact in the area.
        6. Economic impact in the area.

        Reply with either:
        "COMPLETE" if research is sufficient
        "NEEDS_MORE_RESEARCH" if additional research needed (specify gaps)
        """
        print(f"Asking LLM for evaluation")
        await self.emit_status(task_type="init", action="Evaluating Research", status="pending")
        evaluation = await self.llm.ainvoke([HumanMessage(content=prompt)])
        print(f"LLM response: {evaluation.content}")
        await self.emit_status(task_type="update", action="Evaluating Research", status="success")
        if "needs_more_research" in evaluation.content.lower():
            state["next_action"] = "conduct_research"
        else:
            state["next_action"] = "write_proposal"
        
        return state

    async def write_proposal(self, state: State) -> State:
        print("\n=== WRITING PROPOSAL ===")
        print(f"Total research results: {len(state['research_results'])}")
        print(f"Has zoning info: {bool(state['zoning_info'])}")
        print(f"Has ranked POIs: {bool(state['ranked_pois'])}")
        """
        Write a proposal using the research results.
        """
        await self.emit_status(task_type="init", action="Writing Proposal", status="pending")
        proposal = await self.proposal_writer.process(state)
        state["proposal"] = proposal
        state["next_action"] = "end"
        await self.emit_status(task_type="update", action="Writing Proposal", status="success")
        return state

    async def web_research(self, state: State) -> State:
        print("\n=== CONDUCTING WEB RESEARCH ===")
        print(f"Location: {state['location']}")
        """
        Conduct web research for non-zoning related complaints.
        """
        prompt = f"""
        Given this complaint and solution outline:
        Complaint: {state["summary"]}
        Solution: {state["solution_outline"]}

        Generate 3-5 specific search queries to gather relevant information.
        Return ONLY a JSON array of strings, nothing else. Example:
        ["query 1", "query 2", "query 3"]
        """
        
        await self.emit_status(task_type="init", action="Web Research", status="pending")
        response = await self.llm.ainvoke([
            SystemMessage(content="You are a JSON-only response bot. Only output valid JSON."),
            HumanMessage(content=prompt)
        ])
        
        try:
            queries = json.loads(response.content)
        except json.JSONDecodeError:
            queries = [f"demographics of {state['location']} Toronto", 
                      f"economic impact of {state['location']} Toronto",
                      f"social impact of {state['location']} Toronto"]
        
        research_results = []
        for query in queries:
            print(f"\nProcessing web query: {query}")
            results = self.tavily_client.search(query, include_answer=True)
            research_results.append({
                "query": query,
                "answer": results['answer'],
                "results": results['results'],
                "sources": [result['title'] for result in results['results']]
            })

        state["research_results"] = research_results
        state["next_action"] = "evaluate_web_research"
        await self.emit_status(task_type="update", action="Web Research", status="success", data=queries)
        return state

    async def evaluate_web_research(self, state: State) -> State:
        print("\n=== EVALUATING WEB RESEARCH ===")
        print(f"Research results count: {len(state['research_results'])}")
        """
        Evaluate if web research results are sufficient.
        """
        prompt = f"""
        Evaluate if we have sufficient information for a proposal:

        Research Results:
        {json.dumps(state['research_results'], indent=2)}

        Do we have enough information about:
        1. Current situation/problem
        2. Similar initiatives/solutions
        3. Impact assessment
        4. Implementation considerations

        Reply with either:
        "COMPLETE" if research is sufficient
        "NEEDS_MORE_RESEARCH" if additional research needed
        """
        await self.emit_status(task_type="init", action="Evaluating Research", status="pending")
        evaluation = await self.llm.ainvoke([HumanMessage(content=prompt)])
        
        if "NEEDS_MORE_RESEARCH" in evaluation.content:
            state["research_feedback"] = evaluation.content
            state["next_action"] = "web_research"
        else:
            state["next_action"] = "write_proposal"

        await self.emit_status(task_type="update", action="Evaluating Research", status="success")
        
        print(f"Next action: {state['next_action']}")
        
        return state

    def create_graph(self) -> Graph:
        graph = StateGraph(State)

        
        # all nodes
        graph.add_node("determine_research_path", self.determine_research_path)
        graph.add_node("check_zoning", self.check_zoning)
        graph.add_node("get_policies", self.research_zoning_policies)
        graph.add_node("find_pois", self.find_pois)
        graph.add_node("rank_pois", self.rank_pois)
        graph.add_node("create_research_plan", self.create_research_plan)
        graph.add_node("conduct_research", self.conduct_research)
        graph.add_node("evaluate_research", self.evaluate_research)
        graph.add_node("web_research", self.web_research)
        graph.add_node("evaluate_web_research", self.evaluate_web_research)
        graph.add_node("write_proposal", self.write_proposal)
        
        # entry point
        graph.set_entry_point("determine_research_path")
        
        # conditional path to determine whether we need zoning research or web research
        graph.add_conditional_edges(
            "determine_research_path",
            lambda x: x["next_action"],
            {
                "check_zoning": "check_zoning",
                "web_research": "web_research",
                "end": END
            }
        )
        
        # edges for the zoning analysis path
        graph.add_edge("check_zoning", "get_policies")
        graph.add_edge("get_policies", "find_pois")
        graph.add_edge("find_pois", "rank_pois")
        graph.add_edge("rank_pois", "create_research_plan")
        graph.add_edge("create_research_plan", "conduct_research")
        graph.add_edge("conduct_research", "evaluate_research")
        graph.add_edge("evaluate_research", "write_proposal")
        
        # edges for the web research path
        graph.add_edge("web_research", "evaluate_web_research")
        
        # conditional edges from evaluations
        graph.add_conditional_edges(
            "evaluate_research",
            lambda x: x["next_action"],
            {
                "conduct_research": "conduct_research",
                "create_research_plan": "create_research_plan",
                "write_proposal": "write_proposal"
            }
        )

        graph.add_edge("write_proposal", END)
        
        return graph.compile()

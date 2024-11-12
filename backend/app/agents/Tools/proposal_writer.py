from agents.base_agent import BaseAgent
from datetime import datetime
from typing import Dict, Any
import os
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class ProposalWriterAgent(BaseAgent):
    """
    Writes a formal proposal based on the ranked POIs and zoning information.
    """
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
        super().__init__(tools=[])

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write a formal proposal based on the ranked POIs, research, and zoning information.
        """
        ranked_pois = context.get("ranked_pois", [])
        zoning_info = context.get("zoning_info", {})
        policies = context.get("zoning_policies", {})
        summary = context.get("summary", "")
        solution_outline = context.get("solution_outline", "")
        location = context.get("location", "")

        research = context.get("research_results", {})
        research_answers = [result.get("answer") for result in research]
        research_formatted = "\n".join(research_answers)

        research_sources = [source for result in research for source in result.get("sources", [])] # there has to be a better way to do this
        research_sources_formatted = "\n".join(research_sources)
        print(f"ranked pois: {ranked_pois}")
        print(f"zoning info: {zoning_info}")
        print(f"policies: {policies}")
        
        if ranked_pois:
            prompt = f"""
            You are a municipal government proposal writer. Create a formal proposal using the following information:

            Location: {location}

            Complaint Summary:
            {summary}

            Proposed Solution Rough Outline:
            {solution_outline}

            You are free to build upon the ideas in the outline and add more details based on the research results and other information.

            Research Results:
            {research_formatted}

            Sources: {research_sources_formatted}

            Zoning Information:
            - Zone Type: {zoning_info.get('zone_type')}
            - Bylaw Section: {zoning_info.get('bylaw_section')}
            - Zoning Policies:
            {policies.get('policies', '')}

            Recommended Locations (ranked by suitability):
            {ranked_pois}

            RULES:
            - YOU MUST mention the research in the proposal
            - YOU MUST mention the zoning information in the proposal
            - YOU MUST mention the recommended locations in the proposal
            - YOU MUST cite all sources given to you in the proposal
            - YOU SHOULD NOT use tables in the proposal

            Write a formal proposal that includes:
            1. Title page (do not include date, or prepared by. Just title and say it is for the location in the City of Toronto)
            2. Executive summary
            3. Background and Research
            4. Analysis of suggested locations (with references to the research and zoning information)
            5. Project understanding and approach
            6. Methodology
            7. Timeline
            8. Budget
            9. References

            For the analysis of suggested locations, under each location you MUST HAVE the following sections:
            - Location Name
            - Location Description
            - Zoning 
            - Plan (what you plan to do at each location)
            - Site Plan (more specifics of what you plan to do on the site)
            - Raionale (why you chose this location, make sure to reference the research and zoning information.)
                - EX. if it is a commericial residential area, you can talk about how it is a good location for a homeless shelter because it is close to amenities and services, and is still in a residential zone (this depends on the solution and the zoning information for the complaint)

            Format as a structured document with clear sections IN MARKDOWN. Focus on actionable solutions that address the core issues raised in the complaints.
            """
        else:
            prompt = f"""
            You are a municipal government proposal writer. Create a formal proposal using the following information:

            Location: {location}

            Issue Summary:
            {summary}

            Proposed Solution Outline:
            {solution_outline}

            Research Results:
            {research}

            RULES:
            - YOU MUST mention the research in the proposal
            - YOU MUST cite all sources given to you in the proposal
            - YOU SHOULD NOT use tables in the proposal

            Sources: {research_sources_formatted}

            Write a formal proposal that includes:
            1. Title page (do not include date, or prepared by. Just title and say it is for the location in the City of Toronto)
            2. Executive summary
            3. Background and Research
            4. Project understanding and approach
            5. Methodology
            6. Timeline
            7. Budget
            8. References

            Format as a structured document with clear sections. Focus on actionable solutions that address the core issues raised in the complaints.
            """

        print(f"Asking LLM for proposal")
        response = await self.llm.ainvoke(prompt)
        print(f"LLM response: {response.content}")

        return {
            "proposal": response.content,
            "metadata": {
                "date_generated": datetime.now().isoformat(),
                "version": "1.0",
                "department": "City Planning",
                "zone_type": zoning_info.get('zone_type'),
                "bylaw_reference": f"{zoning_info.get('bylaw_chapter')}.{zoning_info.get('bylaw_section')}"
            }
        }
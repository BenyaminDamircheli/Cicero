from agents.base_agent import BaseAgent
from datetime import datetime
from typing import Dict, Any

class ProposalWriterAgent(BaseAgent):
    """
    Writes a formal proposal based on the ranked POIs and zoning information.
    """
    def __init__(self):
        super().__init__(tools=[])

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        ranked_pois = context.get("ranked_locations", [])
        zoning_info = context.get("zoning_info", {})
        policies = context.get("policies", {})
        
        prompt = f"""
        You are a municipal government proposal writer. Create a formal proposal using the following information:

        Zoning Information:
        - Zone Type: {zoning_info.get('zone_type')}
        - Bylaw Chapter: {zoning_info.get('bylaw_chapter')}
        - Bylaw Section: {zoning_info.get('bylaw_section')}

        Relevant Policies:
        {policies.get('policies', '')}

        Recommended Locations:
        {ranked_pois}

        Write a formal proposal that includes:
        1. Executive Summary (100 words)
        2. Background and Context (150 words)
        3. Proposed Solutions with specific locations (200 words)
        4. Implementation Timeline (50 words)
        5. Next Steps (50 words)

        Format as a structured document with clear sections.
        """

        response = await self.llm.ainvoke(prompt)

        return {
            "proposal": response.content,
            "metadata": {
                "date_generated": datetime.now().isoformat(),
                "status": "DRAFT",
                "version": "1.0",
                "department": "City Planning",
                "zone_type": zoning_info.get('zone_type'),
                "bylaw_reference": f"{zoning_info.get('bylaw_chapter')}.{zoning_info.get('bylaw_section')}"
            }
        }
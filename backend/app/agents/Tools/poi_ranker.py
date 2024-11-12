from agents.base_agent import BaseAgent
from typing import List, Dict, Any
from .zoning_checker import ZoningCheckerAgent

class POIRankerAgent(BaseAgent):
    """
    Ranks POIs based on zoning compatibility.
    """
    def __init__(self):
        self.zoning_checker = ZoningCheckerAgent()
        super().__init__(tools=[])

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rank POIs based on zoning compatibility.
        """
        target_zone = context.get("zoning_info", {})
        pois = context.get("points_of_interest", [])
        
        if not pois:
            return {"error": "No POIs provided"}

        # Get zoning for each POI
        poi_zones = []
        for poi in pois:
            if not poi.get('coordinates'):
                continue
            zone_info = await self.zoning_checker.process(poi['coordinates'])
            if 'error' not in zone_info:
                poi_zones.append({
                    **poi,
                    "zoning": zone_info
                })

        print("asking llm for ranked pois")

        prompt = f"""
        YOU CAN ONLY RESPOND IN JSON.

        You are a zoning expert for the City of Toronto. Analyze these locations for compatibility with the target zone.
        
        You are also a member of a team that is tasked with coming up with a municipal proposal for the city of Toronto. You are tackling the following issue:
        {context.get('summary', '')}
        Here is the solution outline:
        {context.get('solution_outline', '')}

        Target Zone Information:
        - Zone Type: {target_zone.get('zone_type')}
        - Bylaw Chapter: {target_zone.get('bylaw_chapter')}
        - Bylaw Section: {target_zone.get('bylaw_section')}

        Potential Locations:
        {[{
            'name': pz['name'],
            'address': pz['address'],
            'current_zone': pz['zoning']['zone_type'],
            'current_chapter': pz['zoning']['bylaw_chapter'],
            'type': pz['type']
        } for pz in poi_zones]}

        Return exactly 3 locations (or fewer if less available) that are most compatible with the target zone.
        For each location provide:
        1. Address
        2. Name
        3. Type (just return what is given to you in text)
        4. Justification (based on the summary, solution outline, and target zone.)
        Format as a list of dictionaries.
        """

        response = await self.llm.ainvoke(prompt)
        print(f"Ranked POIs: {response.content}")

        return {
            "ranked_locations": response.content,
            "detailed_analysis": poi_zones[:3]
        }

from shapely.geometry import shape, Point
import geopandas as gpd
from agents.base_agent import BaseAgent

class ZoningCheckerAgent(BaseAgent):
    def __init__(self):
        self.zoning_data = gpd.read_file("backend/data/Zoning Area 4326.geojson")
        super().__init__(tools=[])


    async def process(self, location: list[float, float]) -> dict:
        print(f"Checking zoning for {location}")
        point = Point(location[1], location[0])
        for _, zone in self.zoning_data.iterrows():
            if shape(zone.geometry).contains(point):
                print(f"Zoning found: {zone['ZN_ZONE']}")
                return {
                    "zone_type": zone["ZN_ZONE"],
                    "bylaw_chapter": zone["ZBL_CHAPT"],
                    "bylaw_section": zone["ZBL_SECTN"],
                    "bylaw_exception": zone["ZBL_EXCPTN"],
                }
        print("No zoning found")
        return {
            "zone_type": "CR",
            "bylaw_chapter": "40",
            "bylaw_section": "40.10",
            "bylaw_exception": "",
        }

from shapely.geometry import shape, Point
import geopandas as gpd
from base_agent import BaseAgent

class ZoningCheckerAgent(BaseAgent):
    def __init__(self):
        self.zoning_data = gpd.read_file("backend/data/Zoning Area 4326.geojson")
        super().__init__(tools=[])


    def process(self, location: list[float, float]) -> dict:
        point = Point(location[1], location[0])
        for _, zone in self.zoning_data.iterrows():
            if shape(zone.geometry).contains(point):
                return {
                    "zone_type": zone["ZN_ZONE"],
                    "bylaw_chapter": zone["ZBL_CHAPT"],
                    "bylaw_section": zone["ZBL_SECTN"],
                    "bylaw_exception": zone["ZBL_EXCPTN"],
                }
        return {
            "zone_type": "CR",
            "bylaw_chapter": "40",
            "bylaw_section": "40.10",
            "bylaw_exception": "",
        }

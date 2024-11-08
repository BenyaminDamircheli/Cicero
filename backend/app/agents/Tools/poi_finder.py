from langchain_core.tools import Tool
from base_agent import BaseAgent
import os
from langchain_google_community.places_api import GooglePlacesAPIWrapper
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from typing import Dict, List
import asyncio

load_dotenv()

api_key = os.getenv("GPLACES_API_KEY")

class POIFinderAgent(BaseAgent):
    """
    Finds nearby POIs based on a given location.
    """
    def __init__(self):
        places = GooglePlacesAPIWrapper(gplaces_api_key=api_key, top_k_results=10)
        self.geolocator = Nominatim(user_agent="cicero")
        tools = [
            Tool(
                name="Find POIs",
                func=places.run,
                description="Use this tool to find nearby POIs based a set of coordinates."
            )
        ]
        super().__init__(tools=tools)

    def _get_coordinates(self, address: str) -> tuple[float, float] | None:
        try:
            location = self.geolocator.geocode(address)
            if location:
                return [location.latitude, location.longitude]
            
        except Exception as e:
            print(f"Error getting coordinates for {address}: {e}")
            return None

    def _structure_pois(self, pois:str) -> Dict[str, List[Dict]]:
        structured = []
        for poi in pois.split('\n\n\n'):
            lines = poi.split('\n')
            if len(lines) < 2:
                continue

            name = lines[0].strip('1234567890. ')
            address = lines[1].replace('Address: ', '')
            coords = self._get_coordinates(name)

            structured.append({
                'name': name,
                'address': address,
                'coordinates': coords
            })

        return structured
        
    async def process(self, location: str) -> Dict[str, List[Dict]]:
        query = f"Streets around {location} Toronto Canada"
        pois = await self.ainvoke_tool("Find POIs", query)
        structured_pois = self._structure_pois(pois)
        return {'points_of_interest': structured_pois}


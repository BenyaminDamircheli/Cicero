from agents.base_agent import BaseAgent
import os
import requests
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from typing import Dict, List

load_dotenv()

class POIFinderAgent(BaseAgent):
    """
    Finds nearby POIs based on a given location.
    """
    def __init__(self):
        self.geolocator = Nominatim(user_agent="cicero")
        super().__init__(tools=[])

    def _get_coordinates(self, address: str) -> tuple[float, float] | None:
        """
        Get the coordinates of a given address.
        """
        try:
            print(f"Getting coordinates for {address}")
            location = self.geolocator.geocode(address)
            if location:
                return [location.latitude, location.longitude]
            
        except Exception as e:
            print(f"Error getting coordinates for {address}: {e}")
            return None

    def text_search(self, query, **kwargs):
        url = "https://places.googleapis.com/v1/places:searchText"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": os.getenv("GPLACES_API_KEY"),
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types"  
        }
        
        data = {
            "textQuery": query,
            **kwargs
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()


    def _structure_places(self, places: Dict) -> List[Dict]:
        structured = []
        for place in places.get('places', []):
            structured.append({
                'name': place['displayName']['text'],
                'address': place['formattedAddress'],
                'coordinates': [
                    place['location']['latitude'],
                    place['location']['longitude']
                ],
                'type': place['types']
            })
        return structured

    async def process(self, location: str, zoning_info: Dict, summary: str, solution_outline: str) -> Dict[str, List[Dict]]:
        """
        Process the location to find nearby POIs.
        """
        coords = self._get_coordinates(f"{location}, Toronto, Canada")

        prompt = f"""
        You are a member of a team that is tasked with coming up with a municipal proposal for the city of Toronto. You are tackling the following issue:

        Create a search query for Google Places API to find relevant locations near {location} in Toronto Canada.
        The query should focus on finding public spaces, community centers, parks,etc. You should write a query that will find any locations that would be suitable for the following, however, keep your query general and not too specific so that locations can be found:
        
        Summary: {summary}

        Solution Outline: {solution_outline}

        Zoning Info: {zoning_info}

        In your query, only have one type of location (eg public spaces, parks, etc).
        Return only the query text. AND YOU MUST RETURN A QUERY IN ENGLISH WORDS PLEASE, YOU ARE NOT MAKING AN API CALL.
        """
        try:
            query = await self.llm.ainvoke(prompt)
            print(f"Query for poi finder: {query.content}")
        except Exception as e:
            print(f"Error getting query for poi finder: {e}")
            return []
        
        places = self.text_search(
            query.content,
            # Optional parameters
            locationBias={
                "circle": {
                    "center": {
                        "latitude": coords[0] if coords else 49.2827,
                        "longitude": coords[1] if coords else -79.1207
                    },
                    "radius": 5000.0
                }
            },
            maxResultCount=10
        )
        print(f"Places: {places}")
        structured_places = self._structure_places(places)
        print(f"Structured Places: {structured_places}")
        return structured_places


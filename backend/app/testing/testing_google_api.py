import requests
from dotenv import load_dotenv
import os

load_dotenv()

def text_search(query, **kwargs):
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

# Example usage
results = text_search(
    "points of interest around grace/bloor Toronto",
    locationBias={
        "circle": {
            "center": {
                "latitude": 43.6532,
                "longitude": -79.3832
            },
            "radius": 5000.0
        }
    },
    maxResultCount=10
)

print(results)

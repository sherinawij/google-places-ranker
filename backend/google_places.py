import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_PLACES_API_KEY")

url = "https://places.googleapis.com/v1/places:searchText"
def search_places(query):
    headers = {'Content-Type': 'application/json', 
               'X-Goog-Api-Key': api_key, 
               'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.priceLevel'
               }
    body = {"textQuery": query}
    response = requests.post(url, headers=headers, json=body, timeout=10)
    response.raise_for_status()
    return response.json()
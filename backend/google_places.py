import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_PLACES_API_KEY")

url = "https://places.googleapis.com/v1/places:searchText"
def search_places(query, page_token=None):
    headers = {'Content-Type': 'application/json', 
               'X-Goog-Api-Key': api_key, 
               'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount,nextPageToken'
               }
    body = {"textQuery": query}
    if page_token:
        body["pageToken"] = page_token
    response = requests.post(url, headers=headers, json=body, timeout=10)
    response.raise_for_status()
    return response.json()

def search_all(query, max_pages=3):
    results = []
    token = None
    for i in range(max_pages):
        try:
            data = search_places(query, page_token=token)
        except requests.HTTPError:
            if i == 0:
                # no responses yet, raise throws an exception
                raise

            # retry again
            time.sleep(1)
            try:
                data = search_places(query, page_token=token)
            except requests.HTTPError:
                # returns partial response
                break

        results.extend(normalize(data))
        token = data.get("nextPageToken")
        if not token:
            break
    return results

def normalize(payload):
    out = []
    for p in payload.get("places", []):
        out.append({
            "id": p.get("id"),
            "name": p.get("displayName", {}).get("text", ""),
            "address": p.get("formattedAddress", ""),
            "rating": p.get("rating"),
            "review_count": p.get("userRatingCount", 0),
        })
    return out

# for testing
# if __name__ == "__main__":
#     import json

#     print("key loaded:", bool(api_key))

#     results = search_all("sushi montreal")

#     print(f"\ngot {len(results)} results\n")
#     for r in results[:60]:
#         print(f"{r['rating']} ({r['review_count']:>5}) — {r['name']}")

#     ids = [r["id"] for r in results]
#     print(f"\nunique ids: {len(set(ids))} of {len(ids)}")
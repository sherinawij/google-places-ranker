import os
import time
import requests
from dotenv import load_dotenv
from cache import redis_client
import json

load_dotenv()
api_key = os.getenv("GOOGLE_PLACES_API_KEY")
RESULTS_TTL = 15 * 60
url = "https://places.googleapis.com/v1/places:searchText"
def search_places(query, page_token=None, max_tries=3):
    headers = {'Content-Type': 'application/json', 
               'X-Goog-Api-Key': api_key, 
               'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.reviews,places.currentOpeningHours.openNow,places.googleMapsLinks,places.currentOpeningHours.weekdayDescriptions,nextPageToken'
               }
    body = {"textQuery": query}
    if page_token:
        body["pageToken"] = page_token
    for attempt in range(max_tries):
        try: 
            response = requests.post(url, headers=headers, json=body, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            if attempt == max_tries - 1:
                raise
            wait_time = 2 ** attempt
            time.sleep(wait_time)


MAX_PAGES = 3  
def fetch_page(query, page, page_token):
    cache_key = f"places:v3:{query.strip().lower()}:page:{page}"
    cached_page = redis_client.get(cache_key)
    if cached_page is not None:
        print(f"CACHE HIT page {page}")
        return json.loads(cached_page)
    print(f"CACHE MISS page {page}")
    data = search_places(query, page_token=page_token)
    entry = {"places": normalize(data), "next": data.get("nextPageToken")}
    redis_client.set(cache_key, json.dumps(entry), ex=RESULTS_TTL)
    return entry

def search_all(query, pages=1):
    places = []
    token = None
    has_more = False
    for page in range(1, pages + 1):
        try:
            entry = fetch_page(query, page, token)
        except requests.RequestException:
            if page == 1:
                raise
            break
        places.extend(entry["places"])
        token = entry["next"]
        if token:
            has_more = True
        else: 
            has_more = False
        if not token:
            break
    return places, has_more

def normalize(payload):
    out = []
    for p in payload.get("places", []):
        current_hours = p.get("currentOpeningHours", {})
        out.append({
            "id": p.get("id"),
            "name": p.get("displayName", {}).get("text", ""),
            "address": p.get("formattedAddress", ""),
            "rating": p.get("rating"),
            "review_count": p.get("userRatingCount", 0),
            "reviews": p.get("reviews", []),
            "open_now": current_hours.get("openNow"),
            "opening_hours": current_hours.get("weekdayDescriptions", []),
            "map_link": p.get("googleMapsLinks", {}).get("placeUri", ""),
        })
    return out

# if __name__ == "__main__":
#     import json

#     print("key loaded:", bool(api_key))

#     results = search_all("sushi montreal")
#     add_score(results)
#     sorted_results = sorted(results, key=lambda place: place["score"] if place["score"] is not None else -1, reverse=True)
#     print(add_score(results)) 
    # print(f"\ngot {len(results)} results\n")
    # for r in results[:60]:
    #     print(f"{r['ratin
    # g']} ({r['review_count']:>5}) — {r['name']}")

    # ids = [r["id"] for r in results]
    # print(f"\nunique ids: {len(set(ids))} of {len(ids)}")
import os
import time
import requests
from dotenv import load_dotenv
from ranking import add_score
from cache import redis_client
import json

load_dotenv()
api_key = os.getenv("GOOGLE_PLACES_API_KEY")

url = "https://places.googleapis.com/v1/places:searchText"
def search_places(query, page_token=None, max_tries=3):
    headers = {'Content-Type': 'application/json', 
               'X-Goog-Api-Key': api_key, 
               'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.rating,places.userRatingCount,nextPageToken'
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


def search_all(query, max_pages=3):
    cache_key = f"{query.strip().lower()}"
    cached_results = redis_client.get(cache_key)
    if cached_results is not None:
        print("CACHE HIT")
        return json.loads(cached_results)
    print("CACHE MISS")
    results = []
    token = None
    for i in range(max_pages):
        try:
            data = search_places(query, page_token=token)
        except requests.RequestException:
            if i == 0:
                # no responses yet, raise throws an exception
                raise
            break

        results.extend(normalize(data))
        token = data.get("nextPageToken")
        if not token:
            break
    redis_client.set(cache_key, json.dumps(results), ex=3600)
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
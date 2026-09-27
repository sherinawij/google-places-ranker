import requests
import os
from pathlib import Path
from flask import Flask, request, render_template
from extensions import db
from models.user import UserModel
from google_places import search_all
from ranking import add_score
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from summarize import summarize_place
from cache import REDIS_URL
import time
from concurrent.futures import ThreadPoolExecutor

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

app = Flask(__name__, template_folder=FRONTEND/"templates" , static_folder=FRONTEND/"static")
limiter = Limiter(key_func=get_remote_address, app=app, storage_uri=REDIS_URL)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search", methods=['GET'])
@limiter.limit("20 per minute")
def places_search():
    start = time.perf_counter()
    query = request.args.get("query")
    if not query or not query.strip():
        return render_template("home.html", error="Please enter a search query"), 400
    results = search_all(query)
    print(results)
    elapsed = time.perf_counter() - start
    print(f"Search took {elapsed:.4f} seconds")
    add_score(results)
    sorted_results = sorted(results, key=lambda place: place["score"] if place["score"] is not None else -1, reverse=True)
    top_places = sorted_results[:3]
    with ThreadPoolExecutor(max_workers=len(top_places) or 1) as executor:
        summaries = executor.map(summarize_place, top_places)
    for place, summary in zip(top_places, summaries):
        place['summary'] = summary
    return render_template("search.html", results=sorted_results, query=query)

@app.route("/summary", methods=['GET'])
@limiter.limit("30 per minute")
def place_summary():
    query = request.args.get("query")
    place_id = request.args.get("id")
    if not query or not place_id:
        return {"error": "query and id are required"}, 400
    # look the place up server-side so clients can't send arbitrary text to Groq
    place = next((p for p in search_all(query) if p["id"] == place_id), None)
    if place is None:
        return {"error": "place not found"}, 404
    return {"summary": summarize_place(place)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
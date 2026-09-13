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

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

app = Flask(__name__, template_folder=FRONTEND/"templates" , static_folder=FRONTEND/"static")
limiter = Limiter(key_func=get_remote_address, app=app, storage_uri="redis://localhost:6379")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search", methods=['GET'])
@limiter.limit("20 per minute")
def places_search():
    query = request.args.get("query")
    results = search_all(query)
    add_score(results)
    sorted_results = sorted(results, key=lambda place: place["score"] if place["score"] is not None else -1, reverse=True)
    return render_template("search.html", results=sorted_results, query=query)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

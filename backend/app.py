import requests
import os
from pathlib import Path
from flask import Flask, request, render_template, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from extensions import db
from models.user import UserModel
from models.favorite import FavoriteModel
from google_places import search_all
from ranking import add_score
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from summarize import summarize_place
from cache import REDIS_URL
import time
from concurrent.futures import ThreadPoolExecutor
from google_places import MAX_PAGES

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

app = Flask(__name__, template_folder=FRONTEND/"templates" , static_folder=FRONTEND/"static")
limiter = Limiter(key_func=get_remote_address, app=app, storage_uri=REDIS_URL)
# SQLite locally; set DATABASE_URL (e.g. Postgres) in production
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///database.db")
db.init_app(app)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY is not set (add it to .env)")

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(UserModel, int(user_id))

# create any missing tables (doesn't change existing ones)
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("home.html")

def read_pages():
    try:
        pages = int(request.args.get("pages", 1))
    except ValueError:
        pages = 1
    return max(1, min(pages, MAX_PAGES))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    if not name or not email or not password:
        return render_template("signup.html", error="Please fill in all fields."), 400
    if "@" not in email:
        return render_template("signup.html", error="Please enter a valid email."), 400
    if len(password) < 8:
        return render_template("signup.html", error="Password must be at least 8 characters."), 400
    if UserModel.query.filter_by(email=email).first():
        return render_template("signup.html", error="That email is already registered."), 400
    if UserModel.query.filter_by(name=name).first():
        return render_template("signup.html", error="That name is already taken."), 400
    user = UserModel(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(url_for("home"))
@app.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    user = UserModel.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return render_template("login.html", error="Invalid email or password.")
    login_user(user)
    return redirect(url_for("home"))

@app.route("/search", methods=['GET'])
@limiter.limit("20 per minute")
def places_search():
    start = time.perf_counter()
    query = request.args.get("query")
    pages = read_pages()
    open_only = False
    if request.args.get("open_now") == "true":
        open_only = True
    else:
        open_only = False
    if not query or not query.strip():
        return render_template("home.html", error="Please enter a search query"), 400
    results, has_more = search_all(query, pages)
    elapsed = time.perf_counter() - start
    print(f"Search took {elapsed:.4f} seconds")
    add_score(results)
    if open_only:
        new_results = []
        for place in results:
            if place["open_now"] == True:
                new_results.append(place)
                print(place)
        results = new_results
    sorted_results = sorted(results, key=lambda place: place["score"] if place["score"] is not None else -1, reverse=True)
    top_places = sorted_results[:3]
    with ThreadPoolExecutor(max_workers=len(top_places) or 1) as executor:
        summaries = executor.map(summarize_place, top_places)
    for place, summary in zip(top_places, summaries):
        place['summary'] = summary
    fav_ids = []
    if current_user.is_authenticated:
        for fav in current_user.favorites:
            fav_ids.append(fav.place_id)
    return render_template("search.html", pages=pages, has_more=has_more, results=sorted_results, query=query, open_only=open_only, favorite_ids=fav_ids)

@app.route("/summary", methods=['GET'])
@limiter.limit("30 per minute")
def place_summary():
    query = request.args.get("query")
    place_id = request.args.get("id")
    if not query or not place_id:
        return {"error": "query and id are required"}, 400
    places, _ = search_all(query, read_pages())
    place = next((p for p in places if p["id"] == place_id), None)
    if place is None:
        return {"error": "place not found"}, 404
    return {"summary": summarize_place(place)}

@app.route("/favorites", methods=["GET"])
@login_required
def favorites():
    favorites = FavoriteModel.query.filter_by(user_id=current_user.id).order_by(FavoriteModel.created_at.desc()).all()
    return render_template("favorites.html", favorites=favorites)

@app.route("/favorites", methods=["POST"])
@login_required
def add_favorite():
    data = request.get_json(silent=True) or {}
    place_id = data.get("place_id", "")
    name = data.get("name", "")
    if not place_id or not name:
        return {"error": "place_id and name are required"}, 400
    existing = FavoriteModel.query.filter_by(user_id=current_user.id, place_id=place_id).first()
    if existing:
        return {"saved": True}
    favorite = FavoriteModel(user_id=current_user.id, place_id=place_id, name=name, address=data.get("address", ""), map_link=data.get("map_link", ""))
    db.session.add(favorite)
    db.session.commit()
    return {"saved": True}

@app.route("/favorites/<place_id>/remove", methods=["POST"])
@login_required
def remove_favorite(place_id):
    favorite = FavoriteModel.query.filter_by(user_id=current_user.id, place_id=place_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
    if request.is_json:
        return {"saved": False}
    return redirect(url_for("favorites"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
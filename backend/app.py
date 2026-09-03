from pathlib import Path
from flask import Flask, request, render_template
from extensions import db
from models.user import UserModel
from google_places import search_all
from ranking import add_score

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

app = Flask(__name__, template_folder=FRONTEND/"templates" , static_folder=FRONTEND/"static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search", methods=['GET'])
def places_search():
    query = request.args.get("query")
    results = search_all(query)
    add_score(results)
    sorted_results = sorted(results, key=lambda place: place["score"] if place["score"] is not None else -1, reverse=True)
    return render_template("search.html", results=sorted_results, query=query)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

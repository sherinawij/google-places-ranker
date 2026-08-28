from flask import Flask, request
from extensions import db
from models.user import UserModel
from google_places import search_places

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db.init_app(app)

@app.route("/")
def home():
    return "MapRank is running"

@app.route("/places/search", methods=['GET'])
def places_search():
    query = request.args.get("query")
    return search_places(query)

if __name__ == "__main__":
    app.run(debug=True)

import requests
from pathlib import Path
from flask import Flask, request, render_template
from extensions import db
from models.user import UserModel
from google_places import search_all

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

app = Flask(__name__, template_folder=FRONTEND/"templates" , static_folder=FRONTEND/"static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/places/search", methods=['GET'])
def places_search():
    query = request.args.get("query")

    try:
        result = search_all(query)

    except requests.HTTPError as e:
        code = e.response.status_code
        if code == 429:
            return "Too many requests", 429
        # app.logger.error("Places %s: %s", code, e.response.text[:500])
        return "Upstream Error", 502
    
    except requests.Timeout:
        return "Timeout Error", 504

    except requests.RequestException as e:
        return "Upstream Error", 502
    
    return result

if __name__ == "__main__":
    app.run(debug=True)

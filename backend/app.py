from flask import Flask
from extensions import db
from models.user import UserModel

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db.init_app(app)

@app.route("/")
def home():
    return "MapRank is running"

if __name__ == "__main__":
    app.run(debug=True)

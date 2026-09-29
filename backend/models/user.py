from extensions import db

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    # only the hash is stored, never the password itself
    password_hash = db.Column(db.String(255), nullable=False)
    # one user has many favorites; deleting a user deletes their favorites
    favorites = db.relationship("FavoriteModel", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"User(name = {self.name}, email = {self.email})"

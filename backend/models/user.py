from extensions import db

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    def __repr__(self): 
        return f"User(name = {self.name}, email = {self.email})"
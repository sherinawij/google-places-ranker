from datetime import datetime, timezone
from extensions import db

class FavoriteModel(db.Model):
    # the same user can't save the same place twice
    __table_args__ = (db.UniqueConstraint("user_id", "place_id"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_model.id"), nullable=False, index=True)
    place_id = db.Column(db.String(255), nullable=False)
    # a copy of the place details, so the favorites page doesn't need to call Google again
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False, default="")
    map_link = db.Column(db.String(1024), nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("UserModel", back_populates="favorites")

    def __repr__(self):
        return f"Favorite(user_id = {self.user_id}, name = {self.name})"

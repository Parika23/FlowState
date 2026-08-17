from datetime import datetime

from app.extensions import db


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    predicted_for_date = db.Column(
        db.Date,
        nullable=False
    )

    predicted_energy = db.Column(db.Float)

    predicted_completion_rate = db.Column(db.Float)

    model_version = db.Column(
        db.String(50),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        back_populates="predictions"
    )

    def __repr__(self):
        return (
            f"<Prediction {self.predicted_for_date}>"
        )
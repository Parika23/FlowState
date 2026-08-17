from datetime import datetime

from app.extensions import db


class Insight(db.Model):
    __tablename__ = "insights"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    generated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    insight_text = db.Column(
        db.Text,
        nullable=False
    )

    based_on_range = db.Column(
        db.String(50),
        nullable=False
    )

    user = db.relationship(
        "User",
        back_populates="insights"
    )

    def __repr__(self):
        return f"<Insight {self.id}>"
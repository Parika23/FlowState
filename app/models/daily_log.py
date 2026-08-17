from datetime import datetime

from app.extensions import db


class DailyLog(db.Model):
    __tablename__ = "daily_logs"

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "log_date",
            name="unique_user_log"
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    log_date = db.Column(
        db.Date,
        nullable=False
    )

    # ------------------------
    # Recovery
    # ------------------------

    sleep_hours = db.Column(
        db.Float,
        nullable=False
    )

    # ------------------------
    # Lifestyle
    # ------------------------

    recreational_screen_time = db.Column(
        db.Float,
        nullable=False
    )

    focus_hours = db.Column(
        db.Float,
        nullable=False
    )

    # ------------------------
    # Productivity
    # ------------------------

    planned_tasks = db.Column(
        db.Integer,
        nullable=False
    )

    completed_tasks = db.Column(
        db.Integer,
        nullable=False
    )

    # ------------------------
    # Well-being
    # ------------------------

    energy = db.Column(
        db.Integer,
        nullable=False
    )

    mood = db.Column(
        db.Integer,
        nullable=False
    )

    stress = db.Column(
        db.Integer,
        nullable=False
    )

    # ------------------------
    # Health
    # ------------------------

    exercise_minutes = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    water_intake = db.Column(
        db.Float,
        nullable=False
    )

    # ------------------------
    # FlowState
    # ------------------------

    flow_state = db.Column(
    db.Integer,
    nullable=False,
    default=0
    )
    
    # ------------------------
    # Journal
    # ------------------------

    notes = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # ------------------------
    # Relationships
    # ------------------------

    user = db.relationship(
        "User",
        back_populates="daily_logs"
    )

    # ------------------------
    # Computed Properties
    # ------------------------

    @property
    def productivity_ratio(self):
        """
        Returns completion ratio.

        Example:
        Planned: 8
        Completed: 6

        Returns:
        0.75
        """

        if self.planned_tasks == 0:
            return 0.0

        return round(
            self.completed_tasks / self.planned_tasks,
            3
        )

    @property
    def entered_flow_state(self):
        """
        Human-readable Flow State.
        """

        return (
            "Yes"
            if self.flow_state
            else "No"
        )

    @property
    def completion_rate(self):
        """
        Percentage of planned tasks completed.
        """

        if self.planned_tasks == 0:
            return 0

        return round(
            (self.completed_tasks / self.planned_tasks) * 100,
            1
        )
    # ------------------------
    # Debug Representation
    # ------------------------

    def __repr__(self):
        return (
            f"<DailyLog "
            f"user={self.user_id}, "
            f"date={self.log_date}, "
            f"tasks={self.completed_tasks}/{self.planned_tasks}>"
        )
"""
analytics_service.py
====================

FlowState Analytics V2

High-level analytics service responsible for exposing
dashboard metrics and summaries.

The service delegates all dataframe preparation to
AnalyticsDataFrame.
"""

from __future__ import annotations

from app.models import DailyLog
from app.services.analytics_dataframe import AnalyticsDataFrame


class AnalyticsService:
    """
    Main analytics service.

    Responsibilities
    ----------------
    • Load user logs
    • Build analytics dataframe
    • Expose dashboard metrics
    • Expose chart data
    • Expose summary statistics

    This class does NOT calculate performance scores.
    """

    def __init__(self, user_id: int):

        self.user_id = user_id

        self.logs = (
            DailyLog.query
            .filter_by(user_id=user_id)
            .order_by(DailyLog.log_date)
            .all()
        )

        self.analytics = (
            AnalyticsDataFrame
            .from_logs(self.logs)
        )

        self.df = self.analytics.dataframe

    # =====================================================
    # Basic Information
    # =====================================================

    @property
    def has_data(self) -> bool:

        return not self.df.empty

    @property
    def total_checkins(self) -> int:

        return len(self.df)

    # =====================================================
    # Internal Helper
    # =====================================================

    def _average(
        self,
        column: str,
    ) -> float:
        """
        Return the mean value of a dataframe column.
        """

        if self.df.empty:
            return 0.0

        if column not in self.df.columns:
            return 0.0

        return round(
            float(
                self.df[column].mean()
            ),
            2,
        )

    # =====================================================
    # Daily Metrics
    # =====================================================

    @property
    def average_sleep(self):

        return self._average(
            "sleep_hours"
        )

    @property
    def average_focus(self):

        return self._average(
            "focus_hours"
        )

    @property
    def average_energy(self):

        return self._average(
            "energy"
        )

    @property
    def average_mood(self):

        return self._average(
            "mood"
        )

    @property
    def average_stress(self):

        return self._average(
            "stress"
        )

    @property
    def average_water(self):

        return self._average(
            "water_intake"
        )

    @property
    def average_exercise(self):

        return self._average(
            "exercise_minutes"
        )

    @property
    def average_screen_time(self):

        return self._average(
            "recreational_screen_time"
        )

    @property
    def average_completion(self):

        return self._average(
            "completion_rate"
        )

        # =====================================================
    # Human Performance Scores
    # =====================================================

    @property
    def average_recovery_score(self):

        return self._average(
            "recovery_score"
        )

    @property
    def average_capacity_score(self):

        return self._average(
            "capacity_score"
        )

    @property
    def average_focus_investment_score(self):

        return self._average(
            "focus_investment_score"
        )

    @property
    def average_execution_score(self):

        return self._average(
            "execution_score"
        )

    @property
    def average_productivity_score(self):

        return self._average(
            "productivity_score"
        )

    @property
    def average_sustainability_score(self):

        return self._average(
            "sustainability_score"
        )

    @property
    def average_flowstate_index(self):

        return self._average(
            "flowstate_index"
        )

    # =====================================================
    # Flow Statistics
    # =====================================================

    @property
    def full_flow_days(self) -> int:

        if self.df.empty:
            return 0

        return int(
            (self.df["flow_state"] == 2).sum()
        )

    @property
    def partial_flow_days(self) -> int:

        if self.df.empty:
            return 0

        return int(
            (self.df["flow_state"] == 1).sum()
        )

    @property
    def no_flow_days(self) -> int:

        if self.df.empty:
            return 0

        return int(
            (self.df["flow_state"] == 0).sum()
        )

    @property
    def flow_state_percentage(self) -> float:

        if not self.has_data:
            return 0.0

        return round(
            (
                self.full_flow_days
                / self.total_checkins
            ) * 100,
            2,
        )

    # =====================================================
    # KPI Cards
    # =====================================================

    @property
    def performance_cards(self) -> dict:

        return {

            "recovery": self.average_recovery_score,

            "capacity": self.average_capacity_score,

            "focus": self.average_focus_investment_score,

            "execution": self.average_execution_score,

            "productivity": self.average_productivity_score,

            "sustainability": self.average_sustainability_score,

            "flowstate": self.average_flowstate_index,

        }

    @property
    def wellbeing_cards(self) -> dict:

        return {

            "sleep": self.average_sleep,

            "energy": self.average_energy,

            "mood": self.average_mood,

            "stress": self.average_stress,

            "water": self.average_water,

            "exercise": self.average_exercise,

        }

    @property
    def productivity_cards(self) -> dict:

        return {

            "focus_hours": self.average_focus,

            "screen_time": self.average_screen_time,

            "completion_rate": self.average_completion,

            "total_checkins": self.total_checkins,

            "full_flow_days": self.full_flow_days,

            "flow_percentage": self.flow_state_percentage,

        }

        # =====================================================
    # Dashboard
    # =====================================================

    @property
    def dashboard_summary(self) -> dict:
        """
        Main dashboard metrics.
        """

        return {
            "total_checkins": self.total_checkins,
            "recovery": self.average_recovery_score,
            "capacity": self.average_capacity_score,
            "focus": self.average_focus_investment_score,
            "execution": self.average_execution_score,
            "productivity": self.average_productivity_score,
            "sustainability": self.average_sustainability_score,
            "flowstate": self.average_flowstate_index,
        }

    @property
    def chart_data(self) -> list[dict]:
        """
        Return chart-ready data.
        """

        if self.df.empty:
            return []

        return self.analytics.chart_dataframe.to_dict(
            orient="records"
        )

    @property
    def correlation_matrix(self):
        """
        Return correlation matrix.
        """

        return self.analytics.correlation_dataframe

    @property
    def dataframe(self):
        """
        Return analytics dataframe.
        """

        return self.analytics.dataframe

    @property
    def overview(self) -> dict:
        """
        Complete analytics overview.

        Useful for API responses and dashboard rendering.
        """

        return {
            "summary": self.dashboard_summary,
            "performance": self.performance_cards,
            "wellbeing": self.wellbeing_cards,
            "productivity": self.productivity_cards,
            "chart_data": self.chart_data,
        }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"user_id={self.user_id}, "
            f"checkins={self.total_checkins})"
        )
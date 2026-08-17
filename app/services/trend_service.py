"""
trend_service.py
================

FlowState Analytics V2

Historical analytics, trend analysis,
rolling metrics and streak calculations.

This service never calculates performance
scores directly.

All data preparation is delegated to
AnalyticsDataFrame.
"""

from __future__ import annotations

from datetime import timedelta

import pandas as pd

from app.models import DailyLog
from app.services.analytics_dataframe import AnalyticsDataFrame


class TrendService:
    """
    Trend analytics service.
    """

    def __init__(
        self,
        user_id: int,
    ):

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
    # Helpers
    # =====================================================

    @property
    def has_data(self) -> bool:

        return not self.df.empty

    def _series(
        self,
        metric_name: str,
    ) -> pd.Series:
        """
        Return a dataframe column.

        Raises
        ------
        KeyError
            If metric does not exist.
        """

        if metric_name not in self.df.columns:

            raise KeyError(
                f"Unknown metric '{metric_name}'"
            )

        return self.df[metric_name]

    def _history_dataframe(
        self,
        metric_name: str,
    ) -> pd.DataFrame:
        """
        Return date + metric dataframe.
        """

        return self.df[
            [
                "log_date",
                metric_name,
            ]
        ].copy()

        # =====================================================
    # History
    # =====================================================

    def metric_history(
        self,
        metric_name: str,
    ) -> list[dict]:
        """
        Return historical values for a metric.
        """

        history = self._history_dataframe(metric_name)

        history["date"] = (
            history["log_date"]
            .dt.strftime("%d %b")
        )

        history.rename(
            columns={
                metric_name: "score",
            },
            inplace=True,
        )

        return (
            history[
                [
                    "date",
                    "score",
                ]
            ]
            .round(2)
            .to_dict(
                orient="records"
            )
        )

    # =====================================================
    # Chart.js Dataset
    # =====================================================

    def chart_data(
        self,
        metric_name: str,
    ) -> dict:
        """
        Return Chart.js compatible dataset.
        """

        history = self.metric_history(metric_name)

        return {

            "labels": [
                row["date"]
                for row in history
            ],

            "values": [
                row["score"]
                for row in history
            ]

        }

    # =====================================================
    # Moving Averages
    # =====================================================

    def weekly_average(
        self,
        metric_name: str,
    ) -> float:

        if self.df.empty:
            return 0.0

        latest = self.df["log_date"].max()

        start = latest - timedelta(days=6)

        dataframe = self.df[
            self.df["log_date"] >= start
        ]

        return round(
            float(
                dataframe[metric_name].mean()
            ),
            2,
        )

    def monthly_average(
        self,
        metric_name: str,
    ) -> float:

        if self.df.empty:
            return 0.0

        latest = self.df["log_date"].max()

        start = latest - timedelta(days=29)

        dataframe = self.df[
            self.df["log_date"] >= start
        ]

        return round(
            float(
                dataframe[metric_name].mean()
            ),
            2,
        )

    def rolling_average(
        self,
        metric_name: str,
        window: int = 7,
    ) -> list[dict]:
        """
        Return rolling averages.
        """

        dataframe = self._history_dataframe(
            metric_name
        ).copy()

        dataframe["average"] = (
            dataframe[metric_name]
            .rolling(
                window=window,
                min_periods=1,
            )
            .mean()
        )

        dataframe["date"] = (
            dataframe["log_date"]
            .dt.strftime("%d %b")
        )

        return (
            dataframe[
                [
                    "date",
                    "average",
                ]
            ]
            .round(2)
            .to_dict(
                orient="records"
            )
        )

         # =====================================================
    # Trend Analysis
    # =====================================================

    def trend_direction(
        self,
        metric_name: str,
    ) -> str:
        """
        Determine whether a metric is improving,
        declining or stable.
        """

        if self.df.empty:
            return "No Data"

        values = self._series(metric_name)

        if len(values) < 2:
            return "Not Enough Data"

        difference = values.iloc[-1] - values.iloc[0]

        if difference >= 5:
            return "Improving"

        if difference <= -5:
            return "Declining"

        return "Stable"

    def improvement_percentage(
        self,
        metric_name: str,
    ) -> float:
        """
        Percentage improvement from first
        recorded value.
        """

        if self.df.empty:
            return 0.0

        values = self._series(metric_name)

        if len(values) < 2:
            return 0.0

        first = values.iloc[0]
        last = values.iloc[-1]

        if first == 0:
            return 0.0

        return round(
            ((last - first) / first) * 100,
            2,
        )

    # =====================================================
    # Streak Analysis
    # =====================================================

    @property
    def current_streak(self) -> int:
        """
        Current consecutive logging streak.
        """

        if self.df.empty:
            return 0

        dates = (
            self.df["log_date"]
            .sort_values()
            .tolist()
        )

        streak = 1

        for i in range(
            len(dates) - 1,
            0,
            -1,
        ):

            if (
                dates[i] - dates[i - 1]
            ).days == 1:

                streak += 1

            else:
                break

        return streak

    @property
    def best_streak(self) -> int:
        """
        Longest consecutive logging streak.
        """

        if self.df.empty:
            return 0

        dates = (
            self.df["log_date"]
            .sort_values()
            .tolist()
        )

        best = 1
        current = 1

        for i in range(
            1,
            len(dates),
        ):

            if (
                dates[i] - dates[i - 1]
            ).days == 1:

                current += 1
                best = max(best, current)

            else:

                current = 1

        return best

    # =====================================================
    # Dashboard Helpers
    # =====================================================

    @property
    def trend_summary(self) -> dict:
        """
        High-level trend overview.
        """

        return {

            "flowstate": {
                "weekly_average":
                    self.weekly_average(
                        "flowstate_index"
                    ),
                "monthly_average":
                    self.monthly_average(
                        "flowstate_index"
                    ),
                "trend":
                    self.trend_direction(
                        "flowstate_index"
                    ),
                "improvement":
                    self.improvement_percentage(
                        "flowstate_index"
                    ),
            },

            "productivity": {
                "weekly_average":
                    self.weekly_average(
                        "productivity_score"
                    ),
                "monthly_average":
                    self.monthly_average(
                        "productivity_score"
                    ),
                "trend":
                    self.trend_direction(
                        "productivity_score"
                    ),
                "improvement":
                    self.improvement_percentage(
                        "productivity_score"
                    ),
            },

            "streaks": {
                "current":
                    self.current_streak,
                "best":
                    self.best_streak,
            }

        }

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"user_id={self.user_id}, "
            f"rows={len(self.df)})"
        )  
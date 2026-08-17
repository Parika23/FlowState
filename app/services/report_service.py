"""
FlowState Analytics V2

Unified reporting service for dashboards,
charts and analytics exports.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

# Required for Flask/server environments where
# no graphical display is available.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns

from app.services.analytics_service import AnalyticsService
from app.services.trend_service import TrendService
from app.services.insights_service import InsightsService
from app.services.prediction_service import PredictionService


class ReportService:
    """
    Central reporting service.

    Combines analytics, trends, insights,
    predictions and visual reports.
    """

    def __init__(
        self,
        user_id: int,
    ):

        self.analytics = AnalyticsService(
            user_id
        )

        self.trends = TrendService(
            user_id
        )

        self.insights = InsightsService(
            user_id
        )

        self.predictions = PredictionService(
            user_id
        )

        # Cache generated charts so that
        # accessing report.charts multiple times
        # does not regenerate every chart.
        self._charts_cache = None

    # =====================================================
    # Dashboard
    # =====================================================

    @property
    def dashboard_data(self) -> dict:
        """
        Complete dashboard reporting payload.
        """

        return {

            "summary":
                self.analytics.dashboard_summary,

            "insights":
                self.insights.insights,

            "predictions":
                self.predictions.prediction_summary,

            "charts":
                self.charts,

        }

    # =====================================================
    # Analytics Cards
    # =====================================================

    @property
    def analytics_cards(self) -> list[dict]:
        """
        Human-readable analytics cards.
        """

        summary = (
            self.analytics.dashboard_summary
        )

        prediction = (
            self.predictions.prediction_summary
        )

        return [

            {
                "title":
                    "FlowState Index",

                "value":
                    summary["flowstate"],

                "prediction":
                    prediction[
                        "flowstate_index"
                    ],

                "icon":
                    "🌊",
            },

            {
                "title":
                    "Productivity",

                "value":
                    summary["productivity"],

                "prediction":
                    prediction[
                        "productivity_score"
                    ],

                "icon":
                    "🎯",
            },

            {
                "title":
                    "Recovery",

                "value":
                    summary["recovery"],

                "prediction":
                    prediction[
                        "recovery_score"
                    ],

                "icon":
                    "😴",
            },

            {
                "title":
                    "Execution",

                "value":
                    summary["execution"],

                "icon":
                    "⚡",
            },

            {
                "title":
                    "Capacity",

                "value":
                    summary["capacity"],

                "icon":
                    "🧠",
            },

        ]

    # =====================================================
    # Insights
    # =====================================================

    @property
    def dashboard_insights(self) -> list[dict]:
        """
        Human-readable dashboard insights.
        """

        return self.insights.insights

    # =====================================================
    # Chart Directory
    # =====================================================

    @property
    def charts_directory(self) -> Path:
        """
        Directory used for generated chart images.
        """

        directory = (
            Path("app")
            / "static"
            / "charts"
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return directory

    # =====================================================
    # Matplotlib Helper
    # =====================================================

    def _save_line_chart(
        self,
        history: list[dict],
        title: str,
        filename: str,
        ylabel: str,
    ) -> str:
        """
        Generate and save a clean performance trend chart.

        Designed for user-facing Analytics visualizations.
        """

        if not history:
            return ""

        labels = [
            item["date"]
            for item in history
        ]

        values = [
            item["score"]
            for item in history
        ]

        figure, axis = plt.subplots(
            figsize=(7, 4)
        )

        axis.plot(
            labels,
            values,
            marker="o",
            linewidth=2,
            markersize=5,
        )

        axis.set_title(
            title,
            fontsize=13,
            fontweight="bold",
            pad=12,
        )

        axis.set_xlabel(
            "Date",
            fontsize=10,
        )

        axis.set_ylabel(
            ylabel,
            fontsize=10,
        )

        # All performance scores use a consistent
        # 0–100 scale.
        axis.set_ylim(
            0,
            100,
        )

        axis.grid(
            axis="y",
            alpha=0.2,
        )

        axis.tick_params(
            axis="x",
            rotation=45,
            labelsize=9,
        )

        axis.tick_params(
            axis="y",
            labelsize=9,
        )

        figure.tight_layout()

        path = (
            self.charts_directory
            / filename
        )

        figure.savefig(
            path,
            dpi=120,
            bbox_inches="tight",
        )

        plt.close(
            figure
        )

        return (
            f"charts/{filename}"
        )

    # =====================================================
    # FlowState Chart
    # =====================================================

    @property
    def flowstate_chart(self) -> str:
        """
        FlowState Index trend.
        """

        history = (
            self.trends.metric_history(
                "flowstate_index"
            )
        )

        return self._save_line_chart(
            history=history,
            title="FlowState Over Time",
            filename="flowstate_trend.png",
            ylabel="FlowState Index",
        )

    # =====================================================
    # Productivity Chart
    # =====================================================

    @property
    def productivity_chart(self) -> str:
        """
        Productivity trend.
        """

        history = (
            self.trends.metric_history(
                "productivity_score"
            )
        )

        return self._save_line_chart(
            history=history,
            title="Productivity Over Time",
            filename="productivity_trend.png",
            ylabel="Productivity Score",
        )

    # =====================================================
    # Recovery Chart
    # =====================================================

    @property
    def recovery_chart(self) -> str:
        """
        Recovery trend.
        """

        history = (
            self.trends.metric_history(
                "recovery_score"
            )
        )

        return self._save_line_chart(
            history=history,
            title="Recovery Over Time",
            filename="recovery_trend.png",
            ylabel="Recovery Score",
        )

    # =====================================================
    # Sleep Chart
    # =====================================================

    @property
    def sleep_chart(self) -> str:
        """
        Sleep trend.

        Sleep is measured in hours, so this chart
        intentionally does not use the 0–100 score scale.
        """

        history = (
            self.trends.metric_history(
                "sleep_hours"
            )
        )

        if not history:
            return ""

        labels = [
            item["date"]
            for item in history
        ]

        values = [
            item["score"]
            for item in history
        ]

        figure, axis = plt.subplots(
            figsize=(7, 4)
        )

        axis.plot(
            labels,
            values,
            marker="o",
            linewidth=2,
            markersize=5,
        )

        axis.set_title(
            "Sleep Over Time",
            fontsize=13,
            fontweight="bold",
            pad=12,
        )

        axis.set_xlabel(
            "Date",
            fontsize=10,
        )

        axis.set_ylabel(
            "Sleep Hours",
            fontsize=10,
        )

        axis.grid(
            axis="y",
            alpha=0.2,
        )

        axis.tick_params(
            axis="x",
            rotation=45,
            labelsize=9,
        )

        axis.tick_params(
            axis="y",
            labelsize=9,
        )

        figure.tight_layout()

        path = (
            self.charts_directory
            / "sleep_trend.png"
        )

        figure.savefig(
            path,
            dpi=120,
            bbox_inches="tight",
        )

        plt.close(
            figure
        )

        return (
            "charts/sleep_trend.png"
        )

    # =====================================================
    # All Charts
    # =====================================================

    @property
    def charts(self) -> dict:
        """
        Generate Analytics charts once and reuse them
        for the lifetime of this ReportService instance.
        """

        if self._charts_cache is None:

            self._charts_cache = {

                "flowstate":
                    self.flowstate_chart,

                "productivity":
                    self.productivity_chart,

                "recovery":
                    self.recovery_chart,

                "sleep":
                    self.sleep_chart,

                "correlation":
                    self.correlation_heatmap,

            }

        return self._charts_cache

    # =====================================================
    # Advanced Analytics
    # =====================================================

    @property
    def correlation_heatmap(self) -> str:
        """
        Generate a correlation heatmap.

        This visualization is intended for deeper
        analytical exploration rather than the
        primary Dashboard.
        """

        analytics_dataframe = (
            self.analytics.analytics
        )

        if analytics_dataframe.is_empty:
            return ""

        dataframe = (
            analytics_dataframe.numeric_dataframe
        )

        if dataframe.empty:
            return ""

        correlation = dataframe.corr()

        figure, axis = plt.subplots(
            figsize=(10, 8)
        )

        sns.heatmap(
            correlation,
            annot=True,
            fmt=".2f",
            cmap="Blues",
            vmin=-1,
            vmax=1,
            center=0,
            linewidths=0.5,
            ax=axis,
        )

        axis.set_title(
            "How Your Metrics Move Together",
            fontsize=14,
            fontweight="bold",
            pad=14,
        )

        axis.tick_params(
            axis="x",
            rotation=45,
            labelsize=9,
        )

        axis.tick_params(
            axis="y",
            rotation=0,
            labelsize=9,
        )

        figure.tight_layout()

        path = (
            self.charts_directory
            / "correlation_heatmap.png"
        )

        figure.savefig(
            path,
            dpi=120,
            bbox_inches="tight",
        )

        plt.close(
            figure
        )

        return (
            "charts/correlation_heatmap.png"
        )

    # =====================================================
    # CSV Export
    # =====================================================

    def export_csv(
        self,
        filename: str = "analytics_export.csv",
    ) -> str:
        """
        Export analytics data as CSV.
        """

        path = (
            self.charts_directory.parent
            / filename
        )

        self.analytics.dataframe.to_csv(
            path,
            index=False,
        )

        return str(path)

    # =====================================================
    # Excel Export
    # =====================================================

    def export_excel(
        self,
        filename: str = "analytics_export.xlsx",
    ) -> str:
        """
        Export analytics data as Excel.
        """

        path = (
            self.charts_directory.parent
            / filename
        )

        self.analytics.dataframe.to_excel(
            path,
            index=False,
        )

        return str(path)

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"user_id={self.analytics.user_id})"
        )
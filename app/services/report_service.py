"""
FlowState Analytics V2

Unified reporting service for dashboards,
charts and analytics exports.
"""

from __future__ import annotations

import hashlib
import json
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

from flask import current_app

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

        self.user_id = user_id

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

        # Prevent repeated chart generation during
        # the same request.
        self._charts_cache = None

        # Prevent repeated database calls for the
        # same metric during the same request.
        self._history_cache = {}

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

        Each user gets a separate directory so that
        cached charts cannot overwrite each other.
        """

        directory = (
            Path("app")
            / "static"
            / "charts"
            / f"user_{self.user_id}"
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return directory

    # =====================================================
    # History Cache
    # =====================================================

    def _get_history(
        self,
        metric: str,
    ) -> list[dict]:
        """
        Retrieve metric history once per request.
        """

        if metric not in self._history_cache:

            self._history_cache[metric] = (
                self.trends.metric_history(
                    metric
                )
            )

        return self._history_cache[metric]

    # =====================================================
    # Chart Cache Key
    # =====================================================

    def _chart_cache_name(
        self,
        prefix: str,
        data,
    ) -> str:
        """
        Create a deterministic filename based on the
        chart's underlying data.

        If the data hasn't changed, the same PNG filename
        is reused and Matplotlib/Seaborn does not need to
        regenerate the chart.
        """

        try:

            serialized = json.dumps(
                data,
                sort_keys=True,
                default=str,
            )

        except TypeError:

            serialized = str(data)

        digest = hashlib.md5(
            serialized.encode("utf-8")
        ).hexdigest()[:12]

        return (
            f"{prefix}_{digest}.png"
        )

    # =====================================================
    # Cached Chart Path
    # =====================================================

    def _cached_chart_path(
        self,
        filename: str,
    ) -> tuple[Path, str]:
        """
        Return the filesystem path and Flask static
        path for a cached chart.
        """

        path = (
            self.charts_directory
            / filename
        )

        static_path = (
            f"charts/user_{self.user_id}/{filename}"
        )

        return path, static_path

    # =====================================================
    # Matplotlib Helper
    # =====================================================

    def _save_line_chart(
        self,
        history: list[dict],
        title: str,
        filename_prefix: str,
        ylabel: str,
        use_score_scale: bool = True,
    ) -> str:
        """
        Generate a line chart only when its underlying
        data has changed.
        """

        if not history:
            return ""

        filename = self._chart_cache_name(
            filename_prefix,
            {
                "history": history,
                "title": title,
                "ylabel": ylabel,
            },
        )

        path, static_path = (
            self._cached_chart_path(
                filename
            )
        )

        # Reuse the existing chart when the same
        # data has already been rendered.
        if path.exists():
            return static_path

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

        if use_score_scale:

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

        figure.savefig(
            path,
            dpi=120,
            bbox_inches="tight",
        )

        plt.close(
            figure
        )

        return static_path

    # =====================================================
    # FlowState Chart
    # =====================================================

    @property
    def flowstate_chart(self) -> str:
        """
        FlowState Index trend.
        """

        history = self._get_history(
            "flowstate_index"
        )

        return self._save_line_chart(
            history=history,
            title="FlowState Over Time",
            filename_prefix="flowstate_trend",
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

        history = self._get_history(
            "productivity_score"
        )

        return self._save_line_chart(
            history=history,
            title="Productivity Over Time",
            filename_prefix="productivity_trend",
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

        history = self._get_history(
            "recovery_score"
        )

        return self._save_line_chart(
            history=history,
            title="Recovery Over Time",
            filename_prefix="recovery_trend",
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
        intentionally does not use the 0–100 scale.
        """

        history = self._get_history(
            "sleep_hours"
        )

        if not history:
            return ""

        filename = self._chart_cache_name(
            "sleep_trend",
            {
                "history": history,
                "title": "Sleep Over Time",
                "ylabel": "Sleep Hours",
            },
        )

        path, static_path = (
            self._cached_chart_path(
                filename
            )
        )

        if path.exists():
            return static_path

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

        figure.savefig(
            path,
            dpi=120,
            bbox_inches="tight",
        )

        plt.close(
            figure
        )

        return static_path

    # =====================================================
    # Performance Comparison
    # =====================================================

    @property
    def performance_comparison_chart(
        self,
    ) -> str:
        """
        Compare the main performance areas.

        The chart is regenerated only when the underlying
        performance values change.
        """

        summary = (
            self.analytics.dashboard_summary
        )

        values = {
            "FlowState":
                summary.get("flowstate", 0),

            "Productivity":
                summary.get("productivity", 0),

            "Recovery":
                summary.get("recovery", 0),

            "Execution":
                summary.get("execution", 0),

            "Capacity":
                summary.get("capacity", 0),
        }

        filename = self._chart_cache_name(
            "performance_comparison",
            values,
        )

        path, static_path = (
            self._cached_chart_path(
                filename
            )
        )

        if path.exists():
            return static_path

        figure, axis = plt.subplots(
            figsize=(7, 4.2)
        )

        bars = axis.bar(
            list(values.keys()),
            list(values.values()),
        )

        axis.set_title(
            "Your Performance Areas",
            fontsize=14,
            fontweight="bold",
            pad=12,
        )

        axis.set_ylabel(
            "Score",
            fontsize=10,
        )

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
            rotation=20,
        )

        for bar, value in zip(
            bars,
            values.values(),
        ):

            axis.text(
                bar.get_x()
                + bar.get_width() / 2,
                float(value) + 2,
                f"{float(value):.1f}",
                ha="center",
                fontsize=9,
            )

        figure.tight_layout()

        figure.savefig(
            path,
            dpi=120,
            bbox_inches="tight",
        )

        plt.close(
            figure
        )

        return static_path

    # =====================================================
    # Trend Interpretation
    # =====================================================

    def _trend_interpretation(
        self,
        history: list[dict],
        metric_name: str,
        unit: str = "score",
    ) -> str:
        """
        Create a simple, data-driven interpretation
        for a trend chart.

        The interpretation is descriptive only.
        It does not make predictions.
        """

        if not history or len(history) < 3:

            return (
                "Keep logging your daily habits to build "
                "a clearer trend over time."
            )

        values = [
            float(item["score"])
            for item in history
            if item.get("score") is not None
        ]

        if len(values) < 3:

            return (
                "Keep logging your daily habits to build "
                "a clearer trend over time."
            )

        midpoint = len(values) // 2

        earlier = values[:midpoint]

        recent = values[midpoint:]

        earlier_average = (
            sum(earlier)
            / len(earlier)
        )

        recent_average = (
            sum(recent)
            / len(recent)
        )

        difference = (
            recent_average
            - earlier_average
        )

        average = (
            sum(values)
            / len(values)
        )

        if average == 0:

            variability = 0

        else:

            variability = (
                max(values)
                - min(values)
            ) / average

        if variability >= 0.30:

            trend_type = "fluctuating"

        elif difference >= 5:

            trend_type = "improving"

        elif difference <= -5:

            trend_type = "declining"

        else:

            trend_type = "stable"

        metric = metric_name.lower()

        if trend_type == "improving":

            if metric == "sleep":

                return (
                    "Your sleep duration has been trending "
                    "upward recently. Your recent check-ins "
                    "show more sleep than earlier in your history."
                )

            if metric == "productivity":

                return (
                    "Your productivity has been improving recently. "
                    "Your recent scores are stronger than earlier "
                    "in your check-in history."
                )

            if metric == "recovery":

                return (
                    "Your recovery has been improving recently. "
                    "Your recent scores are stronger than earlier "
                    "in your check-in history."
                )

            if metric == "flowstate":

                return (
                    "Your FlowState has been improving recently. "
                    "Your recent scores suggest stronger overall "
                    "performance than earlier in your history."
                )

        if trend_type == "declining":

            if metric == "sleep":

                return (
                    "Your sleep duration has been trending "
                    "downward recently. Your recent check-ins "
                    "show less sleep than earlier in your history."
                )

            if metric == "productivity":

                return (
                    "Your productivity has been declining recently. "
                    "Your recent scores are lower than earlier "
                    "in your check-in history."
                )

            if metric == "recovery":

                return (
                    "Your recovery has been declining recently. "
                    "Your recent scores are lower than earlier "
                    "in your check-in history."
                )

            if metric == "flowstate":

                return (
                    "Your FlowState has been declining recently. "
                    "Your recent scores suggest weaker overall "
                    "performance than earlier in your history."
                )

        if trend_type == "fluctuating":

            if metric == "sleep":

                return (
                    "Your sleep has been fluctuating recently. "
                    "Your check-ins show noticeable changes in "
                    "sleep duration from day to day."
                )

            if metric == "productivity":

                return (
                    "Your productivity has been fluctuating recently. "
                    "Your check-ins show noticeable ups and downs "
                    "rather than a consistent direction."
                )

            if metric == "recovery":

                return (
                    "Your recovery has been fluctuating recently. "
                    "Your check-ins show noticeable ups and downs "
                    "rather than a consistent direction."
                )

            if metric == "flowstate":

                return (
                    "Your FlowState has been fluctuating recently. "
                    "Your check-ins show noticeable ups and downs "
                    "rather than a consistent direction."
                )

        if metric == "sleep":

            return (
                "Your sleep duration has remained fairly stable. "
                "Your recent check-ins show only small changes "
                "over time."
            )

        if metric == "productivity":

            return (
                "Your productivity has remained fairly stable. "
                "Your recent check-ins show no major shift "
                "in either direction."
            )

        if metric == "recovery":

            return (
                "Your recovery has remained fairly stable. "
                "Your recent check-ins show no major shift "
                "in either direction."
            )

        if metric == "flowstate":

            return (
                "Your FlowState has remained fairly stable. "
                "Your recent check-ins show no major shift "
                "in either direction."
            )

        return (
            f"Your {metric_name} has remained fairly stable "
            "across your recent check-ins."
        )

    # =====================================================
    # Trend Interpretations
    # =====================================================

    @property
    def trend_interpretations(self) -> dict:
        """
        User-facing interpretations for the four
        Analytics trend charts.
        """

        return {

            "flowstate":
                self._trend_interpretation(
                    self._get_history(
                        "flowstate_index"
                    ),
                    "FlowState",
                ),

            "productivity":
                self._trend_interpretation(
                    self._get_history(
                        "productivity_score"
                    ),
                    "Productivity",
                ),

            "recovery":
                self._trend_interpretation(
                    self._get_history(
                        "recovery_score"
                    ),
                    "Recovery",
                ),

            "sleep":
                self._trend_interpretation(
                    self._get_history(
                        "sleep_hours"
                    ),
                    "Sleep",
                    unit="hours",
                ),
        }

    # =====================================================
    # All Charts
    # =====================================================

    @property
    def charts(self) -> dict:
        """
        Generate or retrieve all Analytics chart paths.

        The dictionary itself is cached for the lifetime
        of this ReportService instance.
        """

        if self._charts_cache is not None:

            return self._charts_cache

        self._charts_cache = {

            "flowstate":
                self.flowstate_chart,

            "productivity":
                self.productivity_chart,

            "recovery":
                self.recovery_chart,

            "sleep":
                self.sleep_chart,

            "performance_comparison":
                self.performance_comparison_chart,

            "correlation":
                self.correlation_heatmap,

            "interpretations":
                self.trend_interpretations,
        }

        return self._charts_cache

    # =====================================================
    # Correlation Heatmap
    # =====================================================

    @property
    def correlation_heatmap(self) -> str:
        """
        Generate a compact, user-friendly correlation
        heatmap using meaningful metrics only.

        The heatmap is regenerated only when the selected
        analytics data changes.
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

        metric_columns = {
            "sleep_hours": "Sleep",
            "focus_hours": "Focus",
            "energy": "Energy",
            "stress": "Stress",
            "water_intake": "Water",
            "exercise_minutes": "Exercise",
            "productivity_score": "Productivity",
            "recovery_score": "Recovery",
            "flowstate_index": "FlowState",
        }

        available_columns = [
            column
            for column in metric_columns
            if column in dataframe.columns
        ]

        if len(available_columns) < 2:

            return ""

        selected = dataframe[
            available_columns
        ].copy()

        selected = selected.rename(
            columns={
                column:
                    metric_columns[column]
                for column in available_columns
            }
        )

        # Convert the selected data into a deterministic
        # representation for cache detection.
        cache_data = (
            selected.to_dict(
                orient="list"
            )
        )

        filename = self._chart_cache_name(
            "correlation_heatmap",
            cache_data,
        )

        path, static_path = (
            self._cached_chart_path(
                filename
            )
        )

        if path.exists():

            return static_path

        correlation = (
            selected.corr()
        )

        figure, axis = plt.subplots(
            figsize=(7, 5.5)
        )

        sns.heatmap(
            correlation,
            cmap="RdYlBu_r",
            vmin=-1,
            vmax=1,
            center=0,
            annot=False,
            linewidths=0.8,
            linecolor="white",
            square=True,
            cbar_kws={
                "label":
                    "Relationship strength"
            },
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
            rotation=35,
            labelsize=9,
        )

        axis.tick_params(
            axis="y",
            rotation=0,
            labelsize=9,
        )

        figure.tight_layout()

        figure.savefig(
            path,
            dpi=120,
            bbox_inches="tight",
        )

        plt.close(
            figure
        )

        return static_path

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
            Path(current_app.root_path)
            / "static"
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
            Path(current_app.root_path)
            / "static"
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
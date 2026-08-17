from flask import Blueprint, render_template

from flask_login import (
    login_required,
    current_user
)

from app.services.analytics_service import AnalyticsService
from app.services.insights_service import InsightsService
from app.services.prediction_service import PredictionService
from app.services.report_service import ReportService
from app.services.trend_service import TrendService


main_bp = Blueprint(
    "main",
    __name__
)


@main_bp.route("/")
def home():

    return render_template(
        "home.html"
    )


@main_bp.route("/dashboard")
@login_required
def dashboard():

    analytics = AnalyticsService(
        current_user.id
    )

    trends = TrendService(
        current_user.id
    )

    
    recovery_chart = trends.chart_data(
        "recovery_score"
    )

    productivity_chart = trends.chart_data(
        "productivity_score"
    )

    flowstate_chart = trends.chart_data(
        "flowstate_index"
    )

    return render_template(
        "dashboard/index.html",

        analytics=analytics,

        trends=trends,

        recovery_chart=recovery_chart,

        productivity_chart=productivity_chart,

        flowstate_chart=flowstate_chart
    )

@main_bp.route("/analytics")
@login_required
def analytics():

    analytics = AnalyticsService(
        current_user.id
    )

    trends = TrendService(
        current_user.id
    )

    insights = InsightsService(
        current_user.id
    )

    predictions = PredictionService(
        current_user.id
    )

    prediction = predictions.prediction_summary

    report = ReportService(
        current_user.id
    )

    return render_template(
        "analytics/index.html",

        analytics=analytics,

        trends=trends,

        insights=insights.insights,

        prediction=prediction,

        report=report
    )
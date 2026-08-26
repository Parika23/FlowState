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

from flask import (
    Blueprint,
    render_template,
    send_file
)

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

    return render_template(
        "dashboard/index.html",
        analytics=analytics
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

@main_bp.route("/analytics/export/csv")
@login_required
def export_csv():

    report = ReportService(
        current_user.id
    )

    file_path = report.export_csv()

    return send_file(
        file_path,
        as_attachment=True,
        download_name="flowstate_analytics.csv",
        mimetype="text/csv"
    )


@main_bp.route("/analytics/export/excel")
@login_required
def export_excel():

    report = ReportService(
        current_user.id
    )

    file_path = report.export_excel()

    return send_file(
        file_path,
        as_attachment=True,
        download_name="flowstate_analytics.xlsx",
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )
from flask import (
    Blueprint,
    render_template,
    send_file
)

from flask_login import (
    login_required,
    current_user
)

from app.services.analytics_service import AnalyticsService
from app.services.insights_service import InsightsService
from app.services.prediction_service import PredictionService
from app.services.report_service import ReportService
from app.services.ai_insight_service import AIInsightService


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

    report = ReportService(
        current_user.id
    )

    return render_template(
        "dashboard/index.html",

        analytics=analytics,

        report=report
    )


@main_bp.route("/analytics")
@login_required
def analytics():

    analytics = AnalyticsService(
        current_user.id
    )

    checkins = analytics.total_checkins

    # -------------------------------------------------
    # Empty-data state
    # -------------------------------------------------

    if checkins == 0:

        return render_template(
            "analytics/index.html",
            analytics=analytics,
            insights=[],
            prediction={
                "flowstate_index": None,
                "productivity_score": None,
                "recovery_score": None,
                "performance_label": "Not Enough Data",
            },
            report=None,
            ai_insight=None,
            has_data=False,
        )

    # -------------------------------------------------
    # Rule-based insights are valid from the first
    # check-in because they describe the actual data.
    # -------------------------------------------------

    insights = InsightsService(
        current_user.id
    )

    # -------------------------------------------------
    # ML prediction requires 5 training pairs,
    # which means at least 6 check-ins.
    # -------------------------------------------------

    if checkins >= 6:

        predictions = PredictionService(
            current_user.id
        )

        prediction = predictions.prediction_summary

    else:

        prediction = {
            "flowstate_index": None,
            "productivity_score": None,
            "recovery_score": None,
            "performance_label": "Not Enough Data",
        }

    # -------------------------------------------------
    # Trend/report charts require at least 2
    # observations to show a meaningful change.
    # -------------------------------------------------

    if checkins >= 2:

        report = ReportService(
            current_user.id
        )

    else:

        report = None

    # -------------------------------------------------
    # AI insight requires a small history rather than
    # interpreting a single check-in as a pattern.
    # -------------------------------------------------

    ai_insight = None

    if checkins >= 3:

        ai_service = AIInsightService()

        recent_data = (
            analytics.dataframe
            .tail(14)
            .to_dict(orient="records")
        )

        ai_insight = ai_service.generate_insight(
            recent_data
        )

    return render_template(
        "analytics/index.html",

        analytics=analytics,

        insights=insights.insights,

        prediction=prediction,

        report=report,

        ai_insight=ai_insight,

        has_data=True,
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

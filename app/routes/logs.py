from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from app.extensions import db
from app.models import DailyLog
from app.forms.daily_log_forms import DailyLogForm


logs_bp = Blueprint(
    "logs",
    __name__,
    url_prefix="/logs"
)


@logs_bp.route("/")
@login_required
def index():

    logs = (
        DailyLog.query
        .filter_by(user_id=current_user.id)
        .order_by(DailyLog.log_date.desc())
        .all()
    )

    return render_template(
        "logs/index.html",
        logs=logs
    )


@logs_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_log():

    form = DailyLogForm()

    if form.validate_on_submit():

        # Prevent duplicate logs for the same day
        existing_log = DailyLog.query.filter_by(
            user_id=current_user.id,
            log_date=form.log_date.data
        ).first()

        if existing_log:

            flash(
                "You've already completed your Flow Check-In for this date.",
                "warning"
            )

            return redirect(
                url_for("logs.index")
            )

        # Convert RadioField response to Boolean
        entered_flow_state = (
            form.flow_state.data == "yes"
        )

        log = DailyLog(

            user_id=current_user.id,

            log_date=form.log_date.data,

            sleep_hours=form.sleep_hours.data,

            recreational_screen_time=form.recreational_screen_time.data,

            focus_hours=form.focus_hours.data,

            planned_tasks=form.planned_tasks.data,

            completed_tasks=form.completed_tasks.data,

            energy=form.energy.data,

            mood=form.mood.data,

            stress=form.stress.data,

            exercise_minutes=form.exercise_minutes.data,

            water_intake=form.water_intake.data,

            flow_state=form.flow_state.data,

            notes=form.notes.data.strip()
            if form.notes.data else None

        )

        db.session.add(log)
        db.session.commit()

        flash(
            "🎉 Today's Flow Check-In has been saved successfully!",
            "success"
        )

        return redirect(
            url_for("logs.index")
        )

    return render_template(
        "logs/create.html",
        form=form
    )
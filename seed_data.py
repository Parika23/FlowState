import random
from datetime import datetime, timedelta

from app import create_app
from app.extensions import db
from app.models.daily_log import DailyLog
from app.models.user import User

app = create_app()

with app.app_context():

    user = User.query.first()

    if not user:
        print("No users found.")
        raise SystemExit

    # ---------------------------------------
    # Delete old logs
    # ---------------------------------------

    DailyLog.query.filter_by(
        user_id=user.id
    ).delete()

    db.session.commit()

    # ---------------------------------------
    # Generate 30 days of sample data
    # ---------------------------------------

    start_date = (
        datetime.today().date()
        - timedelta(days=29)
    )

    for i in range(30):

        current_date = start_date + timedelta(days=i)

        sleep = round(
            random.uniform(5.5, 8.5),
            1
        )

        screen = round(
            random.uniform(1.5, 6.5),
            1
        )

        focus = round(
            random.uniform(2.0, 8.0),
            1
        )

        planned = random.randint(5, 10)

        completed = random.randint(
            3,
            planned
        )

        energy = random.randint(4, 10)

        mood = random.randint(4, 10)

        stress = random.randint(2, 9)

        exercise = random.randint(0, 90)

        water = round(
            random.uniform(1.8, 4.5),
            1
        )

        # 0 = No flow
        # 1 = Partial flow
        # 2 = Full flow
        flow = random.choices(
            [0, 1, 2],
            weights=[0.30, 0.45, 0.25],
            k=1
        )[0]

        log = DailyLog(
            user_id=user.id,
            log_date=current_date,
            sleep_hours=sleep,
            recreational_screen_time=screen,
            focus_hours=focus,
            planned_tasks=planned,
            completed_tasks=completed,
            energy=energy,
            mood=mood,
            stress=stress,
            exercise_minutes=exercise,
            water_intake=water,
            flow_state=flow,
            notes="Generated sample data"
        )

        db.session.add(log)

    db.session.commit()

    print(
        "✅ Seed complete! 30 logs inserted."
    )  
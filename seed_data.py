import random
from datetime import datetime, timedelta

from app import create_app
from app.extensions import db
from app.models.daily_log import DailyLog
from app.models.user import User


app = create_app()


# ============================================================
# DEMO USER CONFIGURATION
# ============================================================

DEMO_USERS = [
    {
        "username": "flow_explorer",
        "email": "flow.explorer@demo.com",
        "password": "FlowStateDemo123!",
        "profile": "balanced",
    },
    {
        "username": "deep_focus",
        "email": "deep.focus@demo.com",
        "password": "FlowStateDemo123!",
        "profile": "focused",
    },
    {
        "username": "recovery_first",
        "email": "recovery.first@demo.com",
        "password": "FlowStateDemo123!",
        "profile": "recovery",
    },
    {
        "username": "struggling_week",
        "email": "struggling.week@demo.com",
        "password": "FlowStateDemo123!",
        "profile": "struggling",
    },
]


# ============================================================
# VALUE GENERATION
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def generate_profile_data(profile, day_index):
    """
    Generate realistic daily metrics for different
    productivity profiles.
    """

    # --------------------------------------------------------
    # Balanced
    # --------------------------------------------------------

    if profile == "balanced":

        sleep = random.uniform(6.5, 8.0)
        screen = random.uniform(2.0, 4.5)
        focus = random.uniform(3.0, 6.0)

        energy = random.randint(6, 9)
        mood = random.randint(6, 9)
        stress = random.randint(3, 6)

        exercise = random.randint(20, 60)
        water = random.uniform(2.0, 3.2)

        flow_weights = [0.20, 0.50, 0.30]


    # --------------------------------------------------------
    # High Focus
    # --------------------------------------------------------

    elif profile == "focused":

        sleep = random.uniform(6.8, 8.2)
        screen = random.uniform(1.0, 3.0)
        focus = random.uniform(5.0, 8.5)

        energy = random.randint(7, 10)
        mood = random.randint(7, 10)
        stress = random.randint(2, 6)

        exercise = random.randint(20, 75)
        water = random.uniform(2.2, 3.8)

        flow_weights = [0.10, 0.35, 0.55]


    # --------------------------------------------------------
    # Recovery First
    # --------------------------------------------------------

    elif profile == "recovery":

        sleep = random.uniform(7.2, 9.0)
        screen = random.uniform(1.5, 4.0)
        focus = random.uniform(3.0, 6.5)

        energy = random.randint(7, 10)
        mood = random.randint(7, 10)
        stress = random.randint(1, 5)

        exercise = random.randint(30, 90)
        water = random.uniform(2.5, 4.0)

        flow_weights = [0.15, 0.40, 0.45]


    # --------------------------------------------------------
    # Struggling
    # --------------------------------------------------------

    else:

        sleep = random.uniform(5.0, 6.8)
        screen = random.uniform(4.0, 7.5)
        focus = random.uniform(1.5, 4.0)

        energy = random.randint(3, 7)
        mood = random.randint(3, 7)
        stress = random.randint(5, 9)

        exercise = random.randint(0, 35)
        water = random.uniform(1.2, 2.5)

        flow_weights = [0.50, 0.40, 0.10]


    # --------------------------------------------------------
    # Tasks
    # --------------------------------------------------------

    planned = random.randint(5, 10)

    completion_bias = (
        focus / 10
        + energy / 20
        - stress / 30
    )

    completion_probability = clamp(
        0.35 + completion_bias,
        0.25,
        0.95
    )

    completed = sum(
        random.random() < completion_probability
        for _ in range(planned)
    )

    completed = max(
        1,
        min(completed, planned)
    )


    # --------------------------------------------------------
    # Flow State
    # --------------------------------------------------------

    flow = random.choices(
        [0, 1, 2],
        weights=flow_weights,
        k=1
    )[0]


    return {
        "sleep_hours": round(sleep, 1),
        "recreational_screen_time": round(screen, 1),
        "focus_hours": round(focus, 1),
        "planned_tasks": planned,
        "completed_tasks": completed,
        "energy": energy,
        "mood": mood,
        "stress": stress,
        "exercise_minutes": exercise,
        "water_intake": round(water, 1),
        "flow_state": flow,
    }


# ============================================================
# SEED DATABASE
# ============================================================

with app.app_context():

    print("\n========================================")
    print(" FlowState Demo Data Seeder")
    print("========================================\n")


    # --------------------------------------------------------
    # Create / find demo users
    # --------------------------------------------------------

    users = []

    for demo in DEMO_USERS:

        user = User.query.filter_by(
            email=demo["email"]
        ).first()


        if not user:

            user = User(
                username=demo["username"],
                email=demo["email"],
            )

            user.set_password(
                demo["password"]
            )

            db.session.add(user)

            db.session.flush()

            print(
                f"Created demo user: "
                f"{demo['username']} "
                f"(ID: {user.id})"
            )

        else:

            print(
                f"Found demo user: "
                f"{demo['username']} "
                f"(ID: {user.id})"
            )


        users.append(
            (
                user,
                demo["profile"]
            )
        )


    db.session.commit()


    # --------------------------------------------------------
    # Generate 30 days for each demo user
    # --------------------------------------------------------

    start_date = (
        datetime.today().date()
        - timedelta(days=29)
    )


    for user, profile in users:

        # Remove previous demo logs
        DailyLog.query.filter_by(
            user_id=user.id
        ).delete(
            synchronize_session=False
        )


        for day_index in range(30):

            current_date = (
                start_date
                + timedelta(days=day_index)
            )


            data = generate_profile_data(
                profile,
                day_index
            )


            log = DailyLog(
                user_id=user.id,
                log_date=current_date,

                sleep_hours=data["sleep_hours"],

                recreational_screen_time=(
                    data["recreational_screen_time"]
                ),

                focus_hours=data["focus_hours"],

                planned_tasks=data["planned_tasks"],

                completed_tasks=data["completed_tasks"],

                energy=data["energy"],

                mood=data["mood"],

                stress=data["stress"],

                exercise_minutes=(
                    data["exercise_minutes"]
                ),

                water_intake=data["water_intake"],

                flow_state=data["flow_state"],

                notes=(
                    f"Demo profile: {profile}. "
                    f"Generated sample data."
                )
            )


            db.session.add(log)


        print(
            f"Generated 30 logs for "
            f"{user.username}"
        )


    db.session.commit()


    print("\n========================================")
    print(" Seed complete!")
    print(" 4 demo users")
    print(" 30 days per user")
    print(" 120 daily logs total")
    print("========================================\n")


    print("Demo accounts:\n")

    for demo in DEMO_USERS:

        print(
            f"Username: {demo['username']}"
        )

        print(
            f"Email:    {demo['email']}"
        )

        print(
            f"Password: {demo['password']}"
        )

        print() 
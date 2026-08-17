from datetime import date

from flask_wtf import FlaskForm

from wtforms import (
    DateField,
    FloatField,
    IntegerField,
    RadioField,
    TextAreaField,
    SubmitField,
    SelectField
)

from wtforms.validators import (
    DataRequired,
    NumberRange,
    Optional,
    ValidationError
)


class DailyLogForm(FlaskForm):

    log_date = DateField(
        "Log Date",
        validators=[DataRequired()]
    )

    sleep_hours = FloatField(
        "Sleep Duration (Hours)",
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                max=24,
                message="Sleep duration must be between 0 and 24 hours."
            )
        ]
    )

    recreational_screen_time = FloatField(
        "Recreational Screen Time (Hours)",
        description="Exclude studying, work, coding and productive screen time.",
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                max=24,
                message="Recreational screen time must be between 0 and 24 hours."
            )
        ]
    )

    focus_hours = FloatField(
        "Deep Focus Hours",
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                max=16,
                message="Deep focus hours should be between 0 and 16 hours."
            )
        ]
    )

    planned_tasks = IntegerField(
        "How many tasks did you plan today?",
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                message="Planned tasks cannot be negative."
            )
        ]
    )

    completed_tasks = IntegerField(
        "How many of those tasks did you complete?",
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                message="Completed tasks cannot be negative."
            )
        ]
    )

    energy = SelectField(
        "Energy Level",
        coerce=int,
        choices=[
            (1, "1 - Completely Drained"),
            (2, "2 - Very Low"),
            (3, "3 - Low"),
            (4, "4 - Slightly Low"),
            (5, "5 - Average"),
            (6, "6 - Fairly Good"),
            (7, "7 - Good"),
            (8, "8 - Very Good"),
            (9, "9 - Excellent"),
            (10, "10 - Peak Energy")
        ],
        validators=[DataRequired()]
    )

    mood = SelectField(
        "Mood",
        coerce=int,
        choices=[
            (1, "1 - Very Poor"),
            (2, "2 - Poor"),
            (3, "3 - Low"),
            (4, "4 - Below Average"),
            (5, "5 - Neutral"),
            (6, "6 - Fair"),
            (7, "7 - Good"),
            (8, "8 - Very Good"),
            (9, "9 - Great"),
            (10, "10 - Amazing")
        ],
        validators=[DataRequired()]
    )

    stress = SelectField(
        "Stress Level",
        coerce=int,
        choices=[
            (1, "1 - Completely Relaxed"),
            (2, "2 - Very Low"),
            (3, "3 - Low"),
            (4, "4 - Mild"),
            (5, "5 - Moderate"),
            (6, "6 - Slightly High"),
            (7, "7 - High"),
            (8, "8 - Very High"),
            (9, "9 - Extremely High"),
            (10, "10 - Overwhelming")
        ],
        validators=[DataRequired()]
    )

    exercise_minutes = IntegerField(
        "Exercise Duration (Minutes)",
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                max=300,
                message="Exercise duration must be between 0 and 300 minutes."
            )
        ]
    )

    water_intake = FloatField(
        "Water Intake (Litres)",
        validators=[
            DataRequired(),
            NumberRange(
                min=0,
                max=15,
                message="Water intake must be between 0 and 15 litres."
            )
        ]
    )

    flow_state = RadioField(
    "🌊 Did you tap into your Flow State today?",
    choices=[
        (2, "Yes — I was completely in the zone"),
        (1, "Partially — I had moments of deep focus"),
        (0, "No — I never quite reached it")
    ],
    coerce=int,
    default=None,
    validators=[DataRequired(message="Please select your Flow State for today.")]
    )

    notes = TextAreaField(
        "Daily Reflection / Notes",
        validators=[Optional()]
    )

    submit = SubmitField(
        "Complete Today's Check-In"
    )

    # ------------------------
    # Custom Validations
    # ------------------------

    def validate_log_date(self, field):

        if field.data > date.today():
            raise ValidationError(
                "Log date cannot be in the future."
            )

    def validate_completed_tasks(self, field):

        if (
            self.planned_tasks.data is not None
            and field.data is not None
            and field.data > self.planned_tasks.data
        ):
            raise ValidationError(
                "Completed tasks cannot exceed planned tasks."
            )

    def validate_focus_hours(self, field):

        if (
            self.sleep_hours.data is not None
            and self.recreational_screen_time.data is not None
            and field.data is not None
        ):

            total_hours = (
                self.sleep_hours.data
                + field.data
                + self.recreational_screen_time.data
            )

            if total_hours > 24:

                raise ValidationError(
                    "Sleep, deep focus and recreational screen time together cannot exceed 24 hours."
                )
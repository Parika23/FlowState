"""
FlowState Analytics V2

Next-day performance prediction using
supervised machine learning.

The model learns relationships between
today's behavioral data and tomorrow's
performance scores.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

from app.models import DailyLog
from app.services.analytics_dataframe import AnalyticsDataFrame


class PredictionService:
    """
    Generate next-day performance predictions.

    This service uses supervised machine learning.

    Today's behavioral features are used to predict
    the corresponding performance metric for the
    following day.
    """

    # =====================================================
    # Model Features
    # =====================================================

    FEATURE_COLUMNS = [
        "sleep_hours",
        "focus_hours",
        "energy",
        "mood",
        "stress",
        "water_intake",
        "exercise_minutes",
        "recreational_screen_time",
        "planned_tasks",
        "completed_tasks",
        "completion_rate",
    ]

    TARGET_COLUMNS = [
        "flowstate_index",
        "productivity_score",
        "recovery_score",
    ]

    # =====================================================
    # Initialization
    # =====================================================

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

        self.df = (
            self.analytics.dataframe
            .copy()
        )

        if "log_date" in self.df.columns:

            self.df["log_date"] = pd.to_datetime(
                self.df["log_date"]
            )

            self.df = (
                self.df
                .sort_values("log_date")
                .reset_index(drop=True)
            )

    # =====================================================
    # Data Preparation
    # =====================================================

    def _prepare_training_data(
        self,
        target: str,
    ):
        """
        Build supervised learning data.

        Today's behavioral features become X.

        Tomorrow's target score becomes y.
        """

        if target not in self.df.columns:
            return None, None

        available_features = [
            column
            for column in self.FEATURE_COLUMNS
            if column in self.df.columns
        ]

        if not available_features:
            return None, None

        data = self.df[
            available_features + [target]
        ].copy()

        # -------------------------------------------------
        # Today's data -> Tomorrow's target
        # -------------------------------------------------

        data["target_next_day"] = (
            data[target].shift(-1)
        )

        data = data.dropna(
            subset=available_features + [
                "target_next_day"
            ]
        )

        if len(data) < 5:
            return None, None

        X = data[
            available_features
        ]

        y = data[
            "target_next_day"
        ]

        return X, y

    # =====================================================
    # Model Training
    # =====================================================

    def _train_model(
        self,
        target: str,
    ):
        """
        Train a Linear Regression model.
        """

        X, y = self._prepare_training_data(
            target
        )

        if X is None or y is None:
            return None

        model = LinearRegression()

        model.fit(
            X,
            y
        )

        return model

    # =====================================================
    # Model Evaluation
    # =====================================================

    def _evaluate_model(
        self,
        target: str,
    ) -> dict:

        X, y = self._prepare_training_data(
            target
        )

        if X is None or y is None:
            return {
                "mae": None,
                "r2": None,
            }

        if len(X) < 5:
            return {
                "mae": None,
                "r2": None,
            }

        # -------------------------------------------------
        # Chronological train/test split
        # -------------------------------------------------

        split_index = int(
            len(X) * 0.8
        )

        if (
            split_index <= 0
            or split_index >= len(X)
        ):
            return {
                "mae": None,
                "r2": None,
            }

        X_train = X.iloc[
            :split_index
        ]

        X_test = X.iloc[
            split_index:
        ]

        y_train = y.iloc[
            :split_index
        ]

        y_test = y.iloc[
            split_index:
        ]

        model = LinearRegression()

        model.fit(
            X_train,
            y_train
        )

        predictions = model.predict(
            X_test
        )

        mae = mean_absolute_error(
            y_test,
            predictions
        )

        r2 = None

        if len(y_test) >= 2:

            r2 = r2_score(
                y_test,
                predictions
            )

        return {
            "mae": round(
                float(mae),
                2
            ),

            "r2": (
                round(
                    float(r2),
                    2
                )
                if r2 is not None
                else None
            ),
        }

    # =====================================================
    # Next-Day Prediction
    # =====================================================

    def predict_next_day(
        self,
        target: str,
    ) -> float | None:
        """
        Predict tomorrow's target score.

        The prediction uses the latest available
        behavioral observation.
        """

        if self.df.empty:
            return None

        model = self._train_model(
            target
        )

        if model is None:
            return None

        available_features = [
            column
            for column in self.FEATURE_COLUMNS
            if column in self.df.columns
        ]

        if not available_features:
            return None

        latest = (
            self.df[
                available_features
            ]
            .iloc[-1:]
        )

        if latest.empty:
            return None

        prediction = model.predict(
            latest
        )[0]

        prediction = np.clip(
            prediction,
            0,
            100
        )

        return round(
            float(prediction),
            2
        )

    # =====================================================
    # Individual Predictions
    # =====================================================

    @property
    def predicted_flowstate_index(
        self,
    ) -> float | None:

        return self.predict_next_day(
            "flowstate_index"
        )

    @property
    def predicted_productivity_score(
        self,
    ) -> float | None:

        return self.predict_next_day(
            "productivity_score"
        )

    @property
    def predicted_recovery_score(
        self,
    ) -> float | None:

        return self.predict_next_day(
            "recovery_score"
        )

    # =====================================================
    # Model Evaluation
    # =====================================================

    @property
    def model_evaluation(self) -> dict:
        """
        Return evaluation metrics for the
        primary prediction targets.
        """

        return {
            target: self._evaluate_model(
                target
            )
            for target in self.TARGET_COLUMNS
        }

    # =====================================================
    # Performance Interpretation
    # =====================================================

    @property
    def predicted_performance_label(
        self,
    ) -> str:

        score = (
            self.predicted_flowstate_index
        )

        if score is None:
            return "Not Enough Data"

        if score >= 90:
            return "Exceptional"

        if score >= 75:
            return "Excellent"

        if score >= 60:
            return "Good"

        if score >= 45:
            return "Fair"

        return "Needs Attention"

    # =====================================================
    # Prediction Summary
    # =====================================================

    @property
    def prediction_summary(self) -> dict:
        """
        Complete next-day prediction summary.
        """

        return {

            "flowstate_index":
                self.predicted_flowstate_index,

            "productivity_score":
                self.predicted_productivity_score,

            "recovery_score":
                self.predicted_recovery_score,

            "performance_label":
                self.predicted_performance_label,

        }

    # =====================================================
    # Dashboard Data
    # =====================================================

    @property
    def dashboard_prediction(self) -> dict:
        """
        Human-readable prediction data for
        dashboard rendering.
        """

        return {

            "flowstate":
                self.predicted_flowstate_index,

            "productivity":
                self.predicted_productivity_score,

            "recovery":
                self.predicted_recovery_score,

            "performance":
                self.predicted_performance_label,

        }

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"user_id={self.user_id}, "
            f"rows={len(self.df)})"
        )
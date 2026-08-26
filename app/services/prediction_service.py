"""
FlowState Analytics V2

Next-day performance prediction using
supervised machine learning.

The model learns relationships between
today's behavioral data and tomorrow's
performance scores.
"""

from __future__ import annotations

import hashlib

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
    # Prediction Cache
    # =====================================================

    _cache = {}

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

        # -------------------------------------------------
        # Identify the current version of the user's data.
        # -------------------------------------------------

        fingerprint = self._dataset_fingerprint()

        cached = self._cache.get(
            self.user_id
        )

        if (
            cached is None
            or cached["fingerprint"] != fingerprint
        ):

            self._cache[
                self.user_id
            ] = {
                "fingerprint": fingerprint,
                "models": {},
                "predictions": {},
                "evaluations": {},
            }

    # =====================================================
    # Dataset Fingerprint
    # =====================================================

    def _dataset_fingerprint(self) -> str:
        """
        Create a fingerprint from the current dataset.

        When a new check-in changes the data, the
        fingerprint changes and the cached models
        and predictions are automatically discarded.
        """

        if self.df.empty:
            return "empty"

        try:

            values = (
                pd.util.hash_pandas_object(
                    self.df,
                    index=True,
                )
                .values
                .tobytes()
            )

            return hashlib.sha256(
                values
            ).hexdigest()

        except Exception:

            return hashlib.sha256(
                repr(
                    self.df.to_dict(
                        orient="records"
                    )
                ).encode("utf-8")
            ).hexdigest()

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

        If a model has already been trained for the
        current version of the user's data, reuse it
        instead of training another model.
        """

        cached_models = (
            self._cache[
                self.user_id
            ]["models"]
        )

        if target in cached_models:
            return cached_models[target]

        X, y = self._prepare_training_data(
            target
        )

        if X is None or y is None:

            cached_models[target] = None

            return None

        model = LinearRegression()

        model.fit(
            X,
            y
        )

        cached_models[target] = model

        return model

    # =====================================================
    # Model Evaluation
    # =====================================================

    def _evaluate_model(
        self,
        target: str,
    ) -> dict:

        cached_evaluations = (
            self._cache[
                self.user_id
            ]["evaluations"]
        )

        if target in cached_evaluations:
            return cached_evaluations[target]

        X, y = self._prepare_training_data(
            target
        )

        if X is None or y is None:

            result = {
                "mae": None,
                "r2": None,
            }

            cached_evaluations[
                target
            ] = result

            return result

        if len(X) < 5:

            result = {
                "mae": None,
                "r2": None,
            }

            cached_evaluations[
                target
            ] = result

            return result

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

            result = {
                "mae": None,
                "r2": None,
            }

            cached_evaluations[
                target
            ] = result

            return result

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

        result = {
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

        cached_evaluations[
            target
        ] = result

        return result

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

        Predictions are cached for the current
        version of the user's dataset.
        """

        cached_predictions = (
            self._cache[
                self.user_id
            ]["predictions"]
        )

        if target in cached_predictions:
            return cached_predictions[target]

        if self.df.empty:

            cached_predictions[target] = None

            return None

        model = self._train_model(
            target
        )

        if model is None:

            cached_predictions[target] = None

            return None

        available_features = [
            column
            for column in self.FEATURE_COLUMNS
            if column in self.df.columns
        ]

        if not available_features:

            cached_predictions[target] = None

            return None

        latest = (
            self.df[
                available_features
            ]
            .iloc[-1:]
        )

        if latest.empty:

            cached_predictions[target] = None

            return None

        prediction = model.predict(
            latest
        )[0]

        prediction = np.clip(
            prediction,
            0,
            100
        )

        result = round(
            float(prediction),
            2
        )

        cached_predictions[target] = result

        return result

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
    def model_evaluation(
        self,
    ) -> dict:
        """
        Return evaluation metrics for the
        primary prediction targets.
        """

        return {
            target:
                self._evaluate_model(
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
    def prediction_summary(
        self,
    ) -> dict:
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
    def dashboard_prediction(
        self,
    ) -> dict:
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

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"user_id={self.user_id}, "
            f"rows={len(self.df)})"
        )
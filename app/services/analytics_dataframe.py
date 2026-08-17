"""
analytics_dataframe.py
======================

FlowState Analytics V2

Central data preparation layer for analytics.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.models import DailyLog
from app.services.performance_engine import PerformanceEngine


@dataclass(slots=True)
class DataFrameSummary:
    """
    Summary information for the dataframe.
    """

    rows: int
    columns: int
    missing_values: int
    duplicate_rows: int
    start_date: object | None
    end_date: object | None


class AnalyticsDataFrame:
    """
    Converts DailyLog objects into an
    analytics-ready dataframe.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
    ):

        self._df = dataframe.copy()

        self._prepare()

    @classmethod
    def from_logs(
        cls,
        logs: list[DailyLog],
    ) -> "AnalyticsDataFrame":

        if not logs:
            return cls(
                pd.DataFrame()
            )

        rows = []

        for log in logs:

            engine = PerformanceEngine(log)

            rows.append({

                "log_date":
                    pd.to_datetime(log.log_date),

                "sleep_hours":
                    log.sleep_hours,

                "focus_hours":
                    log.focus_hours,

                "planned_tasks":
                    log.planned_tasks,

                "completed_tasks":
                    log.completed_tasks,

                "energy":
                    log.energy,

                "mood":
                    log.mood,

                "stress":
                    log.stress,

                "exercise_minutes":
                    log.exercise_minutes,

                "water_intake":
                    log.water_intake,

                "recreational_screen_time":
                    log.recreational_screen_time,

                "flow_state":
                    log.flow_state,

                "completion_rate":
                    engine.completion_rate,

                "recovery_score":
                    engine.recovery_score,

                "capacity_score":
                    engine.capacity_score,

                "focus_investment_score":
                    engine.focus_investment_score,

                "execution_score":
                    engine.execution_score,

                "productivity_score":
                    engine.productivity_score,

                "sustainability_score":
                    engine.sustainability_score,

                "flowstate_index":
                    engine.flowstate_index,

                "performance_label":
                    engine.performance_label(
                        engine.flowstate_index
                    ),

                "notes":
                    log.notes,

            })

        dataframe = pd.DataFrame(rows)

    
        return cls(dataframe)

        # ======================================================
    # Preparation Pipeline
    # ======================================================

    def _prepare(self) -> None:
        """
        Execute the dataframe preparation pipeline.
        """

        if self._df.empty:
            return

        self._validate()

        self._clean()

        self._engineer_features()

    # ======================================================
    # Validation
    # ======================================================

    def _validate(self) -> None:
        """
        Validate required dataframe columns.
        """

        required_columns = [

            "log_date",

            "sleep_hours",

            "focus_hours",

            "planned_tasks",

            "completed_tasks",

            "energy",

            "mood",

            "stress",

            "exercise_minutes",

            "water_intake",

            "recreational_screen_time",

            "flow_state",

            "flowstate_index",

        ]

        missing = [

            column

            for column in required_columns

            if column not in self._df.columns

        ]

        if missing:

            raise ValueError(

                f"Missing required columns: {missing}"

            )

    # ======================================================
    # Cleaning
    # ======================================================

    def _clean(self) -> None:
        """
        Clean and normalize the dataframe.
        """

        self._normalize_types()

        self._remove_duplicates()

        self._sort_dataframe()

        self._fill_missing_values()

    def _normalize_types(self) -> None:
        """
        Normalize dataframe column types.
        """

        self._df["log_date"] = pd.to_datetime(
            self._df["log_date"]
        )

        numeric_columns = [

            "sleep_hours",

            "focus_hours",

            "planned_tasks",

            "completed_tasks",

            "energy",

            "mood",

            "stress",

            "exercise_minutes",

            "water_intake",

            "recreational_screen_time",

            "completion_rate",

            "recovery_score",

            "capacity_score",

            "focus_investment_score",

            "execution_score",

            "productivity_score",

            "sustainability_score",

            "flowstate_index",

        ]

        for column in numeric_columns:

            if column in self._df.columns:

                self._df[column] = pd.to_numeric(

                    self._df[column],

                    errors="coerce",

                )

    def _remove_duplicates(self) -> None:
        """
        Remove duplicate dates.
        """

        self._df = (

            self._df

            .drop_duplicates(

                subset="log_date",

                keep="last",

            )

            .reset_index(drop=True)

        )

    def _sort_dataframe(self) -> None:
        """
        Sort by date.
        """

        self._df = (

            self._df

            .sort_values("log_date")

            .reset_index(drop=True)

        )

    def _fill_missing_values(self) -> None:
        """
        Fill missing values.
        """

        numeric_columns = (

            self._df

            .select_dtypes(include=np.number)

            .columns

        )

        for column in numeric_columns:

            median = self._df[column].median()

            if pd.isna(median):

                median = 0

            self._df[column] = (

                self._df[column]

                .fillna(median)

            )

        object_columns = (

            self._df

            .select_dtypes(include="object")

            .columns

        )

        for column in object_columns:

            self._df[column] = (

                self._df[column]

                .fillna("")

            )

        # ======================================================
    # Feature Engineering
    # ======================================================

    def _engineer_features(self) -> None:
        """
        Create analytical features.
        """

        self._create_calendar_features()
        self._create_productivity_features()
        self._create_behavior_features()
        self._create_rolling_features()

    def _create_calendar_features(self) -> None:
        """
        Calendar-based features.
        """

        dates = self._df["log_date"]

        self._df["year"] = dates.dt.year

        self._df["quarter"] = dates.dt.quarter

        self._df["month"] = dates.dt.month

        self._df["month_name"] = dates.dt.month_name()

        self._df["week"] = (
            dates.dt.isocalendar().week.astype(int)
        )

        self._df["day"] = dates.dt.day

        self._df["weekday"] = dates.dt.day_name()

        self._df["is_weekend"] = (
            dates.dt.weekday >= 5
        ).astype(int)

    def _create_productivity_features(self) -> None:
        """
        Productivity-derived features.
        """

        df = self._df

        df["task_gap"] = (
            df["planned_tasks"]
            - df["completed_tasks"]
        )

        df["task_completion_flag"] = (
            df["completion_rate"] >= 100
        ).astype(int)

        df["focus_screen_ratio"] = np.where(
            df["recreational_screen_time"] > 0,
            (
                df["focus_hours"]
                / df["recreational_screen_time"]
            ),
            df["focus_hours"],
        )

        df["focus_per_task"] = np.where(
            df["completed_tasks"] > 0,
            (
                df["focus_hours"]
                / df["completed_tasks"]
            ),
            0,
        )

        df["screen_per_task"] = np.where(
            df["completed_tasks"] > 0,
            (
                df["recreational_screen_time"]
                / df["completed_tasks"]
            ),
            0,
        )

        df["exercise_per_task"] = np.where(
            df["completed_tasks"] > 0,
            (
                df["exercise_minutes"]
                / df["completed_tasks"]
            ),
            0,
        )

    def _create_behavior_features(self) -> None:
        """
        Behaviour indicators.
        """

        df = self._df

        df["sleep_target_met"] = (
            df["sleep_hours"] >= 7
        ).astype(int)

        df["hydration_target_met"] = (
            df["water_intake"] >= 3
        ).astype(int)

        df["exercise_target_met"] = (
            df["exercise_minutes"] >= 45
        ).astype(int)

        df["deep_focus_day"] = (
            df["focus_hours"] >= 4
        ).astype(int)

        df["high_stress_day"] = (
            df["stress"] >= 8
        ).astype(int)

        df["high_energy_day"] = (
            df["energy"] >= 8
        ).astype(int)

        df["good_mood_day"] = (
            df["mood"] >= 8
        ).astype(int)

        df["flow_day"] = (
            df["flow_state"] > 0
        ).astype(int)

    def _create_rolling_features(self) -> None:
        """
        Rolling averages.
        """

        rolling_columns = [

            "flowstate_index",

            "productivity_score",

            "recovery_score",

            "capacity_score",

            "execution_score",

            "focus_investment_score",

            "sleep_hours",

            "focus_hours",

            "completed_tasks",

        ]

        for column in rolling_columns:

            self._df[
                f"{column}_7d_avg"
            ] = (
                self._df[column]
                .rolling(
                    window=7,
                    min_periods=1,
                )
                .mean()
            )

            self._df[
                f"{column}_30d_avg"
            ] = (
                self._df[column]
                .rolling(
                    window=30,
                    min_periods=1,
                )
                .mean()
            )

        # ======================================================
    # Public Data Views
    # ======================================================

    @property
    def dataframe(self) -> pd.DataFrame:
        """
        Return a copy of the dataframe.
        """

        return self._df.copy()

    @property
    def numeric_dataframe(self) -> pd.DataFrame:
        """
        Return numeric columns only.
        """

        return self._df.select_dtypes(
            include=np.number
        )

    @property
    def chart_dataframe(self) -> pd.DataFrame:
        """
        Return chart-ready dataframe.
        """

        columns = [

            "log_date",

            "flowstate_index",

            "recovery_score",

            "capacity_score",

            "execution_score",

            "productivity_score",

            "focus_investment_score",

        ]

        existing = [

            column

            for column in columns

            if column in self._df.columns

        ]

        return self._df.loc[:, existing].copy()

    @property
    def ml_dataframe(self) -> pd.DataFrame:
        """
        Return machine-learning dataframe.
        """

        excluded = [

            "notes",

            "performance_label",

            "month_name",

            "weekday",

        ]

        return (

            self._df

            .drop(
                columns=excluded,
                errors="ignore",
            )

            .select_dtypes(
                include=np.number
            )

        )

    @property
    def correlation_dataframe(self) -> pd.DataFrame:
        """
        Return correlation matrix.
        """

        return (
            self.numeric_dataframe
            .corr()
        )

    # ======================================================
    # Summary
    # ======================================================

    @property
    def summary(self) -> DataFrameSummary:
        """
        Return dataframe summary.
        """

        if self._df.empty:

            return DataFrameSummary(

                rows=0,

                columns=0,

                missing_values=0,

                duplicate_rows=0,

                start_date=None,

                end_date=None,

            )

        return DataFrameSummary(

            rows=len(self._df),

            columns=len(self._df.columns),

            missing_values=int(
                self._df.isna().sum().sum()
            ),

            duplicate_rows=int(
                self._df.duplicated().sum()
            ),

            start_date=self._df["log_date"].min(),

            end_date=self._df["log_date"].max(),

        )

    # ======================================================
    # Simple Properties
    # ======================================================

    @property
    def shape(self) -> tuple[int, int]:

        return self._df.shape

    @property
    def columns(self) -> list[str]:

        return self._df.columns.tolist()

    @property
    def is_empty(self) -> bool:

        return self._df.empty

        # ======================================================
    # Public Helpers
    # ======================================================

    def copy(self) -> "AnalyticsDataFrame":
        """
        Return a deep copy of this analytics dataframe.
        """

        return AnalyticsDataFrame(
            self._df.copy(deep=True)
        )

    def head(
        self,
        n: int = 5,
    ) -> pd.DataFrame:
        """
        Return first n rows.
        """

        return self._df.head(n)

    def tail(
        self,
        n: int = 5,
    ) -> pd.DataFrame:
        """
        Return last n rows.
        """

        return self._df.tail(n)

    def describe(self) -> pd.DataFrame:
        """
        Return descriptive statistics.
        """

        return self.numeric_dataframe.describe()

    def to_dict(self) -> list[dict]:
        """
        Convert dataframe to list of dictionaries.
        """

        return self._df.to_dict(
            orient="records"
        )

    def to_records(self) -> list[dict]:
        """
        Alias for to_dict().
        """

        return self.to_dict()

    # ======================================================
    # Magic Methods
    # ======================================================

    def __len__(self) -> int:
        """
        Number of rows.
        """

        return len(self._df)

    def __repr__(self) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"rows={len(self)}, "
            f"columns={len(self._df.columns)})"
        )        
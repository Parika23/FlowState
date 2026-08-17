"""
FlowState Performance Engine

Converts daily behavioral measurements into
interpretable 0–100 performance metrics.

These are rule-based analytical scores.
Machine learning is handled separately by
PredictionService.
"""

from app.models import DailyLog


class PerformanceEngine:
    """
    Human Performance Engine.

    Score categories:
    - Recovery
    - Capacity
    - Focus Investment
    - Execution
    - Productivity
    - Sustainability
    - FlowState Index
    """

    def __init__(self, log: DailyLog):
        self.log = log

    # =====================================================
    # Generic Helpers
    # =====================================================

    @staticmethod
    def clamp(score):
        """
        Keep a score within the 0–100 range.
        """

        return round(
            max(0, min(score, 100)),
            1
        )

    @staticmethod
    def percentage(value, target):
        """
        Convert a measurement into a percentage
        relative to a target, capped at 100.
        """

        if target <= 0:
            return 0

        return min(
            (value / target) * 100,
            100
        )

    # =====================================================
    # Execution
    # =====================================================

    @property
    def completion_rate(self):
        """
        Percentage of planned tasks completed.

        A completion rate cannot exceed 100%.
        """

        if self.log.planned_tasks <= 0:
            return 0

        return round(
            min(
                (
                    self.log.completed_tasks
                    / self.log.planned_tasks
                ) * 100,
                100
            ),
            1
        )

    # =====================================================
    # Recovery
    # =====================================================

    @property
    def recovery_score(self):
        """
        Measures recovery using:

        Sleep       45%
        Stress      25%
        Exercise    20%
        Hydration   10%
        """

        sleep = self.percentage(
            self.log.sleep_hours,
            8
        )

        stress = (
            (10 - self.log.stress)
            / 9
        ) * 100

        exercise = self.percentage(
            self.log.exercise_minutes,
            45
        )

        water = self.percentage(
            self.log.water_intake,
            3
        )

        return self.clamp(
            sleep * 0.45
            + stress * 0.25
            + exercise * 0.20
            + water * 0.10
        )

    # =====================================================
    # Capacity
    # =====================================================

    @property
    def capacity_score(self):
        """
        Measures current performance capacity.

        Recovery    50%
        Energy      35%
        Mood        15%
        """

        energy = (
            self.log.energy
            / 10
        ) * 100

        mood = (
            self.log.mood
            / 10
        ) * 100

        return self.clamp(
            self.recovery_score * 0.50
            + energy * 0.35
            + mood * 0.15
        )

    # =====================================================
    # Focus Investment
    # =====================================================

    @property
    def focus_investment_score(self):
        """
        Measures how effectively attention is
        directed toward focused work.

        Focus hours       50%
        Flow state        35%
        Screen behavior   15%
        """

        focus = self.percentage(
            self.log.focus_hours,
            6
        )

        flow = {
            0: 0,
            1: 60,
            2: 100
        }.get(
            self.log.flow_state,
            0
        )

        screen_penalty = self.percentage(
            self.log.recreational_screen_time,
            6
        )

        screen_score = (
            100 - screen_penalty
        )

        return self.clamp(
            focus * 0.50
            + flow * 0.35
            + screen_score * 0.15
        )

    # =====================================================
    # Execution Score
    # =====================================================

    @property
    def execution_score(self):
        """
        Measures the ability to turn planned work
        into completed work while maintaining focus.

        Completion rate       70%
        Focus investment     30%
        """

        return self.clamp(
            self.completion_rate * 0.70
            + self.focus_investment_score * 0.30
        )

    # =====================================================
    # Productivity Score
    # =====================================================

    @property
    def productivity_score(self):
        """
        Measures effective output using:

        Execution           65%
        Capacity            20%
        Focus Investment    15%
        """

        return self.clamp(
            self.execution_score * 0.65
            + self.capacity_score * 0.20
            + self.focus_investment_score * 0.15
        )

    # =====================================================
    # Sustainability Score
    # =====================================================

    @property
    def sustainability_score(self):
        """
        Measures whether the user's performance pattern
        appears maintainable.

        Higher scores represent healthier and more
        sustainable behavioral patterns.

        Components:

        Sleep       35%
        Stress      25%
        Exercise    15%
        Hydration   10%
        Focus       15%
        """

        sleep = self.percentage(
            self.log.sleep_hours,
            8
        )

        stress = (
            (10 - self.log.stress)
            / 9
        ) * 100

        exercise = self.percentage(
            self.log.exercise_minutes,
            45
        )

        water = self.percentage(
            self.log.water_intake,
            3
        )

        focus = self.percentage(
            self.log.focus_hours,
            6
        )

        return self.clamp(
            sleep * 0.35
            + stress * 0.25
            + exercise * 0.15
            + water * 0.10
            + focus * 0.15
        )

    # =====================================================
    # FlowState Index
    # =====================================================

    @property
    def flowstate_index(self):
        """
        Overall performance index.

        Recovery          20%
        Capacity          20%
        Focus Investment  20%
        Productivity      25%
        Sustainability    15%
        """

        return self.clamp(
            self.recovery_score * 0.20
            + self.capacity_score * 0.20
            + self.focus_investment_score * 0.20
            + self.productivity_score * 0.25
            + self.sustainability_score * 0.15
        )

    # =====================================================
    # Performance Label
    # =====================================================

    @staticmethod
    def performance_label(score):
        """
        Convert a numerical score into a
        human-readable performance level.
        """

        if score >= 90:
            return "Exceptional"

        if score >= 75:
            return "Excellent"

        if score >= 60:
            return "Good"

        if score >= 45:
            return "Fair"

        return "Needs Attention"
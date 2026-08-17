"""
insights_service.py
===================

FlowState Analytics V2

Generate intelligent, human-readable insights
from analytics data.

This service does not perform calculations.
It interprets metrics provided by
AnalyticsService.
"""

from __future__ import annotations

from app.services.analytics_service import AnalyticsService


class InsightsService:
    """
    Generate personalized insights for the dashboard.
    """

    def __init__(
        self,
        user_id: int,
    ):

        self.analytics = AnalyticsService(
            user_id
        )

    @property
    def insights(self) -> list[dict]:

        insights = []

        if not self.analytics.has_data:
            return insights

        analytics = self.analytics

        # =====================================================
        # Sleep
        # =====================================================

        if analytics.average_sleep >= 8:

            insights.append({

                "category": "Recovery",

                "icon": "😴",

                "title": "Excellent Recovery",

                "message":
                    (
                        f"You're averaging "
                        f"{analytics.average_sleep} hours "
                        f"of sleep. Excellent consistency!"
                    ),

                "status": "success"

            })

        elif analytics.average_sleep >= 7:

            insights.append({

                "category": "Recovery",

                "icon": "🛌",

                "title": "Healthy Sleep",

                "message":
                    (
                        f"Your average sleep is "
                        f"{analytics.average_sleep} hours."
                    ),

                "status": "good"

            })

        else:

            insights.append({

                "category": "Recovery",

                "icon": "⚠️",

                "title": "Sleep Needs Attention",

                "message":
                    (
                        f"Average sleep is only "
                        f"{analytics.average_sleep} hours."
                    ),

                "status": "warning"

            })

        # =====================================================
        # Flow State
        # =====================================================

        if analytics.flow_state_percentage >= 50:

            flow_status = "excellent"

        elif analytics.flow_state_percentage >= 25:

            flow_status = "good"

        else:

            flow_status = "warning"

        insights.append({

            "category": "Flow",

            "icon": "🌊",

            "title": "Flow State",

            "message":
                (
                    f"You reached Full Flow on "
                    f"{analytics.flow_state_percentage}% "
                    f"of logged days."
                ),

            "status": flow_status

        })

        # =====================================================
        # Productivity
        # =====================================================

        productivity = (
            analytics.average_productivity_score
        )

        if productivity >= 80:

            productivity_message = (
                "Outstanding productivity "
                "consistency."
            )

            productivity_status = "success"

        elif productivity >= 60:

            productivity_message = (
                "Productivity is trending "
                "in a healthy direction."
            )

            productivity_status = "good"

        else:

            productivity_message = (
                "There is room to improve "
                "daily execution."
            )

            productivity_status = "warning"

        insights.append({

            "category": "Productivity",

            "icon": "🎯",

            "title": "Productivity",

            "message":
                (
                    f"Average productivity score "
                    f"is {productivity}. "
                    f"{productivity_message}"
                ),

            "status": productivity_status

        })

            # =====================================================
        # Hydration
        # =====================================================

        if analytics.average_water >= 2.5:

            insights.append({

                "category": "Health",

                "icon": "💧",

                "title": "Hydration",

                "message":
                    "Your hydration habits have been consistent.",

                "status": "success"

            })

        else:

            insights.append({

                "category": "Health",

                "icon": "🥤",

                "title": "Hydration",

                "message":
                    (
                        "Average water intake is below the "
                        "recommended level."
                    ),

                "status": "warning"

            })

        # =====================================================
        # Exercise
        # =====================================================

        if analytics.average_exercise >= 45:

            exercise_status = "success"

        elif analytics.average_exercise >= 30:

            exercise_status = "good"

        else:

            exercise_status = "warning"

        insights.append({

            "category": "Fitness",

            "icon": "🏃",

            "title": "Exercise",

            "message":
                (
                    f"Average exercise time is "
                    f"{analytics.average_exercise} minutes."
                ),

            "status": exercise_status

        })

        # =====================================================
        # FlowState Index
        # =====================================================

        flow_index = analytics.average_flowstate_index

        if flow_index >= 80:

            summary = (
                "Your overall performance is excellent."
            )

            status = "success"

        elif flow_index >= 60:

            summary = (
                "You're building consistent habits."
            )

            status = "good"

        else:

            summary = (
                "Focus on recovery and consistency "
                "to improve your FlowState."
            )

            status = "warning"

        insights.append({

            "category": "Overall",

            "icon": "📈",

            "title": "FlowState Index",

            "message":
                (
                    f"Average FlowState Index is "
                    f"{flow_index}. "
                    f"{summary}"
                ),

            "status": status

        })

        return insights

            

        
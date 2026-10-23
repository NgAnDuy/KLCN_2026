"""Orchestrate weekly meal and exercise planning.

Combines the WeeklyMealPlanner and WeeklyExercisePlanner
into a single coordinated weekly plan, ensuring calorie
intake and expenditure are balanced.
"""

from src.weekly_meal_planner import (
    WeeklyMealPlanner
)

from src.weekly_exercise_planner import (
    WeeklyExercisePlanner
)


class WeeklyPlannerEngine:
    """Coordinate meal and exercise weekly plans."""

    def __init__(self):
        self.meal_planner = WeeklyMealPlanner()

        self.exercise_planner = (
            WeeklyExercisePlanner()
        )

    def generate(
        self,
        selected_goal,
        expert_result,
        calculated,
        weight_kg
    ):
        """Generate a combined weekly plan.

        Parameters
        ----------
        selected_goal : str
            The user-selected health goal.
        expert_result : dict
            Output from analyze_goal_conflict.
        calculated : dict
            Calculated features (tdee, bmr, etc.).
        weight_kg : float
            User body weight in kilograms.

        Returns
        -------
        dict
            Combined weekly plan with meal plan,
            exercise plan, and summary statistics.
        """

        # ====================================================
        # 1. GENERATE MEAL PLAN
        # ====================================================

        meal_plan = self.meal_planner.generate(
            selected_goal=selected_goal,
            expert_result=expert_result,
            calculated=calculated
        )

        # ====================================================
        # 2. GENERATE EXERCISE PLAN
        # ====================================================

        exercise_plan = (
            self.exercise_planner.generate(
                selected_goal=selected_goal,
                expert_result=expert_result,
                weight_kg=weight_kg
            )
        )

        # ====================================================
        # 3. BUILD COMBINED DAILY VIEW
        # ====================================================

        combined_days = []

        for index in range(7):
            meal_day = meal_plan["days"][index]
            exercise_day = exercise_plan[
                "days"
            ][index]

            combined = {
                "day": meal_day["day"],
                "meals": meal_day["meals"],
                "meal_total_calories": meal_day[
                    "total_calories"
                ],
                "meal_total_protein": meal_day[
                    "total_protein"
                ],
                "meal_total_carbs": meal_day[
                    "total_carbs"
                ],
                "meal_total_fat": meal_day[
                    "total_fat"
                ],
                "calorie_deviation": meal_day[
                    "calorie_deviation"
                ],
                "is_rest": exercise_day[
                    "is_rest"
                ],
                "exercise": exercise_day.get(
                    "exercise"
                ),
                "exercise_calories": exercise_day[
                    "estimated_calories"
                ],
                "focus": exercise_day.get(
                    "focus",
                    "recovery"
                ),
                "recovery_tips": exercise_day.get(
                    "recovery_tips",
                    []
                )
            }

            combined_days.append(combined)

        # ====================================================
        # 4. BUILD WEEKLY SUMMARY
        # ====================================================

        total_intake = sum(
            day["meal_total_calories"]
            for day in combined_days
        )

        total_burned = exercise_plan[
            "total_calories_burned"
        ]

        avg_daily_intake = round(
            total_intake / 7
        )

        summary = {
            "daily_calorie_target": meal_plan[
                "daily_calories"
            ],
            "avg_daily_intake": avg_daily_intake,
            "total_weekly_intake": round(
                total_intake
            ),
            "total_weekly_burned": total_burned,
            "training_days": exercise_plan[
                "training_days"
            ],
            "rest_days": exercise_plan[
                "rest_days"
            ],
            "split_label": exercise_plan[
                "split_label"
            ],
            "max_intensity": exercise_plan[
                "max_intensity"
            ],
            "macro_targets": meal_plan[
                "macro_targets"
            ],
            "tdee": meal_plan["tdee"],
            "bmr": meal_plan["bmr"]
        }

        # ====================================================
        # 5. HYDRATION RECOMMENDATION
        # ====================================================

        hydration_liters = round(
            weight_kg * 0.033,
            1
        )

        summary[
            "hydration_liters"
        ] = hydration_liters

        return {
            "summary": summary,
            "days": combined_days
        }


def generate_weekly_plan(
    selected_goal,
    expert_result,
    calculated,
    weight_kg
):
    """Convenience function for weekly plan generation."""
    engine = WeeklyPlannerEngine()

    return engine.generate(
        selected_goal=selected_goal,
        expert_result=expert_result,
        calculated=calculated,
        weight_kg=weight_kg
    )

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

EXERCISE_DATA_PATH = (
    BASE_DIR
    / "data"
    / "exercise_dataset.csv"
)


class ExerciseRecommender:
    """Recommend exercises based on current user status."""

    def __init__(self):
        self.exercise_data = pd.read_csv(
            EXERCISE_DATA_PATH
        )

    def recommend(
        self,
        selected_goal,
        expert_result,
        weight_kg,
        top_n=5
    ):
        data = self.exercise_data.copy()

        data["score"] = 0.0
        data["reason"] = ""
        data["estimated_calories"] = 0.0

        for index, exercise in data.iterrows():
            score = 0.0
            reasons = []

            goal_tags = str(
                exercise["goal_tags"]
            ).split(",")

            intensity = str(
                exercise["intensity"]
            )

            difficulty = str(
                exercise["difficulty"]
            )

            impact = str(
                exercise["impact_level"]
            )

            # ----------------------------------------------
            # Goal compatibility
            # ----------------------------------------------

            if selected_goal in goal_tags:
                score += 3

                reasons.append(
                    "Suitable for the selected goal"
                )

            # ----------------------------------------------
            # Current exercise status
            # ----------------------------------------------

            exercise_status = expert_result[
                "exercise_status"
            ]

            if exercise_status in {
                "VERY_LOW",
                "LOW"
            }:
                if difficulty == "beginner":
                    score += 3

                    reasons.append(
                        "Suitable for current fitness level"
                    )

                if intensity == "low":
                    score += 2

                elif intensity == "moderate":
                    score += 1

                if impact == "low":
                    score += 1

            elif exercise_status == "GOOD":
                if difficulty in {
                    "beginner",
                    "intermediate"
                }:
                    score += 2

                if intensity == "moderate":
                    score += 2

            elif exercise_status == "HIGH":
                if difficulty in {
                    "intermediate",
                    "advanced"
                }:
                    score += 2

            # ----------------------------------------------
            # Expert direction safety
            # ----------------------------------------------

            direction = expert_result[
                "direction"
            ]

            if direction in {
                "PROFESSIONAL_REVIEW",
                "MAINTAIN_FIRST"
            }:
                if intensity == "low":
                    score += 4

                    reasons.append(
                        "Conservative intensity based on "
                        "expert direction"
                    )

                elif intensity == "high":
                    score -= 5

                if impact == "low":
                    score += 2

            # ----------------------------------------------
            # Low BMI
            # ----------------------------------------------

            if (
                expert_result["body_status"]
                == "LOW_BMI"
            ):
                if intensity == "high":
                    score -= 4

                if exercise["exercise_type"] in {
                    "recovery",
                    "mobility",
                    "strength",
                    "flexibility"
                }:
                    score += 2

            # ----------------------------------------------
            # Goal-specific preference
            # ----------------------------------------------

            exercise_type = str(
                exercise["exercise_type"]
            )

            if selected_goal == "fitness_improvement":
                if exercise_type in {
                    "strength",
                    "cardio_strength",
                    "strength_cardio"
                }:
                    score += 2

            elif selected_goal == "weight_gain":
                if exercise_type == "strength":
                    score += 3

            elif selected_goal == "weight_loss":
                if exercise_type in {
                    "cardio",
                    "strength",
                    "cardio_strength",
                    "strength_cardio"
                }:
                    score += 2

            elif selected_goal == "healthy_lifestyle":
                if exercise_type in {
                    "cardio",
                    "mobility",
                    "flexibility",
                    "recovery"
                }:
                    score += 2

            # ----------------------------------------------
            # Personalized calorie estimation
            # ----------------------------------------------

            met = float(
                exercise["met"]
            )

            duration = float(
                exercise["duration_min"]
            )

            estimated_calories = (
                met
                * 3.5
                * weight_kg
                / 200
                * duration
            )

            data.at[
                index,
                "estimated_calories"
            ] = round(
                estimated_calories,
                1
            )

            data.at[
                index,
                "score"
            ] = score

            data.at[
                index,
                "reason"
            ] = "; ".join(reasons)

        result = data.sort_values(
            by="score",
            ascending=False
        )

        return result.head(top_n).to_dict(
            orient="records"
        )
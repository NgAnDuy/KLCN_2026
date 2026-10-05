from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

FOOD_DATA_PATH = (
    BASE_DIR
    / "data"
    / "food_dataset.csv"
)


class FoodRecommender:
    """Recommend foods using user status and expert decisions."""

    def __init__(self):
        self.food_data = pd.read_csv(
            FOOD_DATA_PATH
        )

    def recommend(
        self,
        selected_goal,
        expert_result,
        top_n=5
    ):
        data = self.food_data.copy()

        data["score"] = 0.0
        data["reason"] = ""

        for index, food in data.iterrows():
            score = 0.0
            reasons = []

            goal_tags = str(
                food["goal_tags"]
            ).split(",")

            # ----------------------------------------------
            # Goal compatibility
            # ----------------------------------------------

            if selected_goal in goal_tags:
                score += 3

                reasons.append(
                    "Suitable for the selected goal"
                )

            # ----------------------------------------------
            # Expert direction
            # ----------------------------------------------

            direction = expert_result[
                "direction"
            ]

            if direction == "PROFESSIONAL_REVIEW":
                if (
                    food["food_group"]
                    in {
                        "vegetable",
                        "fruit",
                        "protein",
                        "whole_grain",
                        "mixed_meal"
                    }
                ):
                    score += 2

                    reasons.append(
                        "Supports balanced nutrition"
                    )

            # ----------------------------------------------
            # Energy status
            # ----------------------------------------------

            energy_status = expert_result[
                "energy_status"
            ]

            calories = float(
                food["calories"]
            )

            if energy_status == "LARGE_SURPLUS":
                if calories <= 450:
                    score += 2

                    reasons.append(
                        "Moderate energy content"
                    )

            elif energy_status == "MODERATE_SURPLUS":
                if calories <= 500:
                    score += 1.5

            elif energy_status == "LARGE_DEFICIT":
                if calories >= 300:
                    score += 2

                    reasons.append(
                        "Helps support energy intake"
                    )

            elif energy_status == "MODERATE_DEFICIT":
                if calories >= 250:
                    score += 1.5

            # ----------------------------------------------
            # Protein
            # ----------------------------------------------

            protein = float(
                food["protein_g"]
            )

            if protein >= 20:
                score += 2

                reasons.append(
                    "Good protein content"
                )

            elif protein >= 10:
                score += 1

            # ----------------------------------------------
            # Fiber
            # ----------------------------------------------

            fiber = float(
                food["fiber_g"]
            )

            if fiber >= 6:
                score += 2

                reasons.append(
                    "Good fiber content"
                )

            elif fiber >= 3:
                score += 1

            # ----------------------------------------------
            # Sodium
            # ----------------------------------------------

            sodium = float(
                food["sodium_mg"]
            )

            if sodium <= 500:
                score += 0.5

            # ----------------------------------------------
            # Save score
            # ----------------------------------------------

            data.at[index, "score"] = score

            data.at[index, "reason"] = (
                "; ".join(reasons)
            )

        result = data.sort_values(
            by=[
                "score",
                "protein_g",
                "fiber_g"
            ],
            ascending=[
                False,
                False,
                False
            ]
        )

        return result.head(top_n).to_dict(
            orient="records"
        )
from pathlib import Path

import pandas as pd

from src.food_portions import attach_food_portion, load_food_portions
from src.medical_food_screen import screen_food_candidates


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
        top_n=5,
        medical_conditions=(),
        allergies=(),
        return_screening=False,
    ):
        data, screening = screen_food_candidates(
            self.food_data, medical_conditions, allergies
        )

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
                balanced_groups = {
                    "vegetable", "fruit", "whole_grain", "mixed_meal"
                }
                if "kidney_disease" not in medical_conditions:
                    balanced_groups.add("protein")
                if (
                    food["food_group"]
                    in balanced_groups
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

            if "kidney_disease" not in medical_conditions:
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

            sodium = pd.to_numeric(food["sodium_mg"], errors="coerce")

            if pd.notna(sodium) and sodium <= 500:
                score += 0.5

            # ----------------------------------------------
            # Save score
            # ----------------------------------------------

            data.at[index, "score"] = score

            data.at[index, "reason"] = (
                "; ".join(reasons)
            )

        sort_fields = (
            ["score", "fiber_g"]
            if "kidney_disease" in medical_conditions
            else ["score", "protein_g", "fiber_g"]
        )
        result = data.sort_values(
            by=sort_fields,
            ascending=[False] * len(sort_fields),
        )

        selected = result.head(top_n).to_dict(orient="records")
        # Show one documented serving when possible, without changing
        # the existing scoring formula for other foods.
        verified_ids = load_food_portions()
        if top_n > 0 and not any(str(food["food_id"]) in verified_ids for food in selected):
            eligible = result[
                result["food_id"].isin(verified_ids)
                & result["goal_tags"].astype(str).str.split(",").apply(
                    lambda tags: selected_goal in tags
                )
            ]
            if not eligible.empty:
                selected[-1:] = eligible.head(1).to_dict(orient="records")

        foods = [attach_food_portion(food) for food in selected]
        if return_screening:
            return foods, screening
        return foods

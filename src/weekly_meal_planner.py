"""Generate a personalized 7-day meal plan.

Uses expert analysis results to determine daily calorie
targets and macro splits, then composes multi-item meals
from the food dataset with anti-duplication constraints.

Each meal (breakfast, lunch, dinner, snack) is built from
multiple food components so that each item has its own
serving weight in grams.
"""

import random

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

FOOD_DATA_PATH = (
    BASE_DIR
    / "data"
    / "food_dataset.csv"
)

# ============================================================
# CONSTANTS
# ============================================================

DAY_KEYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday"
]

MEAL_SLOTS = [
    "breakfast",
    "lunch",
    "dinner",
    "snack"
]

# Calorie distribution per meal (% of daily target)
MEAL_CALORIE_RATIO = {
    "breakfast": 0.25,
    "lunch": 0.35,
    "dinner": 0.30,
    "snack": 0.10
}

# Macro splits by goal category (protein%, carbs%, fat%)
MACRO_SPLITS = {
    "weight_loss": {
        "protein": 0.30,
        "carbs": 0.40,
        "fat": 0.30
    },
    "weight_gain": {
        "protein": 0.25,
        "carbs": 0.45,
        "fat": 0.30
    },
    "maintenance": {
        "protein": 0.20,
        "carbs": 0.50,
        "fat": 0.30
    },
    "fitness_improvement": {
        "protein": 0.30,
        "carbs": 0.40,
        "fat": 0.30
    },
    "healthy_lifestyle": {
        "protein": 0.20,
        "carbs": 0.50,
        "fat": 0.30
    }
}

# ============================================================
# MEAL COMPOSITION TEMPLATES
# ============================================================
# Each meal slot is composed of multiple food roles.
# Each role defines which food_groups to pick from.

MEAL_COMPOSITION = {
    "breakfast": [
        {
            "role": "main",
            "groups": [
                "whole_grain",
                "carbohydrate",
                "protein"
            ],
            "calorie_share": 0.55
        },
        {
            "role": "side",
            "groups": [
                "fruit",
                "dairy",
                "beverage",
                "seeds"
            ],
            "calorie_share": 0.45
        }
    ],

    "lunch": [
        {
            "role": "protein",
            "groups": [
                "protein"
            ],
            "calorie_share": 0.40
        },
        {
            "role": "carb",
            "groups": [
                "carbohydrate",
                "whole_grain"
            ],
            "calorie_share": 0.35
        },
        {
            "role": "vegetable",
            "groups": [
                "vegetable"
            ],
            "calorie_share": 0.25
        }
    ],

    "dinner": [
        {
            "role": "protein",
            "groups": [
                "protein"
            ],
            "calorie_share": 0.40
        },
        {
            "role": "carb",
            "groups": [
                "carbohydrate",
                "whole_grain"
            ],
            "calorie_share": 0.35
        },
        {
            "role": "vegetable",
            "groups": [
                "vegetable"
            ],
            "calorie_share": 0.25
        }
    ],

    "snack": [
        {
            "role": "snack_item",
            "groups": [
                "fruit",
                "nuts",
                "seeds",
                "dairy",
                "fruit_fat",
                "beverage"
            ],
            "calorie_share": 1.0
        }
    ]
}


def _calculate_daily_calories(
    tdee,
    bmr,
    selected_goal,
    direction
):
    """Calculate the daily calorie target.

    Adjustments are based on the expert system direction
    and the selected health goal.
    """

    # Safety-first directions: keep calories at TDEE
    if direction in {
        "PROFESSIONAL_REVIEW",
        "MAINTAIN_FIRST",
        "REVIEW_GOAL"
    }:
        return round(tdee)

    # Goal-based adjustment
    if selected_goal == "weight_loss":
        target = tdee - 400

        # Never go below BMR
        if target < bmr:
            target = bmr

        return round(target)

    elif selected_goal == "weight_gain":
        target = tdee + 400
        return round(target)

    # maintenance, fitness, healthy lifestyle
    return round(tdee)


def _get_macro_targets(
    daily_calories,
    selected_goal
):
    """Calculate macro nutrient targets in grams."""
    split = MACRO_SPLITS.get(
        selected_goal,
        MACRO_SPLITS["maintenance"]
    )

    protein_cal = (
        daily_calories * split["protein"]
    )
    carbs_cal = (
        daily_calories * split["carbs"]
    )
    fat_cal = (
        daily_calories * split["fat"]
    )

    return {
        "protein_g": round(protein_cal / 4),
        "carbs_g": round(carbs_cal / 4),
        "fat_g": round(fat_cal / 9),
        "protein_pct": round(
            split["protein"] * 100
        ),
        "carbs_pct": round(
            split["carbs"] * 100
        ),
        "fat_pct": round(
            split["fat"] * 100
        )
    }


class WeeklyMealPlanner:
    """Build a 7-day meal plan from the food dataset.

    Each meal is composed of multiple food items
    (protein + carb + vegetable for lunch/dinner),
    each with a specific serving weight in grams.
    """

    def __init__(self):
        self.food_data = pd.read_csv(
            FOOD_DATA_PATH
        )

    def generate(
        self,
        selected_goal,
        expert_result,
        calculated
    ):
        """Generate a complete 7-day meal plan.

        Parameters
        ----------
        selected_goal : str
            The user-selected health goal.
        expert_result : dict
            Output from analyze_goal_conflict.
        calculated : dict
            Calculated features including tdee and bmr.

        Returns
        -------
        dict
            Weekly plan with daily_calories, macros,
            and 7 days of composed meals.
        """
        tdee = float(calculated["tdee"])
        bmr = float(calculated["bmr"])
        direction = expert_result["direction"]

        daily_calories = _calculate_daily_calories(
            tdee=tdee,
            bmr=bmr,
            selected_goal=selected_goal,
            direction=direction
        )

        macro_targets = _get_macro_targets(
            daily_calories,
            selected_goal
        )

        # Track recently used food_ids (cooldown)
        recent_ids = {
            "protein": [],
            "carb": [],
            "general": []
        }

        weekly_plan = []

        for day_index, day_key in enumerate(
            DAY_KEYS
        ):
            day_plan = self._plan_single_day(
                day_key=day_key,
                daily_calories=daily_calories,
                selected_goal=selected_goal,
                expert_result=expert_result,
                recent_ids=recent_ids
            )

            weekly_plan.append(day_plan)

        return {
            "daily_calories": daily_calories,
            "tdee": round(tdee),
            "bmr": round(bmr),
            "macro_targets": macro_targets,
            "days": weekly_plan
        }

    def _plan_single_day(
        self,
        day_key,
        daily_calories,
        selected_goal,
        expert_result,
        recent_ids
    ):
        """Plan all meals for a single day."""
        day_meals = {}
        day_total_calories = 0
        day_total_protein = 0
        day_total_carbs = 0
        day_total_fat = 0
        day_total_serving = 0

        for slot in MEAL_SLOTS:
            slot_budget = round(
                daily_calories
                * MEAL_CALORIE_RATIO[slot]
            )

            meal = self._compose_meal(
                meal_slot=slot,
                calorie_budget=slot_budget,
                selected_goal=selected_goal,
                expert_result=expert_result,
                recent_ids=recent_ids
            )

            day_meals[slot] = meal

            day_total_calories += meal[
                "total_calories"
            ]
            day_total_protein += meal[
                "total_protein"
            ]
            day_total_carbs += meal[
                "total_carbs"
            ]
            day_total_fat += meal[
                "total_fat"
            ]
            day_total_serving += meal[
                "total_serving_g"
            ]

        calorie_deviation = round(
            day_total_calories - daily_calories
        )

        return {
            "day": day_key,
            "meals": day_meals,
            "total_calories": round(
                day_total_calories
            ),
            "total_protein": round(
                day_total_protein
            ),
            "total_carbs": round(
                day_total_carbs
            ),
            "total_fat": round(
                day_total_fat
            ),
            "total_serving_g": round(
                day_total_serving
            ),
            "calorie_deviation": calorie_deviation
        }

    def _compose_meal(
        self,
        meal_slot,
        calorie_budget,
        selected_goal,
        expert_result,
        recent_ids
    ):
        """Compose a meal from multiple food items.

        Each meal slot has a composition template
        defining which food roles to fill.
        """
        composition = MEAL_COMPOSITION[meal_slot]

        items = []
        used_ids_this_meal = []

        for role_spec in composition:
            role_budget = round(
                calorie_budget
                * role_spec["calorie_share"]
            )

            item = self._pick_item(
                meal_slot=meal_slot,
                food_groups=role_spec["groups"],
                calorie_budget=role_budget,
                selected_goal=selected_goal,
                expert_result=expert_result,
                recent_ids=recent_ids,
                exclude_ids=used_ids_this_meal
            )

            if item is not None:
                items.append(item)

                used_ids_this_meal.append(
                    item["food_id"]
                )

                # Track in category cooldown
                role = role_spec["role"]

                if role == "protein":
                    recent_ids["protein"].append(
                        item["food_id"]
                    )

                    if len(
                        recent_ids["protein"]
                    ) > 4:
                        recent_ids[
                            "protein"
                        ].pop(0)

                elif role == "carb":
                    recent_ids["carb"].append(
                        item["food_id"]
                    )

                    if len(
                        recent_ids["carb"]
                    ) > 4:
                        recent_ids[
                            "carb"
                        ].pop(0)

                else:
                    recent_ids[
                        "general"
                    ].append(
                        item["food_id"]
                    )

                    if len(
                        recent_ids["general"]
                    ) > 6:
                        recent_ids[
                            "general"
                        ].pop(0)

        # Calculate meal totals
        total_cal = sum(
            it["calories"] for it in items
        )
        total_protein = sum(
            it["protein_g"] for it in items
        )
        total_carbs = sum(
            it["carbs_g"] for it in items
        )
        total_fat = sum(
            it["fat_g"] for it in items
        )
        total_serving = sum(
            it["serving_g"] for it in items
        )

        return {
            "items": items,
            "total_calories": round(total_cal),
            "total_protein": round(
                total_protein
            ),
            "total_carbs": round(total_carbs),
            "total_fat": round(total_fat),
            "total_serving_g": round(
                total_serving
            )
        }

    def _pick_item(
        self,
        meal_slot,
        food_groups,
        calorie_budget,
        selected_goal,
        expert_result,
        recent_ids,
        exclude_ids
    ):
        """Pick one best food item for a role."""
        data = self.food_data.copy()

        # ------------------------------------------------
        # Filter: meal type compatibility
        # ------------------------------------------------

        compatible = data[
            data["meal_type"].apply(
                lambda types: meal_slot in str(
                    types
                ).split(",")
            )
        ]

        if compatible.empty:
            return None

        # ------------------------------------------------
        # Filter: food group
        # ------------------------------------------------

        compatible = compatible[
            compatible["food_group"].isin(
                food_groups
            )
        ]

        if compatible.empty:
            return None

        # ------------------------------------------------
        # Score each candidate
        # ------------------------------------------------

        scored = []

        all_recent = (
            recent_ids.get("protein", [])
            + recent_ids.get("carb", [])
            + recent_ids.get("general", [])
        )

        for _, food in compatible.iterrows():
            score = 0.0
            food_id = food["food_id"]

            # Skip items already in this meal
            if food_id in exclude_ids:
                continue

            # Goal compatibility
            goal_tags = str(
                food["goal_tags"]
            ).split(",")

            if selected_goal in goal_tags:
                score += 3

            # Calorie proximity to role budget
            calories = float(food["calories"])
            calorie_diff = abs(
                calories - calorie_budget
            )

            if calorie_diff <= 30:
                score += 4
            elif calorie_diff <= 60:
                score += 3
            elif calorie_diff <= 100:
                score += 2
            elif calorie_diff <= 150:
                score += 1

            # Protein bonus
            protein = float(food["protein_g"])

            if protein >= 20:
                score += 2
            elif protein >= 10:
                score += 1

            # Fiber bonus
            fiber = float(food["fiber_g"])

            if fiber >= 6:
                score += 1
            elif fiber >= 3:
                score += 0.5

            # Expert direction adjustment
            direction = expert_result[
                "direction"
            ]

            if direction in {
                "PROFESSIONAL_REVIEW",
                "MAINTAIN_FIRST"
            }:
                if food["food_group"] in {
                    "vegetable",
                    "fruit",
                    "protein",
                    "whole_grain"
                }:
                    score += 1

            # Energy status adjustment
            energy_status = expert_result[
                "energy_status"
            ]

            if energy_status in {
                "LARGE_SURPLUS",
                "MODERATE_SURPLUS"
            }:
                if calories <= calorie_budget:
                    score += 1

            elif energy_status in {
                "LARGE_DEFICIT",
                "MODERATE_DEFICIT"
            }:
                if calories >= calorie_budget * 0.8:
                    score += 1

            # Anti-duplication penalty
            if food_id in all_recent:
                score -= 5

            # Small randomness for variety
            score += random.uniform(0, 1.5)

            scored.append({
                "food": food.to_dict(),
                "score": score
            })

        if not scored:
            return None

        scored.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        best = scored[0]["food"]

        return {
            "food_id": best["food_id"],
            "food_name": best["food_name"],
            "food_group": best["food_group"],
            "serving_g": int(best.get(
                "serving_g", 0
            )),
            "calories": int(best["calories"]),
            "protein_g": float(
                best["protein_g"]
            ),
            "carbs_g": float(
                best["carbs_g"]
            ),
            "fat_g": float(best["fat_g"]),
            "fiber_g": float(best["fiber_g"])
        }

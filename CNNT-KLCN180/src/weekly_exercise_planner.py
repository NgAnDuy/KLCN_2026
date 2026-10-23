"""Generate a personalized 7-day exercise plan.

Uses expert analysis results to determine training
frequency, split strategy, and exercise selection
based on the user's fitness level and goals.
"""

import random

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

EXERCISE_DATA_PATH = (
    BASE_DIR
    / "data"
    / "exercise_dataset.csv"
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

# Training split templates based on fitness level.
# True = training day, False = rest day.
SPLIT_TEMPLATES = {
    "3_days": {
        "pattern": [
            True, False, True,
            False, True, False, False
        ],
        "label": "3_DAYS_PER_WEEK"
    },
    "4_days": {
        "pattern": [
            True, True, False,
            True, False, True, False
        ],
        "label": "4_DAYS_PER_WEEK"
    },
    "5_days": {
        "pattern": [
            True, True, True,
            True, True, False, False
        ],
        "label": "5_DAYS_PER_WEEK"
    }
}

# Day focus rotation for training days
DAY_FOCUS_ROTATION = [
    "cardio",
    "strength_upper",
    "strength_lower",
    "flexibility",
    "full_body",
    "cardio",
    "strength_upper"
]


def _determine_split(
    exercise_status,
    direction
):
    """Pick a training split based on fitness level.

    Returns the split key and rest-day advice.
    """

    # Conservative directions limit intensity
    if direction in {
        "PROFESSIONAL_REVIEW",
        "MAINTAIN_FIRST"
    }:
        return "3_days"

    if exercise_status in {
        "VERY_LOW",
        "LOW"
    }:
        return "3_days"

    elif exercise_status == "GOOD":
        return "4_days"

    else:
        return "5_days"


def _get_max_intensity(
    exercise_status,
    direction
):
    """Determine maximum allowed intensity."""
    if direction in {
        "PROFESSIONAL_REVIEW",
        "MAINTAIN_FIRST"
    }:
        return "low"

    if exercise_status in {
        "VERY_LOW",
        "LOW"
    }:
        return "moderate"

    return "high"


def _intensity_value(intensity):
    """Convert intensity string to numeric value."""
    mapping = {
        "low": 1,
        "moderate": 2,
        "high": 3
    }

    return mapping.get(intensity, 2)


class WeeklyExercisePlanner:
    """Build a 7-day exercise schedule."""

    def __init__(self):
        self.exercise_data = pd.read_csv(
            EXERCISE_DATA_PATH
        )

    def generate(
        self,
        selected_goal,
        expert_result,
        weight_kg
    ):
        """Generate a complete 7-day exercise plan.

        Parameters
        ----------
        selected_goal : str
            The user-selected health goal.
        expert_result : dict
            Output from analyze_goal_conflict.
        weight_kg : float
            User's body weight for calorie estimation.

        Returns
        -------
        dict
            Weekly exercise plan with schedule info
            and 7 days of exercises or rest days.
        """
        exercise_status = expert_result[
            "exercise_status"
        ]

        direction = expert_result["direction"]

        split_key = _determine_split(
            exercise_status,
            direction
        )

        split = SPLIT_TEMPLATES[split_key]

        max_intensity = _get_max_intensity(
            exercise_status,
            direction
        )

        training_days = sum(split["pattern"])

        rest_days = 7 - training_days

        # Track recently used exercise IDs
        recent_exercise_ids = []

        weekly_plan = []

        # Training day counter for focus rotation
        training_index = 0

        total_calories_burned = 0

        for day_index, day_key in enumerate(
            DAY_KEYS
        ):
            is_training = split["pattern"][
                day_index
            ]

            if is_training:
                focus = DAY_FOCUS_ROTATION[
                    training_index
                    % len(DAY_FOCUS_ROTATION)
                ]

                day_plan = self._plan_training_day(
                    day_key=day_key,
                    focus=focus,
                    selected_goal=selected_goal,
                    expert_result=expert_result,
                    weight_kg=weight_kg,
                    max_intensity=max_intensity,
                    recent_exercise_ids=(
                        recent_exercise_ids
                    )
                )

                training_index += 1

            else:
                day_plan = self._plan_rest_day(
                    day_key=day_key,
                    expert_result=expert_result
                )

            total_calories_burned += day_plan.get(
                "estimated_calories",
                0
            )

            weekly_plan.append(day_plan)

        return {
            "split_label": split["label"],
            "training_days": training_days,
            "rest_days": rest_days,
            "max_intensity": max_intensity,
            "total_calories_burned": round(
                total_calories_burned
            ),
            "days": weekly_plan
        }

    def _plan_training_day(
        self,
        day_key,
        focus,
        selected_goal,
        expert_result,
        weight_kg,
        max_intensity,
        recent_exercise_ids
    ):
        """Select exercises for a training day."""
        exercise = self._select_exercise(
            focus=focus,
            selected_goal=selected_goal,
            expert_result=expert_result,
            weight_kg=weight_kg,
            max_intensity=max_intensity,
            recent_exercise_ids=(
                recent_exercise_ids
            )
        )

        if exercise is None:
            return self._plan_rest_day(
                day_key,
                expert_result
            )

        # Track for anti-duplication
        recent_exercise_ids.append(
            exercise["exercise_id"]
        )

        if len(recent_exercise_ids) > 4:
            recent_exercise_ids.pop(0)

        return {
            "day": day_key,
            "is_rest": False,
            "exercise": exercise,
            "estimated_calories": exercise[
                "estimated_calories"
            ],
            "focus": focus
        }

    def _plan_rest_day(
        self,
        day_key,
        expert_result
    ):
        """Create a rest/recovery day entry."""
        sleep_status = expert_result.get(
            "sleep_status",
            "GOOD"
        )

        hydration_status = expert_result.get(
            "hydration_status",
            "GOOD"
        )

        tips = []

        if sleep_status == "LOW":
            tips.append("PRIORITIZE_SLEEP")

        if hydration_status == "LOW":
            tips.append("INCREASE_HYDRATION")

        tips.append("LIGHT_STRETCHING")

        return {
            "day": day_key,
            "is_rest": True,
            "exercise": None,
            "estimated_calories": 0,
            "focus": "recovery",
            "recovery_tips": tips
        }

    def _select_exercise(
        self,
        focus,
        selected_goal,
        expert_result,
        weight_kg,
        max_intensity,
        recent_exercise_ids
    ):
        """Pick the best exercise for a given focus."""
        data = self.exercise_data.copy()

        max_intensity_val = _intensity_value(
            max_intensity
        )

        # Filter out exercises above max intensity
        data = data[
            data["intensity"].apply(
                lambda val: _intensity_value(val)
                <= max_intensity_val
            )
        ]

        if data.empty:
            return None

        scored = []

        for _, exercise in data.iterrows():
            score = 0.0

            exercise_id = exercise["exercise_id"]
            exercise_type = str(
                exercise["exercise_type"]
            )
            intensity = str(
                exercise["intensity"]
            )
            difficulty = str(
                exercise["difficulty"]
            )
            target_area = str(
                exercise["target_area"]
            )

            # Goal compatibility
            goal_tags = str(
                exercise["goal_tags"]
            ).split(",")

            if selected_goal in goal_tags:
                score += 3

            # Focus compatibility
            if focus == "cardio":
                if exercise_type in {
                    "cardio",
                    "cardio_strength",
                    "sport"
                }:
                    score += 4

            elif focus == "strength_upper":
                if exercise_type in {
                    "strength",
                    "strength_cardio"
                }:
                    score += 2

                if target_area in {
                    "upper_body",
                    "chest",
                    "back",
                    "shoulders",
                    "arms",
                    "core"
                }:
                    score += 3

            elif focus == "strength_lower":
                if exercise_type in {
                    "strength",
                    "strength_cardio"
                }:
                    score += 2

                if target_area in {
                    "lower_body",
                    "glutes",
                    "posterior_chain"
                }:
                    score += 3

            elif focus == "flexibility":
                if exercise_type in {
                    "flexibility",
                    "mobility",
                    "core_flexibility",
                    "recovery"
                }:
                    score += 5

            elif focus == "full_body":
                if target_area == "full_body":
                    score += 3

                if exercise_type in {
                    "strength_cardio",
                    "cardio_strength"
                }:
                    score += 2

            # Fitness level matching
            exercise_status = expert_result[
                "exercise_status"
            ]

            if exercise_status in {
                "VERY_LOW",
                "LOW"
            }:
                if difficulty == "beginner":
                    score += 3

                if intensity == "low":
                    score += 2

            elif exercise_status == "GOOD":
                if difficulty in {
                    "beginner",
                    "intermediate"
                }:
                    score += 2

            elif exercise_status == "HIGH":
                if difficulty in {
                    "intermediate",
                    "advanced"
                }:
                    score += 2

            # Body status: low BMI safety
            body_status = expert_result.get(
                "body_status",
                "NORMAL_BMI"
            )

            if body_status == "LOW_BMI":
                if intensity == "high":
                    score -= 4

                if exercise_type in {
                    "recovery",
                    "mobility",
                    "flexibility"
                }:
                    score += 2

            # Anti-duplication
            if exercise_id in recent_exercise_ids:
                score -= 5

            # Small randomness
            score += random.uniform(0, 1.5)

            # Calculate estimated calories
            met = float(exercise["met"])
            duration = float(
                exercise["duration_min"]
            )

            estimated_cal = (
                met
                * 3.5
                * weight_kg
                / 200
                * duration
            )

            scored.append({
                "exercise": exercise.to_dict(),
                "score": score,
                "estimated_cal": round(
                    estimated_cal, 1
                )
            })

        if not scored:
            return None

        scored.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        best = scored[0]
        ex = best["exercise"]

        return {
            "exercise_id": ex["exercise_id"],
            "exercise_name": ex["exercise_name"],
            "exercise_type": ex["exercise_type"],
            "intensity": ex["intensity"],
            "difficulty": ex["difficulty"],
            "duration_min": int(
                ex["duration_min"]
            ),
            "target_area": ex["target_area"],
            "equipment": ex["equipment"],
            "estimated_calories": best[
                "estimated_cal"
            ]
        }

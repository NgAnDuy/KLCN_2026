from src.exercise_recommender import (
    ExerciseRecommender
)
from src.food_recommender import (
    FoodRecommender
)


class PersonalizedRecommendationSystem:
    """Coordinate personalized recommendation engines."""

    def __init__(self):
        self.food_recommender = (
            FoodRecommender()
        )

        self.exercise_recommender = (
            ExerciseRecommender()
        )

    def generate(
        self,
        selected_goal,
        expert_result,
        features,
        top_foods=5,
        top_exercises=5
    ):
        row = features.iloc[0]

        weight_kg = float(
            row["weight_kg"]
        )

        foods = (
            self.food_recommender.recommend(
                selected_goal=selected_goal,
                expert_result=expert_result,
                top_n=top_foods
            )
        )

        exercises = (
            self.exercise_recommender.recommend(
                selected_goal=selected_goal,
                expert_result=expert_result,
                weight_kg=weight_kg,
                top_n=top_exercises
            )
        )

        summary = self._build_summary(
            expert_result
        )

        return {
            "summary": summary,
            "foods": foods,
            "exercises": exercises
        }

    def _build_summary(
        self,
        expert_result
    ):
        direction = expert_result[
            "direction"
        ]

        conflict = expert_result[
            "conflict_level"
        ]

        priorities = expert_result.get(
            "priorities",
            []
        )

        messages = []

        if direction == "PROFESSIONAL_REVIEW":
            messages.append(
                "The selected goal conflicts with the current "
                "health profile. Recommendations are kept "
                "conservative."
            )

        elif direction == "MAINTAIN_FIRST":
            messages.append(
                "Current conditions suggest stabilizing the "
                "current status before making larger changes."
            )

        elif direction == "REVIEW_GOAL":
            messages.append(
                "The selected goal differs strongly from the "
                "MLP assessment. Aggressive changes are not "
                "recommended."
            )

        else:
            messages.append(
                "The current profile supports personalized "
                "recommendations for the selected goal."
            )

        if conflict == "NONE":
            messages.append(
                "The selected goal is consistent with the "
                "MLP-predicted goal."
            )

        elif conflict == "MODERATE":
            messages.append(
                "The selected goal differs from the "
                "MLP-predicted goal."
            )

        elif conflict == "HIGH":
            messages.append(
                "A strong conflict exists between the selected "
                "goal and the MLP-predicted goal."
            )

        if priorities:
            readable_priorities = ", ".join(
                priority.replace(
                    "_",
                    " "
                ).title()
                for priority in priorities
            )

            messages.append(
                "Current priority areas: "
                f"{readable_priorities}."
            )

        return messages


def generate_recommendations(
    selected_goal,
    expert_result,
    features,
    top_foods=5,
    top_exercises=5
):
    system = (
        PersonalizedRecommendationSystem()
    )

    return system.generate(
        selected_goal=selected_goal,
        expert_result=expert_result,
        features=features,
        top_foods=top_foods,
        top_exercises=top_exercises
    )
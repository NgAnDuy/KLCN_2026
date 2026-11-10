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
        top_exercises=5,
        medical_conditions=(),
        allergies=(),
    ):
        row = features.iloc[0]

        weight_kg = float(
            row["weight_kg"]
        )

        foods, food_screening = (
            self.food_recommender.recommend(
                selected_goal=selected_goal,
                expert_result=expert_result,
                top_n=top_foods,
                medical_conditions=medical_conditions,
                allergies=allergies,
                return_screening=True,
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

        return {
            "foods": foods,
            "food_screening": food_screening,
            "exercises": exercises
        }


def generate_recommendations(
    selected_goal,
    expert_result,
    features,
    top_foods=5,
    top_exercises=5,
    medical_conditions=(),
    allergies=(),
):
    system = (
        PersonalizedRecommendationSystem()
    )

    return system.generate(
        selected_goal=selected_goal,
        expert_result=expert_result,
        features=features,
        top_foods=top_foods,
        top_exercises=top_exercises,
        medical_conditions=medical_conditions,
        allergies=allergies,
    )

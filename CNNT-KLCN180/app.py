from flask import Flask
from flask import render_template
from flask import request

from src.expert_recommendation import (
    GOAL_LABELS,
    analyze_goal_conflict
)
from src.feature_engineering import create_health_features
from src.predictor import HealthGoalPredictor
from src.recommendation import generate_recommendations


app = Flask(__name__)

predictor = HealthGoalPredictor()

GOALS = {
    "weight_loss": "Weight Loss",
    "weight_gain": "Weight Gain",
    "maintenance": "Maintenance",
    "fitness_improvement": "Fitness Improvement",
    "healthy_lifestyle": "Healthy Lifestyle"
}

ACTIVITY_LEVELS = [
    "Sedentary",
    "Light",
    "Moderate",
    "Active",
    "Very Active"
]


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        try:
            selected_goal = request.form["goal"]

            age = int(request.form["age"])
            gender = request.form["gender"]

            height_cm = float(
                request.form["height_cm"]
            )

            weight_kg = float(
                request.form["weight_kg"]
            )

            activity_level = request.form[
                "activity_level"
            ]

            calories_consumed = float(
                request.form["calories_consumed"]
            )

            avg_steps_7d = float(
                request.form["avg_steps_7d"]
            )

            avg_sleep_hours_7d = float(
                request.form["avg_sleep_hours_7d"]
            )

            water_intake_l = float(
                request.form["water_intake_l"]
            )

            avg_exercise_minutes_7d = float(
                request.form[
                    "avg_exercise_minutes_7d"
                ]
            )

            exercise_sessions_7d = int(
                request.form[
                    "exercise_sessions_7d"
                ]
            )

            avg_calories_burned_7d = float(
                request.form[
                    "avg_calories_burned_7d"
                ]
            )

            features, calculated = create_health_features(
                age=age,
                gender=gender,
                height_cm=height_cm,
                weight_kg=weight_kg,
                activity_level=activity_level,
                calories_consumed=calories_consumed,
                avg_steps_7d=avg_steps_7d,
                avg_sleep_hours_7d=avg_sleep_hours_7d,
                water_intake_l=water_intake_l,
                avg_exercise_minutes_7d=(
                    avg_exercise_minutes_7d
                ),
                exercise_sessions_7d=(
                    exercise_sessions_7d
                ),
                avg_calories_burned_7d=(
                    avg_calories_burned_7d
                )
            )

            mlp_result = predictor.predict(
                features
            )

            expert_result = analyze_goal_conflict(
                selected_goal=selected_goal,
                predicted_goal=mlp_result["goal"],
                confidence=mlp_result["confidence"],
                features=features
            )

            recommendations = generate_recommendations(
                selected_goal=selected_goal,
                expert_result=expert_result,
                features=features,
                top_foods=5,
                top_exercises=5
            )

            probabilities = sorted(
                mlp_result["probabilities"].items(),
                key=lambda item: item[1],
                reverse=True
            )

            result = {
                "selected_goal": GOAL_LABELS[
                    selected_goal
                ],
                "predicted_goal": GOAL_LABELS[
                    mlp_result["goal"]
                ],
                "confidence": (
                    mlp_result["confidence"] * 100
                ),
                "probabilities": probabilities,
                "calculated": calculated,
                "expert": expert_result,
                "recommendations": recommendations
            }

        except Exception as exception:
            error = str(exception)

    return render_template(
        "index.html",
        goals=GOALS,
        activities=ACTIVITY_LEVELS,
        result=result,
        error=error
    )


if __name__ == "__main__":
    app.run(
        debug=True
    )
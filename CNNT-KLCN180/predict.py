from src.expert_recommendation import (
    GOAL_LABELS,
    analyze_goal_conflict
)
from src.feature_engineering import (
    create_health_features
)
from src.predictor import HealthGoalPredictor
from src.recommendation import (
    generate_recommendations
)


GOALS = [
    "weight_loss",
    "weight_gain",
    "maintenance",
    "fitness_improvement",
    "healthy_lifestyle"
]


ACTIVITY_LEVELS = [
    "Sedentary",
    "Light",
    "Moderate",
    "Active",
    "Very Active"
]


def input_float(message):
    while True:
        try:
            return float(
                input(message)
            )
        except ValueError:
            print(
                "Please enter a valid number."
            )


def input_int(message):
    while True:
        try:
            return int(
                input(message)
            )
        except ValueError:
            print(
                "Please enter a valid integer."
            )


def select_goal():
    print("\n" + "=" * 70)
    print("SELECT YOUR GOAL")
    print("=" * 70)

    for index, goal in enumerate(
        GOALS,
        start=1
    ):
        print(
            f"{index}. "
            f"{GOAL_LABELS[goal]}"
        )

    while True:
        choice = input_int(
            "Select goal (1-5): "
        )

        if 1 <= choice <= len(GOALS):
            return GOALS[
                choice - 1
            ]

        print(
            "Please select from 1 to 5."
        )


def select_activity():
    print("\n" + "=" * 70)
    print("ACTIVITY LEVEL")
    print("=" * 70)

    for index, activity in enumerate(
        ACTIVITY_LEVELS,
        start=1
    ):
        print(
            f"{index}. {activity}"
        )

    while True:
        choice = input_int(
            "Select activity level (1-5): "
        )

        if (
            1
            <= choice
            <= len(ACTIVITY_LEVELS)
        ):
            return ACTIVITY_LEVELS[
                choice - 1
            ]

        print(
            "Please select from 1 to 5."
        )


def print_current_features(
    calculated
):
    print("\n" + "=" * 70)
    print("CURRENT FEATURES")
    print("=" * 70)

    print(
        f"BMI                     : "
        f"{calculated['bmi']:.2f}"
    )

    print(
        f"BMR                     : "
        f"{calculated['bmr']:.0f} kcal"
    )

    print(
        f"TDEE                    : "
        f"{calculated['tdee']:.0f} kcal"
    )

    print(
        f"Calorie Balance         : "
        f"{calculated['calorie_balance']:+.0f} kcal"
    )

    print(
        f"Calorie Balance %       : "
        f"{calculated['calorie_balance_pct']:+.2f}%"
    )

    print(
        f"Calorie Intake Ratio    : "
        f"{calculated['calorie_intake_ratio']:.3f}"
    )

    print(
        f"Hydration Ratio         : "
        f"{calculated['hydration_ratio']:.3f}"
    )

    print(
        f"Weekly Exercise Volume  : "
        f"{calculated['weekly_exercise_volume']:.0f}"
    )

    print(
        f"Exercise Min / Session  : "
        f"{calculated['exercise_minutes_per_session']:.2f}"
    )

    print(
        f"Steps / kg              : "
        f"{calculated['steps_per_kg']:.2f}"
    )

    print(
        f"Sleep Deviation         : "
        f"{calculated['sleep_deviation']:+.2f} h"
    )


def print_goal_analysis(
    selected_goal,
    mlp_result,
    expert_result
):
    print("\n" + "=" * 70)
    print("GOAL ANALYSIS")
    print("=" * 70)

    print(
        "Selected Goal      :",
        GOAL_LABELS[
            selected_goal
        ]
    )

    print(
        "MLP Predicted Goal :",
        GOAL_LABELS[
            mlp_result["goal"]
        ]
    )

    print(
        "MLP Confidence     :",
        f"{mlp_result['confidence'] * 100:.2f}%"
    )

    print(
        "Conflict Level     :",
        expert_result[
            "conflict_level"
        ]
    )

    print(
        "Direction          :",
        expert_result[
            "direction"
        ]
    )

    print("\nMLP Probabilities:")

    probabilities = sorted(
        mlp_result[
            "probabilities"
        ].items(),
        key=lambda item: item[1],
        reverse=True
    )

    for goal, probability in probabilities:
        print(
            f"{goal:25s}: "
            f"{probability * 100:6.2f}%"
        )


def print_expert_analysis(
    expert_result
):
    print("\n" + "=" * 70)
    print("EXPERT ANALYSIS")
    print("=" * 70)

    print("\nCurrent Status:")

    print(
        "Body Status       :",
        expert_result[
            "body_status"
        ]
    )

    print(
        "Energy Status     :",
        expert_result[
            "energy_status"
        ]
    )

    print(
        "Step Status       :",
        expert_result[
            "step_status"
        ]
    )

    print(
        "Exercise Status   :",
        expert_result[
            "exercise_status"
        ]
    )

    print(
        "Sleep Status      :",
        expert_result[
            "sleep_status"
        ]
    )

    print(
        "Hydration Status  :",
        expert_result[
            "hydration_status"
        ]
    )

    print("\nPriority Areas:")

    priorities = expert_result[
        "priorities"
    ]

    if priorities:
        for priority in priorities:
            print(
                f"- {priority}"
            )
    else:
        print(
            "- No major priority area detected."
        )

    print("\nReasons:")

    for reason in expert_result[
        "reasons"
    ]:
        print(
            f"- {reason}"
        )

    print("\nWarnings:")

    warnings = expert_result[
        "warnings"
    ]

    if warnings:
        for warning in warnings:
            print(
                f"- {warning}"
            )
    else:
        print(
            "- No major warning detected."
        )


def print_recommendation_summary(
    recommendations
):
    print("\n" + "=" * 70)
    print("PERSONALIZED RECOMMENDATION")
    print("=" * 70)

    for item in recommendations[
        "summary"
    ]:
        print(
            f"- {item}"
        )


def print_food_recommendations(
    recommendations
):
    print("\n" + "=" * 70)
    print("TOP FOOD RECOMMENDATIONS")
    print("=" * 70)

    foods = recommendations[
        "foods"
    ]

    if not foods:
        print(
            "No suitable food recommendation found."
        )

        return

    for index, food in enumerate(
        foods,
        start=1
    ):
        print(
            f"\n{index}. "
            f"{food['food_name']}"
        )

        print(
            f"   Meal Type : "
            f"{food['meal_type']}"
        )

        print(
            f"   Group     : "
            f"{food['food_group']}"
        )

        print(
            f"   Calories  : "
            f"{float(food['calories']):.0f} kcal"
        )

        print(
            f"   Protein   : "
            f"{float(food['protein_g']):.1f} g"
        )

        print(
            f"   Carbs     : "
            f"{float(food['carbs_g']):.1f} g"
        )

        print(
            f"   Fat       : "
            f"{float(food['fat_g']):.1f} g"
        )

        print(
            f"   Fiber     : "
            f"{float(food['fiber_g']):.1f} g"
        )

        print(
            f"   Sodium    : "
            f"{float(food['sodium_mg']):.0f} mg"
        )

        print(
            f"   Score     : "
            f"{float(food['score']):.1f}"
        )

        if food["reason"]:
            print(
                f"   Why       : "
                f"{food['reason']}"
            )


def print_exercise_recommendations(
    recommendations
):
    print("\n" + "=" * 70)
    print("TOP EXERCISE RECOMMENDATIONS")
    print("=" * 70)

    exercises = recommendations[
        "exercises"
    ]

    if not exercises:
        print(
            "No suitable exercise recommendation found."
        )

        return

    for index, exercise in enumerate(
        exercises,
        start=1
    ):
        print(
            f"\n{index}. "
            f"{exercise['exercise_name']}"
        )

        print(
            f"   Type       : "
            f"{exercise['exercise_type']}"
        )

        print(
            f"   Intensity  : "
            f"{exercise['intensity']}"
        )

        print(
            f"   Difficulty : "
            f"{exercise['difficulty']}"
        )

        print(
            f"   Duration   : "
            f"{float(exercise['duration_min']):.0f} min"
        )

        print(
            f"   MET        : "
            f"{float(exercise['met']):.1f}"
        )

        print(
            f"   Target     : "
            f"{exercise['target_area']}"
        )

        print(
            f"   Equipment  : "
            f"{exercise['equipment']}"
        )

        print(
            f"   Impact     : "
            f"{exercise['impact_level']}"
        )

        print(
            f"   Est. Burn  : "
            f"{float(exercise['estimated_calories']):.1f} kcal"
        )

        print(
            f"   Score      : "
            f"{float(exercise['score']):.1f}"
        )

        if exercise["reason"]:
            print(
                f"   Why        : "
                f"{exercise['reason']}"
            )


def print_final_summary(
    selected_goal,
    mlp_result,
    expert_result,
    recommendations
):
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    print(
        "Selected Goal      :",
        GOAL_LABELS[
            selected_goal
        ]
    )

    print(
        "MLP Predicted Goal :",
        GOAL_LABELS[
            mlp_result["goal"]
        ]
    )

    print(
        "MLP Confidence     :",
        f"{mlp_result['confidence'] * 100:.2f}%"
    )

    print(
        "Conflict Level     :",
        expert_result[
            "conflict_level"
        ]
    )

    print(
        "Expert Direction   :",
        expert_result[
            "direction"
        ]
    )

    print(
        "Foods Recommended  :",
        len(
            recommendations[
                "foods"
            ]
        )
    )

    print(
        "Exercises Recommended:",
        len(
            recommendations[
                "exercises"
            ]
        )
    )

    print("=" * 70)


def main():
    print("\n" + "=" * 70)
    print(
        "HEALTH GOAL & PERSONALIZED "
        "RECOMMENDATION SYSTEM"
    )
    print("=" * 70)

    # ========================================================
    # USER GOAL
    # ========================================================

    selected_goal = select_goal()

    # ========================================================
    # CURRENT INFORMATION
    # ========================================================

    print("\n" + "=" * 70)
    print("ENTER CURRENT INFORMATION")
    print("=" * 70)

    age = input_int(
        "Age: "
    )

    gender = input(
        "Gender (Male/Female): "
    ).strip()

    height_cm = input_float(
        "Height (cm): "
    )

    weight_kg = input_float(
        "Weight (kg): "
    )

    activity_level = (
        select_activity()
    )

    calories_consumed = input_float(
        "Daily calories (kcal): "
    )

    avg_steps_7d = input_float(
        "Average daily steps: "
    )

    avg_sleep_hours_7d = input_float(
        "Average sleep hours: "
    )

    water_intake_l = input_float(
        "Daily water intake (L): "
    )

    avg_exercise_minutes_7d = (
        input_float(
            "Average exercise minutes: "
        )
    )

    exercise_sessions_7d = (
        input_int(
            "Exercise sessions in 7 days: "
        )
    )

    avg_calories_burned_7d = (
        input_float(
            "Average exercise calories burned: "
        )
    )

    # ========================================================
    # FEATURE ENGINEERING
    # ========================================================

    features, calculated = (
        create_health_features(
            age=age,
            gender=gender,
            height_cm=height_cm,
            weight_kg=weight_kg,
            activity_level=activity_level,
            calories_consumed=(
                calories_consumed
            ),
            avg_steps_7d=(
                avg_steps_7d
            ),
            avg_sleep_hours_7d=(
                avg_sleep_hours_7d
            ),
            water_intake_l=(
                water_intake_l
            ),
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
    )

    # ========================================================
    # MLP
    # ========================================================

    predictor = (
        HealthGoalPredictor()
    )

    mlp_result = predictor.predict(
        features
    )

    # ========================================================
    # EXPERT SYSTEM
    # ========================================================

    expert_result = (
        analyze_goal_conflict(
            selected_goal=selected_goal,
            predicted_goal=(
                mlp_result["goal"]
            ),
            confidence=(
                mlp_result["confidence"]
            ),
            features=features
        )
    )

    # ========================================================
    # FOOD + EXERCISE RECOMMENDATION
    # ========================================================

    recommendations = (
        generate_recommendations(
            selected_goal=selected_goal,
            expert_result=expert_result,
            features=features,
            top_foods=5,
            top_exercises=5
        )
    )

    # ========================================================
    # OUTPUT
    # ========================================================

    print_current_features(
        calculated
    )

    print_goal_analysis(
        selected_goal,
        mlp_result,
        expert_result
    )

    print_expert_analysis(
        expert_result
    )

    print_recommendation_summary(
        recommendations
    )

    print_food_recommendations(
        recommendations
    )

    print_exercise_recommendations(
        recommendations
    )

    print_final_summary(
        selected_goal,
        mlp_result,
        expert_result,
        recommendations
    )


if __name__ == "__main__":
    main()
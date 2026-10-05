from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from src.expert_recommendation import (
    analyze_goal_conflict,
    build_detailed_analysis
)
from src.feature_engineering import create_health_features
from src.health_status import analyze_health_status
from src.predictor import HealthGoalPredictor
from src.recommendation import generate_recommendations
from src.translator import translate


app = Flask(__name__)

app.secret_key = "health-recommendation-local-key"


# ============================================================
# CONSTANTS
# ============================================================

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


# ============================================================
# LOAD MODEL
# ============================================================

predictor = HealthGoalPredictor()


# ============================================================
# LANGUAGE
# ============================================================

def get_language():
    """Return the currently selected language."""
    language = session.get(
        "language",
        "en"
    )

    if language not in {
        "vi",
        "en"
    }:
        language = "en"

    return language


def translate_result_value(value):
    """Translate an internal value for Jinja."""
    return translate(
        value,
        get_language()
    )


app.jinja_env.globals[
    "translate_value"
] = translate_result_value


# ============================================================
# LANGUAGE PAGE
# ============================================================

@app.route("/")
def language():
    """Display language selection page."""
    return render_template(
        "language.html"
    )


@app.route(
    "/select-language/<language_code>"
)
def select_language(language_code):
    """Save the selected language."""
    if language_code not in {
        "vi",
        "en"
    }:
        language_code = "en"

    session["language"] = language_code

    return redirect(
        url_for("health_form")
    )


# ============================================================
# HEALTH INPUT FORM
# ============================================================

@app.route(
    "/health",
    methods=[
        "GET",
        "POST"
    ]
)
def health_form():
    """Display and process the health input form."""
    language_code = get_language()

    if request.method == "POST":
        try:
            selected_goal = request.form[
                "goal"
            ]

            if selected_goal not in GOALS:
                raise ValueError(
                    "Invalid selected goal."
                )

            activity_level = request.form[
                "activity_level"
            ]

            if activity_level not in ACTIVITY_LEVELS:
                raise ValueError(
                    "Invalid activity level."
                )

            health_input = {
                "selected_goal": selected_goal,

                "age": int(
                    request.form["age"]
                ),

                "gender": request.form[
                    "gender"
                ],

                "height_cm": float(
                    request.form["height_cm"]
                ),

                "weight_kg": float(
                    request.form["weight_kg"]
                ),

                "activity_level":
                    activity_level,

                "calories_consumed": float(
                    request.form[
                        "calories_consumed"
                    ]
                ),

                "avg_steps_7d": float(
                    request.form[
                        "avg_steps_7d"
                    ]
                ),

                "avg_sleep_hours_7d": float(
                    request.form[
                        "avg_sleep_hours_7d"
                    ]
                ),

                "water_intake_l": float(
                    request.form[
                        "water_intake_l"
                    ]
                ),

                "avg_exercise_minutes_7d": float(
                    request.form[
                        "avg_exercise_minutes_7d"
                    ]
                ),

                "exercise_sessions_7d": int(
                    request.form[
                        "exercise_sessions_7d"
                    ]
                ),

                "avg_calories_burned_7d": float(
                    request.form[
                        "avg_calories_burned_7d"
                    ]
                )
            }

            session["health_input"] = (
                health_input
            )

            session.pop(
                "analysis_result",
                None
            )

            return redirect(
                url_for("analyzing")
            )

        except (
            ValueError,
            KeyError
        ) as error:
            return render_template(
                "index.html",
                goals=GOALS,
                activities=ACTIVITY_LEVELS,
                language=language_code,
                translate=translate,
                error=str(error)
            )

    return render_template(
        "index.html",
        goals=GOALS,
        activities=ACTIVITY_LEVELS,
        language=language_code,
        translate=translate,
        error=None
    )


# ============================================================
# ANALYZING PAGE
# ============================================================

@app.route("/analyzing")
def analyzing():
    """Display the analysis loading page."""
    if "health_input" not in session:
        return redirect(
            url_for("health_form")
        )

    return render_template(
        "analyzing.html",
        language=get_language()
    )


# ============================================================
# PROCESS ANALYSIS
# ============================================================

@app.route("/process-analysis")
def process_analysis():
    """Run feature engineering, MLP and expert analysis."""
    user_input = session.get(
        "health_input"
    )

    if not user_input:
        return redirect(
            url_for("health_form")
        )

    selected_goal = user_input[
        "selected_goal"
    ]

    # ========================================================
    # 1. FEATURE ENGINEERING
    # ========================================================

    features, calculated = create_health_features(
        age=user_input["age"],
        gender=user_input["gender"],
        height_cm=user_input["height_cm"],
        weight_kg=user_input["weight_kg"],

        activity_level=user_input[
            "activity_level"
        ],

        calories_consumed=user_input[
            "calories_consumed"
        ],

        avg_steps_7d=user_input[
            "avg_steps_7d"
        ],

        avg_sleep_hours_7d=user_input[
            "avg_sleep_hours_7d"
        ],

        water_intake_l=user_input[
            "water_intake_l"
        ],

        avg_exercise_minutes_7d=user_input[
            "avg_exercise_minutes_7d"
        ],

        exercise_sessions_7d=user_input[
            "exercise_sessions_7d"
        ],

        avg_calories_burned_7d=user_input[
            "avg_calories_burned_7d"
        ]
    )

    # ========================================================
    # 2. MLP
    # ========================================================

    mlp_result = predictor.predict(
        features
    )

    # ========================================================
    # 3. EXPERT GOAL ANALYSIS
    # ========================================================

    expert_result = analyze_goal_conflict(
        selected_goal=selected_goal,

        predicted_goal=mlp_result[
            "goal"
        ],

        confidence=mlp_result[
            "confidence"
        ],

        features=features
    )

    # ========================================================
    # 4. CURRENT HEALTH STATUS
    # ========================================================

    current_status = analyze_health_status(
        features,
        calculated
    )

    # ========================================================
    # 5. DETAILED EXPERT EXPLANATION
    # ========================================================

    detailed_analysis = (
        build_detailed_analysis(
            current_status,
            get_language()
        )
    )

    # ========================================================
    # 6. RECOMMENDATIONS
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
    # 7. MLP PROBABILITIES
    # ========================================================

    probabilities = sorted(
        mlp_result[
            "probabilities"
        ].items(),
        key=lambda item: item[1],
        reverse=True
    )

    probability_data = []

    for goal, probability in probabilities:
        probability_data.append(
            [
                goal,
                float(probability)
            ]
        )

    # ========================================================
    # 8. CALCULATED FEATURES
    # ========================================================

    calculated_data = {}

    for key, value in calculated.items():
        if hasattr(
            value,
            "item"
        ):
            calculated_data[key] = (
                value.item()
            )
        else:
            calculated_data[key] = value

    # ========================================================
    # 9. SAVE RESULT
    # ========================================================

    session["analysis_result"] = {
        "selected_goal":
            selected_goal,

        "predicted_goal":
            mlp_result["goal"],

        "confidence":
            float(
                mlp_result[
                    "confidence"
                ]
            ),

        "probabilities":
            probability_data,

        "calculated":
            calculated_data,

        "health_status":
            current_status,

        "detailed_analysis":
            detailed_analysis,

        "expert":
            expert_result,

        "recommendations":
            recommendations
    }

    return redirect(
        url_for("result")
    )


# ============================================================
# RESULT PAGE
# ============================================================

@app.route("/result")
def result():
    """Display analysis results."""
    analysis_result = session.get(
        "analysis_result"
    )

    if not analysis_result:
        return redirect(
            url_for("health_form")
        )

    return render_template(
        "result.html",
        result=analysis_result,
        language=get_language(),
        translate=translate
    )


# ============================================================
# HEALTH STATUS PAGE
# ============================================================

@app.route("/health-status")
def health_status():
    """Display detailed current health status."""
    analysis_result = session.get(
        "analysis_result"
    )

    if not analysis_result:
        return redirect(
            url_for("health_form")
        )

    return render_template(
        "health_status.html",
        result=analysis_result,
        language=get_language(),
        translate=translate
    )


# ============================================================
# NEW ANALYSIS
# ============================================================

@app.route("/new-analysis")
def new_analysis():
    """Clear previous data and start a new analysis."""
    session.pop(
        "health_input",
        None
    )

    session.pop(
        "analysis_result",
        None
    )

    return redirect(
        url_for("health_form")
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
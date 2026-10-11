
import json
import math
import os
import threading
import time
import uuid

from pathlib import Path

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    logout_user,
)

from auth import AUTH_MESSAGES, auth_blueprint
from models import HealthAnalysis, User, db

from src.expert_recommendation import (
    analyze_goal_conflict,
    build_detailed_analysis,
)
from src.feature_engineering import create_health_features
from src.health_status import analyze_health_status
from src.predictor import HealthGoalPredictor
from src.recommendation import generate_recommendations
from src.translator import translate


# ============================================================
# FLASK CONFIGURATION
# ============================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY",
    "health-recommendation-development-only",
)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///health.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False

# Do not create persistent remember-me cookies.
app.config["REMEMBER_COOKIE_DURATION"] = 0


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

db.init_app(app)

with app.app_context():
    db.create_all()


# ============================================================
# LOGIN CONFIGURATION
# ============================================================

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "auth.login"
login_manager.login_message = None

app.register_blueprint(auth_blueprint)


@login_manager.user_loader
def load_user(user_id):
    """Load the currently authenticated user."""

    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


# ============================================================
# SERVER SESSION MANAGEMENT
# ============================================================

SERVER_OFFLINE_TIMEOUT = 30
HEARTBEAT_INTERVAL = 2

INSTANCE_DIRECTORY = Path(app.instance_path)

INSTANCE_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)

SERVER_STATE_FILE = (
    INSTANCE_DIRECTORY / "server_session_state.json"
)

SERVER_STATE_LOCK = threading.Lock()


def read_server_state():
    """Read the previous server heartbeat and session ID."""

    if not SERVER_STATE_FILE.exists():
        return None

    try:
        with SERVER_STATE_FILE.open(
            "r",
            encoding="utf-8",
        ) as state_file:
            state = json.load(state_file)

        if not isinstance(state, dict):
            return None

        return state

    except (OSError, ValueError, TypeError):
        return None


def write_server_state(server_session_id):
    """Write the latest server heartbeat atomically."""

    state = {
        "server_session_id": server_session_id,
        "last_heartbeat": time.time(),
    }

    temporary_file = SERVER_STATE_FILE.with_suffix(
        ".tmp"
    )

    with SERVER_STATE_LOCK:
        with temporary_file.open(
            "w",
            encoding="utf-8",
        ) as state_file:
            json.dump(state, state_file)

        os.replace(
            temporary_file,
            SERVER_STATE_FILE,
        )


def initialize_server_session():
    """Restore or replace the previous server session ID."""

    previous_state = read_server_state()
    current_time = time.time()

    if previous_state is not None:
        previous_session_id = previous_state.get(
            "server_session_id"
        )

        last_heartbeat = previous_state.get(
            "last_heartbeat"
        )

        if (
            isinstance(previous_session_id, str)
            and previous_session_id
            and isinstance(last_heartbeat, (int, float))
        ):
            offline_seconds = (
                current_time - last_heartbeat
            )

            if (
                0 <= offline_seconds
                <= SERVER_OFFLINE_TIMEOUT
            ):
                return previous_session_id

    return uuid.uuid4().hex


SERVER_SESSION_ID = initialize_server_session()

# Share the active server ID with the authentication blueprint.
auth_blueprint.server_session_id = SERVER_SESSION_ID


def server_heartbeat_worker():
    """Periodically record that the server is running."""

    while True:
        try:
            write_server_state(SERVER_SESSION_ID)
        except OSError as error:
            app.logger.error(
                "Unable to update server heartbeat: %s",
                error,
            )

        time.sleep(HEARTBEAT_INTERVAL)


heartbeat_thread = threading.Thread(
    target=server_heartbeat_worker,
    daemon=True,
    name="health-server-heartbeat",
)

heartbeat_thread.start()


# ============================================================
# ROUTE ACCESS CONTROL
# ============================================================

PUBLIC_ENDPOINTS = {
    "language",
    "select_language",
    "auth.login",
    "auth.register",
    "static",
}


@app.before_request
def protect_private_routes():
    """Reject expired sessions and protect private routes."""

    endpoint = request.endpoint

    if endpoint is None:
        return None

    # Validate an existing authenticated session first.
    if current_user.is_authenticated:
        stored_session_id = session.get(
            "server_session_id"
        )

        if stored_session_id != SERVER_SESSION_ID:
            language_code = session.get(
                "language",
                "vi",
            )

            if language_code not in {"vi", "en"}:
                language_code = "vi"

            logout_user()
            session.clear()

            session["language"] = language_code

            flash(
                AUTH_MESSAGES[language_code][
                    "session_expired"
                ],
                "error",
            )

            return redirect(url_for("auth.login"))

    # Public pages do not require authentication.
    if endpoint in PUBLIC_ENDPOINTS:
        return None

    # Everything else requires a valid login.
    if not current_user.is_authenticated:
        language_code = session.get(
            "language",
            "vi",
        )

        if language_code not in {"vi", "en"}:
            language_code = "vi"

        flash(
            AUTH_MESSAGES[language_code][
                "login_required"
            ],
            "error",
        )

        return redirect(url_for("auth.login"))

    return None


# ============================================================
# CONSTANTS
# ============================================================

GOALS = [
    "weight_loss",
    "weight_gain",
    "maintenance",
    "fitness_improvement",
    "healthy_lifestyle",
]

ACTIVITY_LEVELS = [
    "Sedentary",
    "Light",
    "Moderate",
    "Active",
    "Very Active",
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

    language_code = session.get(
        "language",
        "en",
    )

    if language_code not in {"vi", "en"}:
        language_code = "en"

    return language_code


def translate_result_value(value):
    """Translate an internal value for Jinja templates."""

    return translate(
        value,
        get_language(),
    )


app.jinja_env.globals[
    "translate_value"
] = translate_result_value


# ============================================================
# JSON SERIALIZATION
# ============================================================

def make_json_safe(value):
    """Convert analysis values into JSON-compatible data."""

    if isinstance(value, dict):
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            make_json_safe(item)
            for item in value
        ]

    if hasattr(value, "item"):
        return make_json_safe(value.item())

    if hasattr(value, "tolist"):
        return make_json_safe(value.tolist())

    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        if not math.isfinite(value):
            return None

        return value

    if isinstance(value, str):
        return value

    if value is None:
        return None

    return str(value)


# ============================================================
# LANGUAGE PAGE
# ============================================================

@app.route("/")
def language():
    """Display the language selection page."""

    return render_template(
        "language.html"
    )


@app.route("/select-language/<language_code>")
def select_language(language_code):
    """Save the selected language."""

    if language_code not in {"vi", "en"}:
        language_code = "en"

    session["language"] = language_code

    if current_user.is_authenticated:
        return redirect(
            url_for("health_form")
        )

    return redirect(
        url_for("auth.login")
    )


# ============================================================
# HEALTH INPUT FORM
# ============================================================

@app.route(
    "/health",
    methods=["GET", "POST"],
)
@login_required
def health_form():
    """Display and process the health input form."""

    language_code = get_language()

    if request.method == "POST":
        try:
            selected_goal = request.form["goal"]

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

            gender = request.form["gender"]

            if gender not in {"Male", "Female"}:
                raise ValueError(
                    "Invalid gender."
                )

            health_input = {
                "selected_goal": selected_goal,
                "age": int(request.form["age"]),
                "gender": gender,
                "height_cm": float(
                    request.form["height_cm"]
                ),
                "weight_kg": float(
                    request.form["weight_kg"]
                ),
                "activity_level": activity_level,
                "calories_consumed": float(
                    request.form["calories_consumed"]
                ),
                "avg_steps_7d": float(
                    request.form["avg_steps_7d"]
                ),
                "avg_sleep_hours_7d": float(
                    request.form["avg_sleep_hours_7d"]
                ),
                "water_intake_l": float(
                    request.form["water_intake_l"]
                ),
                "avg_exercise_minutes_7d": float(
                    request.form["avg_exercise_minutes_7d"]
                ),
                "exercise_sessions_7d": int(
                    request.form["exercise_sessions_7d"]
                ),
                "avg_calories_burned_7d": float(
                    request.form["avg_calories_burned_7d"]
                ),
            }

            if not 1 <= health_input["age"] <= 120:
                raise ValueError(
                    "Age must be between 1 and 120."
                )

            if health_input["height_cm"] <= 0:
                raise ValueError(
                    "Height must be greater than zero."
                )

            if health_input["weight_kg"] <= 0:
                raise ValueError(
                    "Weight must be greater than zero."
                )

            if not 0 <= health_input[
                "avg_sleep_hours_7d"
            ] <= 24:
                raise ValueError(
                    "Sleep hours must be between 0 and 24."
                )

            non_negative_fields = [
                "calories_consumed",
                "avg_steps_7d",
                "water_intake_l",
                "avg_exercise_minutes_7d",
                "exercise_sessions_7d",
                "avg_calories_burned_7d",
            ]

            for field_name in non_negative_fields:
                field_value = health_input[field_name]

                if not math.isfinite(
                    float(field_value)
                ):
                    raise ValueError(
                        f"{field_name} must be finite."
                    )

                if field_value < 0:
                    raise ValueError(
                        f"{field_name} cannot be negative."
                    )

            for field_name in [
                "height_cm",
                "weight_kg",
                "avg_sleep_hours_7d",
            ]:
                if not math.isfinite(
                    float(health_input[field_name])
                ):
                    raise ValueError(
                        f"{field_name} must be finite."
                    )

            session["health_input"] = health_input
            session.pop("analysis_result", None)
            session.pop("analysis_id", None)

            return redirect(
                url_for("analyzing")
            )

        except (ValueError, KeyError) as error:
            return render_template(
                "index.html",
                goals=GOALS,
                activities=ACTIVITY_LEVELS,
                language=language_code,
                translate=translate,
                error=str(error),
            )

    return render_template(
        "index.html",
        goals=GOALS,
        activities=ACTIVITY_LEVELS,
        language=language_code,
        translate=translate,
        error=None,
    )


# ============================================================
# ANALYZING PAGE
# ============================================================

@app.route("/analyzing")
@login_required
def analyzing():
    """Display the analysis loading page."""

    if "health_input" not in session:
        return redirect(
            url_for("health_form")
        )

    return render_template(
        "analyzing.html",
        language=get_language(),
    )


# ============================================================
# PROCESS ANALYSIS
# ============================================================

@app.route("/process-analysis")
@login_required
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
        activity_level=user_input["activity_level"],
        calories_consumed=user_input["calories_consumed"],
        avg_steps_7d=user_input["avg_steps_7d"],
        avg_sleep_hours_7d=user_input["avg_sleep_hours_7d"],
        water_intake_l=user_input["water_intake_l"],
        avg_exercise_minutes_7d=user_input[
            "avg_exercise_minutes_7d"
        ],
        exercise_sessions_7d=user_input[
            "exercise_sessions_7d"
        ],
        avg_calories_burned_7d=user_input[
            "avg_calories_burned_7d"
        ],
    )

    # ========================================================
    # 2. MLP PREDICTION
    # ========================================================

    mlp_result = predictor.predict(
        features
    )

    # ========================================================
    # 3. EXPERT GOAL ANALYSIS
    # ========================================================

    expert_result = analyze_goal_conflict(
        selected_goal=selected_goal,
        predicted_goal=mlp_result["goal"],
        confidence=mlp_result["confidence"],
        features=features,
    )

    # ========================================================
    # 4. CURRENT HEALTH STATUS
    # ========================================================

    current_status = analyze_health_status(
        features,
        calculated,
    )

    # ========================================================
    # 5. DETAILED EXPERT EXPLANATION
    # ========================================================

    detailed_analysis = build_detailed_analysis(
        current_status,
        get_language(),
    )

    # ========================================================
    # 6. RECOMMENDATIONS
    # ========================================================

    recommendations = generate_recommendations(
        selected_goal=selected_goal,
        expert_result=expert_result,
        features=features,
        top_foods=5,
        top_exercises=5,
    )

    # ========================================================
    # 7. MLP PROBABILITIES
    # ========================================================

    probabilities = sorted(
        mlp_result["probabilities"].items(),
        key=lambda item: item[1],
        reverse=True,
    )

    probability_data = []

    for goal, probability in probabilities:
        probability_data.append(
            [goal, float(probability)]
        )

    # ========================================================
    # 8. CALCULATED FEATURES
    # ========================================================

    calculated_data = {}

    for key, value in calculated.items():
        if hasattr(value, "item"):
            calculated_data[key] = value.item()
        else:
            calculated_data[key] = value

    # ========================================================
    # 9. BUILD ANALYSIS RESULT
    # ========================================================

    analysis_result = {
        "selected_goal": selected_goal,
        "predicted_goal": mlp_result["goal"],
        "confidence": float(
            mlp_result["confidence"]
        ),
        "probabilities": probability_data,
        "calculated": calculated_data,
        "health_status": current_status,
        "detailed_analysis": detailed_analysis,
        "expert": expert_result,
        "recommendations": recommendations,
    }

    analysis_result = make_json_safe(
        analysis_result
    )

    # ========================================================
    # 10. SAVE RESULT TO SQLITE
    # ========================================================

    analysis_record = HealthAnalysis(
        user_id=current_user.id,
        selected_goal=selected_goal,
        predicted_goal=str(
            mlp_result["goal"]
        ),
        confidence=float(
            mlp_result["confidence"]
        ),
        input_data=make_json_safe(
            user_input
        ),
        result_data=analysis_result,
    )

    db.session.add(
        analysis_record
    )

    db.session.commit()

    session["analysis_id"] = (
        analysis_record.id
    )

    session.pop(
        "analysis_result",
        None,
    )

    return redirect(
        url_for("result")
    )


# ============================================================
# RESULT PAGE
# ============================================================

@app.route("/result")
@login_required
def result():
    """Display the saved analysis result."""

    analysis_id = session.get(
        "analysis_id"
    )

    if not analysis_id:
        return redirect(
            url_for("health_form")
        )

    analysis_record = db.session.get(
        HealthAnalysis,
        analysis_id,
    )

    if analysis_record is None:
        return redirect(
            url_for("health_form")
        )

    if analysis_record.user_id != current_user.id:
        abort(404)

    return render_template(
        "result.html",
        result=analysis_record.result_data,
        language=get_language(),
        translate=translate,
    )


# ============================================================
# HEALTH STATUS PAGE
# ============================================================

@app.route("/health-status")
@login_required
def health_status():
    """Display detailed current health status."""

    analysis_id = session.get(
        "analysis_id"
    )

    if not analysis_id:
        return redirect(
            url_for("health_form")
        )

    analysis_record = db.session.get(
        HealthAnalysis,
        analysis_id,
    )

    if analysis_record is None:
        return redirect(
            url_for("health_form")
        )

    if analysis_record.user_id != current_user.id:
        abort(404)

    return render_template(
        "health_status.html",
        result=analysis_record.result_data,
        language=get_language(),
        translate=translate,
    )


# ============================================================
# NEW ANALYSIS
# ============================================================

@app.route("/new-analysis")
@login_required
def new_analysis():
    """Clear previous data and start a new analysis."""

    session.pop("health_input", None)
    session.pop("analysis_result", None)
    session.pop("analysis_id", None)

    return redirect(
        url_for("health_form")
    )


# ============================================================
# USER HISTORY
# ============================================================

@app.route("/history")
@login_required
def history():
    """Display the current user's analysis history."""

    analysis_records = (
        HealthAnalysis.query
        .filter_by(user_id=current_user.id)
        .order_by(
            HealthAnalysis.created_at.desc()
        )
        .all()
    )

    return render_template(
        "history.html",
        records=analysis_records,
        language=get_language(),
        translate=translate,
    )


# ============================================================
# HISTORY DETAIL
# ============================================================

@app.route("/history/<int:analysis_id>")
@login_required
def history_detail(analysis_id):
    """Open a saved analysis belonging to the user."""

    analysis_record = db.session.get(
        HealthAnalysis,
        analysis_id,
    )

    if analysis_record is None:
        abort(404)

    if analysis_record.user_id != current_user.id:
        abort(404)

    session["analysis_id"] = (
        analysis_record.id
    )

    return redirect(
        url_for("result")
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False,
        host="127.0.0.1",
        port=5000,
    )

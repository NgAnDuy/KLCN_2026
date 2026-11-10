"""Inference bundle: current and vietnam_asia. Input: complete engineered feature rows."""
import json
from pathlib import Path
import numpy as np

GOALS = ["fitness_improvement", "healthy_lifestyle", "maintenance", "weight_gain", "weight_loss"]

def expert_predict(
    row,
    return_details=False,
    profile="current"
):

    if profile not in ("current", "vietnam_asia"):
        raise ValueError("profile must be current or vietnam_asia")

    scores = {
        goal: 0.0
        for goal in GOALS
    }

    reasons = []


    # ========================================================
    # GET FEATURES
    # ========================================================

    calorie_balance_pct = float(
        row["calorie_balance_pct"]
    )

    calorie_ratio = float(
        row["calorie_intake_ratio"]
    )

    steps = float(
        row["avg_steps_7d"]
    )

    exercise_volume = float(
        row["weekly_exercise_volume"]
    )

    sleep = float(
        row["avg_sleep_hours_7d"]
    )

    hydration = float(
        row["hydration_ratio"]
    )

    activity = str(
        row["activity_level"]
    ).strip().lower()


    # ========================================================
    # WEIGHT GAIN
    # ========================================================

    if calorie_balance_pct >= 8:

        scores["weight_gain"] += 4

        reasons.append(
            "Calorie balance >= +8%"
        )

    elif calorie_balance_pct >= 5:

        scores["weight_gain"] += 2


    if calorie_ratio >= 1.08:

        scores["weight_gain"] += 4

        reasons.append(
            "Calorie intake ratio >= 1.08"
        )

    elif calorie_ratio >= 1.05:

        scores["weight_gain"] += 2


    # ========================================================
    # WEIGHT LOSS
    # ========================================================

    if calorie_balance_pct <= -8:

        scores["weight_loss"] += 4

        reasons.append(
            "Calorie balance <= -8%"
        )

    elif calorie_balance_pct <= -5:

        scores["weight_loss"] += 2


    if calorie_ratio <= 0.92:

        scores["weight_loss"] += 4

        reasons.append(
            "Calorie intake ratio <= 0.92"
        )

    elif calorie_ratio <= 0.95:

        scores["weight_loss"] += 2


    # ========================================================
    # MAINTENANCE
    # ========================================================

    if abs(calorie_balance_pct) <= 3:

        scores["maintenance"] += 4

        reasons.append(
            "Calories are close to TDEE"
        )

    elif abs(calorie_balance_pct) <= 5:

        scores["maintenance"] += 2


    if 0.97 <= calorie_ratio <= 1.03:

        scores["maintenance"] += 3

    elif 0.95 <= calorie_ratio <= 1.05:

        scores["maintenance"] += 1


    if exercise_volume < 200:

        scores["maintenance"] += 2


    # ========================================================
    # FITNESS IMPROVEMENT
    # ========================================================

    if exercise_volume >= 500:

        scores["fitness_improvement"] += 4

        reasons.append(
            "High weekly exercise volume"
        )

    elif exercise_volume >= 350:

        scores["fitness_improvement"] += 2


    if steps >= 10000:

        scores["fitness_improvement"] += 3

    elif steps >= 7500:

        scores["fitness_improvement"] += 1


    if activity in [
        "active",
        "very active"
    ]:

        scores["fitness_improvement"] += 3

    elif activity == "moderate":

        scores["fitness_improvement"] += 1


    # ========================================================
    # HEALTHY LIFESTYLE
    # ========================================================

    if 7500 <= steps < 10000:

        scores["healthy_lifestyle"] += 2


    if 150 <= exercise_volume < 500:

        scores["healthy_lifestyle"] += 2


    if 7 <= sleep <= 9:

        scores["healthy_lifestyle"] += 2


    if 0.8 <= hydration <= 1.5:

        scores["healthy_lifestyle"] += 2


    if activity in [
        "moderate",
        "active"
    ]:

        scores["healthy_lifestyle"] += 2


    if abs(calorie_balance_pct) <= 7:

        scores["healthy_lifestyle"] += 1


    # ========================================================
    # FINAL RESULT
    # ========================================================

    # BMI thresholds: Ministry of Health, Decision 2892/QD-BYT (2022),
    # Table 4.1, printed p. 7. VA1: see XAC_MINH_NGUON_VIETNAM_ASIA.md.
    # +2/+4 and goal mapping are experimental group choices, NOT official scores.
    if profile == "vietnam_asia":
        try:
            age = float(row["age"])
            bmi = float(row["bmi"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("vietnam_asia requires valid age and BMI") from exc
        if not np.isfinite(age) or age < 18:
            raise ValueError("vietnam_asia applies to adults aged 18 or older")
        if not np.isfinite(bmi) or bmi <= 0:
            raise ValueError("BMI must be finite and positive")

        if bmi < 18.5:
            bmi_category, bmi_goal, bmi_points = "underweight", "weight_gain", 2
        elif bmi < 23:
            bmi_category, bmi_goal, bmi_points = "normal", "maintenance", 2
        elif bmi < 25:
            bmi_category, bmi_goal, bmi_points = "overweight", "weight_loss", 2
        elif bmi < 30:
            bmi_category, bmi_goal, bmi_points = "obesity I", "weight_loss", 4
        else:
            bmi_category, bmi_goal, bmi_points = "obesity II", "weight_loss", 4
        scores[bmi_goal] += bmi_points
        reasons.append(
            f"BMI {bmi:.4g}: {bmi_category} [VA1, Table 4.1, p.7]; "
            f"{bmi_goal} +{bmi_points} (experimental score)"
        )

    expert_goal = max(
        scores,
        key=scores.get
    )


    if return_details:

        return (
            expert_goal,
            scores,
            reasons
        )


    return expert_goal

def hybrid_predict(
    mlp_probabilities,
    expert_goal,
    confidence_threshold,
    label_encoder
):

    mlp_index = int(
        np.argmax(
            mlp_probabilities
        )
    )


    mlp_goal = (
        label_encoder
        .inverse_transform(
            [mlp_index]
        )[0]
    )


    mlp_confidence = float(
        mlp_probabilities[
            mlp_index
        ]
    )


    # MLP and Expert agree
    if mlp_goal == expert_goal:

        return (
            mlp_goal,
            "MLP and Expert agree"
        )


    # MLP is confident
    if mlp_confidence >= confidence_threshold:

        return (
            mlp_goal,
            "MLP confidence is high"
        )


    # MLP confidence is low
    return (
        expert_goal,
        "Expert supports low-confidence MLP"
    )

class HealthPredictor:
    def __init__(self, bundle_dir=None):
        import joblib
        from tensorflow.keras.models import load_model
        root = Path(bundle_dir) if bundle_dir is not None else Path(__file__).resolve().parent
        self.config = json.loads((root / "config.json").read_text(encoding="utf-8"))
        self.preprocessor = joblib.load(root / "preprocessor.pkl")
        self.label_encoder = joblib.load(root / "label_encoder.pkl")
        self.model = load_model(root / "health_mlp.keras", compile=False)

    def predict(self, data, profile="current"):
        import pandas as pd
        if profile not in self.config["hybrid_thresholds"]:
            raise ValueError("profile must be current or vietnam_asia")
        frame = data.copy() if isinstance(data, pd.DataFrame) else pd.DataFrame([data])
        missing = set(self.config["feature_columns"]) - set(frame.columns)
        if missing:
            raise ValueError(f"Missing engineered features: {sorted(missing)}")
        frame = frame[self.config["feature_columns"]]
        if frame.empty:
            return []
        experts = [expert_predict(row, return_details=True, profile=profile)
                   for _, row in frame.iterrows()]
        probabilities = self.model.predict(self.preprocessor.transform(frame), verbose=0)
        results = []
        threshold = self.config["hybrid_thresholds"][profile]
        for probability, (expert_goal, scores, reasons) in zip(probabilities, experts):
            index = int(np.argmax(probability))
            final_goal, reason = hybrid_predict(probability, expert_goal, threshold, self.label_encoder)
            results.append({
                "profile": profile,
                "mlp_goal": str(self.label_encoder.inverse_transform([index])[0]),
                "mlp_confidence": float(probability[index]),
                "probabilities": {str(k): float(v) for k, v in zip(self.label_encoder.classes_, probability)},
                "expert_goal": expert_goal, "expert_scores": scores,
                "expert_reasons": reasons, "threshold": threshold,
                "final_goal": str(final_goal), "decision_reason": reason,
            })
        return results

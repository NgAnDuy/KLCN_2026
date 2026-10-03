GOAL_LABELS = {
    "weight_loss": "Weight Loss",
    "weight_gain": "Weight Gain",
    "maintenance": "Maintenance",
    "fitness_improvement": "Fitness Improvement",
    "healthy_lifestyle": "Healthy Lifestyle"
}


STRONG_CONFLICTS = {
    ("weight_loss", "weight_gain"),
    ("weight_gain", "weight_loss")
}


def analyze_goal_conflict(
    selected_goal,
    predicted_goal,
    confidence,
    features
):
    row = features.iloc[0]

    bmi = float(row["bmi"])
    calorie_balance = float(
        row["calorie_balance"]
    )
    calorie_balance_pct = float(
        row["calorie_balance_pct"]
    )
    calorie_ratio = float(
        row["calorie_intake_ratio"]
    )
    steps = float(
        row["avg_steps_7d"]
    )
    sleep = float(
        row["avg_sleep_hours_7d"]
    )
    hydration = float(
        row["hydration_ratio"]
    )
    weekly_exercise = float(
        row["weekly_exercise_volume"]
    )

    reasons = []
    warnings = []
    priorities = []

    # ========================================================
    # 1. GOAL CONFLICT
    # ========================================================

    if selected_goal == predicted_goal:
        conflict_level = "NONE"

        reasons.append(
            "The selected goal matches the MLP-predicted goal."
        )

    elif (
        selected_goal,
        predicted_goal
    ) in STRONG_CONFLICTS:
        conflict_level = "HIGH"

        reasons.append(
            "The selected goal and MLP-predicted goal represent "
            "opposite weight directions."
        )

    else:
        conflict_level = "MODERATE"

        reasons.append(
            "The selected goal differs from the "
            "MLP-predicted goal."
        )

    # ========================================================
    # 2. BODY STATUS
    # ========================================================

    if bmi < 18.5:
        body_status = "LOW_BMI"

        warnings.append(
            "BMI is below the usual healthy adult range."
        )

        priorities.append(
            "NUTRITIONAL_ADEQUACY"
        )

    elif bmi < 25:
        body_status = "NORMAL_BMI"

    elif bmi < 30:
        body_status = "HIGH_BMI"

    else:
        body_status = "VERY_HIGH_BMI"

        warnings.append(
            "BMI is in a high range; weight-related "
            "recommendations should be conservative."
        )

    # ========================================================
    # 3. ENERGY STATUS
    # ========================================================

    if calorie_balance_pct < -20:
        energy_status = "LARGE_DEFICIT"

        warnings.append(
            "Current estimated calorie deficit is large."
        )

        priorities.append(
            "ENERGY_RECOVERY"
        )

    elif calorie_balance_pct < -5:
        energy_status = "MODERATE_DEFICIT"

    elif calorie_balance_pct <= 5:
        energy_status = "BALANCED"

    elif calorie_balance_pct <= 20:
        energy_status = "MODERATE_SURPLUS"

    else:
        energy_status = "LARGE_SURPLUS"

        warnings.append(
            "Current estimated calorie surplus is large."
        )

        priorities.append(
            "ENERGY_CONTROL"
        )

    # ========================================================
    # 4. STEP STATUS
    # ========================================================

    if steps < 5000:
        step_status = "LOW"

        priorities.append(
            "DAILY_MOVEMENT"
        )

    elif steps < 8000:
        step_status = "MODERATE"

    else:
        step_status = "GOOD"

    # ========================================================
    # 5. EXERCISE STATUS
    # ========================================================

    if weekly_exercise < 75:
        exercise_status = "VERY_LOW"

        priorities.append(
            "EXERCISE"
        )

    elif weekly_exercise < 150:
        exercise_status = "LOW"

        priorities.append(
            "EXERCISE"
        )

    elif weekly_exercise <= 300:
        exercise_status = "GOOD"

    else:
        exercise_status = "HIGH"

    # ========================================================
    # 6. SLEEP STATUS
    # ========================================================

    if sleep < 7:
        sleep_status = "LOW"

        priorities.append(
            "SLEEP"
        )

        warnings.append(
            "Average sleep is below 7 hours."
        )

    elif sleep <= 9:
        sleep_status = "GOOD"

    else:
        sleep_status = "HIGH"

    # ========================================================
    # 7. HYDRATION STATUS
    # ========================================================

    if hydration < 0.8:
        hydration_status = "LOW"

        priorities.append(
            "HYDRATION"
        )

        warnings.append(
            "Estimated hydration intake is below the "
            "current reference target."
        )

    elif hydration <= 1.2:
        hydration_status = "GOOD"

    else:
        hydration_status = "HIGH"

    # ========================================================
    # 8. FINAL EXPERT DIRECTION
    # ========================================================

    direction = "SUPPORT_SELECTED_GOAL"

    # --------------------------------------------------------
    # Weight loss safety
    # --------------------------------------------------------

    if (
        selected_goal == "weight_loss"
        and bmi < 18.5
    ):
        direction = "PROFESSIONAL_REVIEW"

        reasons.append(
            "Further automatic weight-loss guidance is not "
            "appropriate based on the current BMI."
        )

    elif (
        selected_goal == "weight_loss"
        and energy_status == "LARGE_DEFICIT"
    ):
        direction = "MAINTAIN_FIRST"

        reasons.append(
            "The current energy deficit is already large, so "
            "additional restriction should not be recommended."
        )

    # --------------------------------------------------------
    # Weight gain safety
    # --------------------------------------------------------

    elif (
        selected_goal == "weight_gain"
        and bmi >= 30
    ):
        direction = "PROFESSIONAL_REVIEW"

        reasons.append(
            "Automatic weight-gain guidance is not appropriate "
            "based on the current BMI."
        )

    elif (
        selected_goal == "weight_gain"
        and energy_status == "LARGE_SURPLUS"
    ):
        direction = "MAINTAIN_FIRST"

        reasons.append(
            "The current energy surplus is already large, so "
            "additional intake should not be recommended."
        )

    # --------------------------------------------------------
    # Strong MLP/User conflict
    # --------------------------------------------------------

    elif (
        conflict_level == "HIGH"
        and confidence >= 0.80
    ):
        direction = "REVIEW_GOAL"

        reasons.append(
            "There is a strong goal conflict and the MLP "
            "prediction has high confidence."
        )

    # ========================================================
    # 9. REMOVE DUPLICATES
    # ========================================================

    priorities = list(
        dict.fromkeys(priorities)
    )

    warnings = list(
        dict.fromkeys(warnings)
    )

    reasons = list(
        dict.fromkeys(reasons)
    )

    # ========================================================
    # 10. RESULT
    # ========================================================

    return {
        "selected_goal": selected_goal,
        "predicted_goal": predicted_goal,
        "mlp_confidence": confidence,

        "conflict_level": conflict_level,
        "direction": direction,

        "body_status": body_status,
        "energy_status": energy_status,
        "step_status": step_status,
        "exercise_status": exercise_status,
        "sleep_status": sleep_status,
        "hydration_status": hydration_status,

        "bmi": bmi,
        "calorie_balance": calorie_balance,
        "calorie_balance_pct": calorie_balance_pct,
        "calorie_ratio": calorie_ratio,

        "priorities": priorities,
        "reasons": reasons,
        "warnings": warnings
    }
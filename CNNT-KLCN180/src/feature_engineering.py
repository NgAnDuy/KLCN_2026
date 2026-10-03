import pandas as pd


ACTIVITY_FACTORS = {
    "sedentary": 1.20,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very active": 1.90
}


def create_health_features(
    age,
    gender,
    height_cm,
    weight_kg,
    activity_level,
    calories_consumed,
    avg_steps_7d,
    avg_sleep_hours_7d,
    water_intake_l,
    avg_exercise_minutes_7d,
    exercise_sessions_7d,
    avg_calories_burned_7d
):
    height_m = height_cm / 100.0

    bmi = weight_kg / (height_m ** 2)

    if gender.lower() == "male":
        bmr = (
            10 * weight_kg
            + 6.25 * height_cm
            - 5 * age
            + 5
        )
    else:
        bmr = (
            10 * weight_kg
            + 6.25 * height_cm
            - 5 * age
            - 161
        )

    activity_factor = ACTIVITY_FACTORS[
        activity_level.lower()
    ]

    tdee = bmr * activity_factor

    calorie_balance = calories_consumed - tdee

    calorie_balance_pct = (
        calorie_balance / tdee * 100
    )

    calorie_intake_ratio = (
        calories_consumed / tdee
    )

    weekly_exercise_volume = (
        avg_exercise_minutes_7d
        * exercise_sessions_7d
    )

    if exercise_sessions_7d > 0:
        exercise_minutes_per_session = (
            avg_exercise_minutes_7d
            / exercise_sessions_7d
        )
    else:
        exercise_minutes_per_session = 0.0

    steps_per_kg = (
        avg_steps_7d / weight_kg
    )

    sleep_deviation_from_8h = (
        avg_sleep_hours_7d - 8
    )

    hydration_requirement = (
        weight_kg * 0.033
    )

    hydration_ratio = (
        water_intake_l
        / hydration_requirement
    )

    tdee_per_kg = (
        tdee / weight_kg
    )

    bmr_tdee_ratio = (
        bmr / tdee
    )

    if avg_exercise_minutes_7d > 0:
        calories_burned_per_exercise_min = (
            avg_calories_burned_7d
            / avg_exercise_minutes_7d
        )
    else:
        calories_burned_per_exercise_min = 0.0

    features = pd.DataFrame([{
        "age": age,
        "gender": gender,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "bmi": bmi,
        "bmr": bmr,
        "activity_level": activity_level,
        "tdee": tdee,
        "calories_consumed": calories_consumed,
        "avg_steps_7d": avg_steps_7d,
        "avg_sleep_hours_7d": avg_sleep_hours_7d,
        "water_intake_l": water_intake_l,
        "avg_exercise_minutes_7d":
            avg_exercise_minutes_7d,
        "exercise_sessions_7d":
            exercise_sessions_7d,
        "avg_calories_burned_7d":
            avg_calories_burned_7d,
        "calorie_balance":
            calorie_balance,
        "calorie_balance_pct":
            calorie_balance_pct,
        "weekly_exercise_volume":
            weekly_exercise_volume,
        "exercise_minutes_per_session":
            exercise_minutes_per_session,
        "steps_per_kg":
            steps_per_kg,
        "sleep_deviation_from_8h":
            sleep_deviation_from_8h,
        "hydration_ratio":
            hydration_ratio,
        "tdee_per_kg":
            tdee_per_kg,
        "bmr_tdee_ratio":
            bmr_tdee_ratio,
        "calorie_intake_ratio":
            calorie_intake_ratio,
        "calories_burned_per_exercise_min":
            calories_burned_per_exercise_min
    }])

    calculated = {
        "bmi": bmi,
        "bmr": bmr,
        "tdee": tdee,
        "calorie_balance": calorie_balance,
        "calorie_balance_pct":
            calorie_balance_pct,
        "calorie_intake_ratio":
            calorie_intake_ratio,
        "hydration_ratio":
            hydration_ratio,
        "weekly_exercise_volume":
            weekly_exercise_volume,
        "exercise_minutes_per_session":
            exercise_minutes_per_session,
        "steps_per_kg":
            steps_per_kg,
        "sleep_deviation":
            sleep_deviation_from_8h
    }

    return features, calculated
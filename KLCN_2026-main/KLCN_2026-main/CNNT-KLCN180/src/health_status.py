"""Analyze the user's current health indicators."""


def _create_item(
    key,
    value,
    unit,
    code,
    status,
    vi_stable,
    vi_warning,
    en_stable,
    en_warning
):
    """Create one health status item."""
    return {
        "key": key,
        "value": value,
        "unit": unit,
        "code": code,
        "status": status,
        "vi_message": (
            vi_stable
            if status == "stable"
            else vi_warning
        ),
        "en_message": (
            en_stable
            if status == "stable"
            else en_warning
        )
    }


def analyze_health_status(
    features,
    calculated
):
    """Analyze current health indicators."""

    # ========================================================
    # GET CURRENT USER ROW
    # ========================================================

    row = features.iloc[0]

    items = []

    # ========================================================
    # 1. BMI STATUS
    # ========================================================

    bmi = float(
        calculated["bmi"]
    )

    if bmi < 18.5:
        bmi_code = "UNDERWEIGHT"
        bmi_status = "warning"

    elif bmi < 25.0:
        bmi_code = "NORMAL_BMI"
        bmi_status = "stable"

    elif bmi < 30.0:
        bmi_code = "OVERWEIGHT"
        bmi_status = "warning"

    else:
        bmi_code = "OBESE"
        bmi_status = "warning"

    items.append(
        _create_item(
            "bmi",
            round(
                bmi,
                2
            ),
            "",
            bmi_code,
            bmi_status,
            (
                "BMI hiện nằm trong khoảng thường được xem là "
                "phù hợp đối với người trưởng thành."
            ),
            (
                "BMI hiện nằm ngoài khoảng thông thường. "
                "Nên cân nhắc mục tiêu cân nặng một cách "
                "thận trọng."
            ),
            (
                "BMI is currently within the commonly used "
                "adult reference range."
            ),
            (
                "BMI is outside the commonly used adult "
                "reference range. Weight goals should be "
                "considered carefully."
            )
        )
    )

    # ========================================================
    # 2. ENERGY STATUS
    # ========================================================

    calorie_balance = float(
        calculated[
            "calorie_balance"
        ]
    )

    tdee = max(
        float(
            calculated["tdee"]
        ),
        1.0
    )

    balance_percentage = (
        calorie_balance
        / tdee
        * 100
    )

    if balance_percentage < -20:
        energy_code = "LARGE_DEFICIT"
        energy_status = "warning"

    elif balance_percentage < -10:
        energy_code = "CALORIE_DEFICIT"
        energy_status = "warning"

    elif balance_percentage <= 10:
        energy_code = "BALANCED_ENERGY"
        energy_status = "stable"

    elif balance_percentage <= 20:
        energy_code = "CALORIE_SURPLUS"
        energy_status = "warning"

    else:
        energy_code = "LARGE_SURPLUS"
        energy_status = "warning"

    items.append(
        _create_item(
            "energy",
            round(
                calorie_balance
            ),
            "kcal",
            energy_code,
            energy_status,
            (
                "Năng lượng nạp vào hiện khá gần với nhu cầu "
                "năng lượng ước tính của cơ thể."
            ),
            (
                "Năng lượng nạp vào và nhu cầu ước tính đang "
                "có chênh lệch đáng chú ý."
            ),
            (
                "Current calorie intake is relatively close "
                "to estimated energy needs."
            ),
            (
                "There is a notable difference between "
                "current calorie intake and estimated "
                "energy needs."
            )
        )
    )

    # ========================================================
    # 3. SLEEP STATUS
    # ========================================================

    sleep = float(
        row[
            "avg_sleep_hours_7d"
        ]
    )

    if 7.0 <= sleep <= 9.0:
        sleep_code = "NORMAL_SLEEP"
        sleep_status = "stable"

    elif sleep < 7.0:
        sleep_code = "LOW_SLEEP"
        sleep_status = "warning"

    else:
        sleep_code = "HIGH_SLEEP"
        sleep_status = "warning"

    items.append(
        _create_item(
            "sleep",
            round(
                sleep,
                1
            ),
            "h",
            sleep_code,
            sleep_status,
            (
                "Thời lượng ngủ trung bình hiện nằm trong "
                "khoảng mục tiêu mà hệ thống sử dụng."
            ),
            (
                "Thời lượng ngủ hiện chưa nằm trong khoảng "
                "mục tiêu 7–9 giờ mà hệ thống sử dụng."
            ),
            (
                "Average sleep duration is within the "
                "target range used by the system."
            ),
            (
                "Average sleep duration is outside the "
                "7–9 hour target range used by the system."
            )
        )
    )

    # ========================================================
    # 4. HYDRATION STATUS
    # ========================================================

    hydration_ratio = float(
        row[
            "hydration_ratio"
        ]
    )

    if 0.8 <= hydration_ratio <= 1.3:
        hydration_code = "NORMAL_HYDRATION"
        hydration_status = "stable"

    elif hydration_ratio < 0.8:
        hydration_code = "LOW_HYDRATION"
        hydration_status = "warning"

    else:
        hydration_code = "HIGH_HYDRATION"
        hydration_status = "warning"

    items.append(
        _create_item(
            "hydration",
            round(
                hydration_ratio,
                2
            ),
            "",
            hydration_code,
            hydration_status,
            (
                "Lượng nước hiện tương đối phù hợp với mức "
                "tham chiếu của hệ thống."
            ),
            (
                "Lượng nước hiện lệch khỏi mức tham chiếu "
                "của hệ thống và nên được cân nhắc điều chỉnh."
            ),
            (
                "Current hydration is reasonably aligned "
                "with the system reference level."
            ),
            (
                "Current hydration differs from the system "
                "reference level and may need adjustment."
            )
        )
    )

    # ========================================================
    # 5. EXERCISE STATUS
    # ========================================================

    weekly_exercise = float(
        row[
            "weekly_exercise_volume"
        ]
    )

    if weekly_exercise < 150:
        exercise_code = "LOW_EXERCISE"
        exercise_status = "warning"

    elif weekly_exercise <= 300:
        exercise_code = "GOOD_EXERCISE"
        exercise_status = "stable"

    else:
        exercise_code = "HIGH_EXERCISE"
        exercise_status = "stable"

    items.append(
        _create_item(
            "exercise",
            round(
                weekly_exercise
            ),
            "min/week",
            exercise_code,
            exercise_status,
            (
                "Khối lượng vận động hàng tuần hiện đạt mức "
                "mà hệ thống xem là tương đối tốt."
            ),
            (
                "Khối lượng vận động hàng tuần hiện còn thấp. "
                "Có thể cân nhắc tăng dần hoạt động phù hợp."
            ),
            (
                "Weekly exercise volume is currently at a "
                "level the system considers reasonably good."
            ),
            (
                "Weekly exercise volume is currently low. "
                "A gradual increase may be considered."
            )
        )
    )

    # ========================================================
    # 6. STEP STATUS
    # ========================================================

    steps = float(
        row[
            "avg_steps_7d"
        ]
    )

    if steps < 5000:
        step_code = "LOW_STEPS"
        step_status = "warning"

    elif steps < 8000:
        step_code = "MODERATE_STEPS"
        step_status = "stable"

    else:
        step_code = "GOOD_STEPS"
        step_status = "stable"

    items.append(
        _create_item(
            "steps",
            round(
                steps
            ),
            "steps/day",
            step_code,
            step_status,
            (
                "Mức đi bộ hàng ngày hiện tương đối phù hợp "
                "với mức tham chiếu của hệ thống."
            ),
            (
                "Số bước trung bình mỗi ngày hiện còn thấp. "
                "Có thể cân nhắc tăng vận động hàng ngày "
                "một cách từ từ."
            ),
            (
                "Daily step count is currently at a "
                "reasonable level based on the system "
                "reference."
            ),
            (
                "Average daily step count is currently low. "
                "A gradual increase in daily movement may "
                "be considered."
            )
        )
    )

    # ========================================================
    # 7. SPLIT STABLE / WARNING
    # ========================================================

    stable_items = [
        item
        for item in items
        if item["status"] == "stable"
    ]

    warning_items = [
        item
        for item in items
        if item["status"] == "warning"
    ]

    # ========================================================
    # 8. RESULT
    # ========================================================

    return {
        "items": items,
        "stable": stable_items,
        "warnings": warning_items,
        "stable_count": len(
            stable_items
        ),
        "warning_count": len(
            warning_items
        )
    }
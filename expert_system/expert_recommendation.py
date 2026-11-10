import math

from .expert_system.rule_engine import evaluate_rules


# ============================================================
# GOAL LABELS
# ============================================================

GOAL_LABELS = {
    "weight_loss": "Weight Loss",
    "weight_gain": "Weight Gain",
    "maintenance": "Maintenance",
    "fitness_improvement": "Fitness Improvement",
    "healthy_lifestyle": "Healthy Lifestyle",
}

STRONG_CONFLICTS = {
    ("weight_loss", "weight_gain"),
    ("weight_gain", "weight_loss"),
}


# ============================================================
# MEDICAL SAFETY
# ============================================================

MEDICAL_BLOCKS = {
    "diabetes": {
        "aggressive_calorie_deficit",
    },
    "hypertension": {
        "high_sodium_plan",
    },
    "kidney_disease": {
        "automatic_high_protein_plan",
        "automatic_high_water_plan",
    },
}

SOURCE_URLS = {
    "CDC_BMI": (
        "https://www.cdc.gov/bmi/adult-calculator/"
        "bmi-categories.html"
    ),
    "WHO_PA_2020": (
        "https://www.who.int/publications/i/item/"
        "9789240015128"
    ),
    "WHO_DIET": (
        "https://www.who.int/news-room/fact-sheets/"
        "detail/healthy-diet"
    ),
    "ADA_2026": (
        "https://professional.diabetes.org/"
        "standards-of-care"
    ),
    "KDIGO_2024": (
        "https://kdigo.org/guidelines/"
        "ckd-evaluation-and-management/"
    ),
    "FDA_ALLERGY": (
        "https://www.fda.gov/food/"
        "buy-store-serve-safe-food/"
        "food-allergies-what-you-need-know"
    ),
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _number(value):
    """
    Chuyển giá trị thành số.
    Giá trị thiếu hoặc không hợp lệ -> None.
    """
    try:
        if value is None or value == "":
            return None

        result = float(value)

        return result if math.isfinite(result) else None

    except (TypeError, ValueError):
        return None


def _get_feature(features, name):
    """
    Hỗ trợ DataFrame một dòng hoặc dict.
    """
    try:
        if hasattr(features, "iloc"):
            return _number(features.iloc[0].get(name))

        return _number(features.get(name))

    except (
        IndexError,
        KeyError,
        AttributeError,
        TypeError,
    ):
        return None


def _unique(items):
    return list(dict.fromkeys(items))


def _add_rule(
    rules,
    rule_id,
    category,
    action,
    message,
    priority,
    source_id=None,
    blocked_actions=None,
    evidence=None,
):
    rules.append({
        "rule_id": rule_id,
        "category": category,
        "action": action,
        "message": message,
        "priority": priority,
        "source_id": source_id,
        "source_url": SOURCE_URLS.get(source_id),
        "blocked_actions": blocked_actions or [],
        "evidence": evidence or {},
        "review_status": "PENDING_CLINICAL_REVIEW",
    })


# ============================================================
# EXPERT GOAL RECOMMENDATION
# ============================================================

def recommend_health_goal(features, age=None):
    """
    Xác định mục tiêu sức khỏe theo quy tắc đơn giản hóa.

    goal = mục tiêu sức khỏe phù hợp,
    KHÔNG phải tình trạng năng lượng hiện tại.

    Chỉ sử dụng ngưỡng BMI người lớn khi tuổi >= 20.

    Quy tắc này phục vụ mô hình thử nghiệm của đồ án,
    không thay thế đánh giá y khoa cá nhân.
    """

    bmi = _get_feature(features, "bmi")
    steps = _get_feature(features, "avg_steps_7d")
    sleep = _get_feature(features, "avg_sleep_hours_7d")
    hydration = _get_feature(features, "hydration_ratio")

    weekly_exercise = _get_feature(
        features,
        "weekly_exercise_volume",
    )

    if age is None:
        age = _get_feature(features, "age")

    age = _number(age)

    # Không áp dụng ngưỡng BMI người lớn khi thiếu tuổi
    # hoặc người dùng dưới 20 tuổi.
    if age is None or age < 20:
        return None

    if bmi is None:
        return None

    # BMI thấp: ưu tiên mục tiêu tăng cân
    if bmi < 18.5:
        return "weight_gain"

    # BMI cao: ưu tiên mục tiêu giảm cân
    if bmi >= 25:
        return "weight_loss"

    # BMI bình thường: ưu tiên cải thiện vận động
    if (
        (steps is not None and steps < 5000)
        or (
            weekly_exercise is not None
            and weekly_exercise < 150
        )
    ):
        return "fitness_improvement"

    # BMI bình thường: cải thiện sinh hoạt
    if (
        (sleep is not None and sleep < 7)
        or (
            hydration is not None
            and hydration < 0.8
        )
    ):
        return "healthy_lifestyle"

    # BMI bình thường, các chỉ số tương đối ổn
    if (
        steps is None
        or weekly_exercise is None
        or sleep is None
        or hydration is None
    ):
        return None

    return "maintenance"


# ============================================================
# MAIN EXPERT ANALYSIS
# ============================================================

def analyze_goal_conflict(
    selected_goal,
    predicted_goal,
    confidence,
    features,
    medical_conditions=None,
    allergies=None,
    recommendations=None,
    age=None,
):
    """
    Phân tích mục tiêu người dùng và dự đoán MLP.

    selected_goal:
        Mục tiêu người dùng tự chọn.

    predicted_goal:
        Mục tiêu do MLP dự đoán.

    recommended_goal:
        Mục tiêu do hệ chuyên gia đề xuất.

    direction:
        Hướng xử lý mục tiêu.

    Giữ tương thích với lời gọi cũ gồm 4 tham số.

    Các quy tắc y khoa chỉ phục vụ sàng lọc và
    cảnh báo an toàn, không phải chẩn đoán.
    """

    medical_conditions = set(medical_conditions or [])
    allergies = set(allergies or [])
    recommendations = recommendations or []

    # --------------------------------------------------------
    # 1. LẤY ĐẶC TRƯNG
    # --------------------------------------------------------

    bmi = _get_feature(features, "bmi")

    calorie_balance = _get_feature(
        features,
        "calorie_balance",
    )

    calorie_balance_pct = _get_feature(
        features,
        "calorie_balance_pct",
    )

    calorie_ratio = _get_feature(
        features,
        "calorie_intake_ratio",
    )

    steps = _get_feature(
        features,
        "avg_steps_7d",
    )

    sleep = _get_feature(
        features,
        "avg_sleep_hours_7d",
    )

    hydration = _get_feature(
        features,
        "hydration_ratio",
    )

    weekly_exercise = _get_feature(
        features,
        "weekly_exercise_volume",
    )

    confidence = _number(confidence)

    if age is None:
        age = _get_feature(features, "age")

    age = _number(age)

    # --------------------------------------------------------
    # 2. XÁC ĐỊNH MỤC TIÊU EXPERT
    # --------------------------------------------------------

    recommended_goal = recommend_health_goal(
        features=features,
        age=age,
    )

    reasons = []
    warnings = []
    priorities = []
    triggered_rules = []
    blocked_actions = set()

    if recommended_goal is None:
        goal_assessment = "INSUFFICIENT_INFORMATION"

    elif selected_goal == recommended_goal:
        goal_assessment = "ALIGNED"

    else:
        goal_assessment = "NEEDS_REVIEW"

    # --------------------------------------------------------
    # 3. SO SÁNH MỤC TIÊU NGƯỜI DÙNG VÀ MLP
    # --------------------------------------------------------

    if selected_goal == predicted_goal:
        conflict_level = "NONE"

        reasons.append(
            "The selected goal matches the "
            "MLP-predicted goal."
        )

    elif (
        selected_goal,
        predicted_goal,
    ) in STRONG_CONFLICTS:

        conflict_level = "HIGH"

        reasons.append(
            "The selected goal and MLP-predicted goal "
            "represent opposite weight directions."
        )

    else:
        conflict_level = "MODERATE"

        reasons.append(
            "The selected goal differs from the "
            "MLP-predicted goal."
        )

    # --------------------------------------------------------
    # 4. SO SÁNH VỚI MỤC TIÊU EXPERT
    # --------------------------------------------------------

    if recommended_goal is not None:

        reasons.append(
            "Expert system recommends goal: "
            f"{GOAL_LABELS[recommended_goal]}."
        )

        if selected_goal != recommended_goal:
            warnings.append(
                "The selected goal differs from the "
                "expert-recommended health goal."
            )

        if predicted_goal != recommended_goal:
            reasons.append(
                "The MLP prediction differs from the "
                "expert-recommended health goal."
            )

    # --------------------------------------------------------
    # 5. BMI
    # --------------------------------------------------------

    adult_bmi = (
        bmi is not None
        and age is not None
        and age >= 20
    )

    if not adult_bmi:
        body_status = "UNKNOWN"

    elif bmi < 18.5:
        body_status = "LOW_BMI"

        warnings.append(
            "BMI is below the usual healthy adult range."
        )

        priorities.append("NUTRITIONAL_ADEQUACY")

        _add_rule(
            triggered_rules,
            "HLT-01",
            "health",
            "INFORM",
            "Adult BMI is below 18.5.",
            40,
            "CDC_BMI",
            evidence={"bmi": bmi},
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

        _add_rule(
            triggered_rules,
            "HLT-02",
            "health",
            "INFORM",
            "Adult BMI is 30 or higher.",
            40,
            "CDC_BMI",
            evidence={"bmi": bmi},
        )

    # --------------------------------------------------------
    # 6. NĂNG LƯỢNG
    # --------------------------------------------------------

    if calorie_balance_pct is None:
        energy_status = "UNKNOWN"

    elif calorie_balance_pct < -20:
        energy_status = "LARGE_DEFICIT"

        warnings.append(
            "Current estimated calorie deficit is large."
        )

        priorities.append("ENERGY_RECOVERY")

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

        priorities.append("ENERGY_CONTROL")

    # Các ngưỡng +/-5%, +/-20% là quy tắc nội bộ.
    # Không dùng calorie_balance để trực tiếp đổi goal.

    # --------------------------------------------------------
    # 7. BƯỚC CHÂN
    # --------------------------------------------------------

    if steps is None:
        step_status = "UNKNOWN"

    elif steps < 5000:
        step_status = "LOW"
        priorities.append("DAILY_MOVEMENT")

    elif steps < 8000:
        step_status = "MODERATE"

    else:
        step_status = "GOOD"

    # --------------------------------------------------------
    # 8. VẬN ĐỘNG
    # --------------------------------------------------------

    if weekly_exercise is None:
        exercise_status = "UNKNOWN"

    elif weekly_exercise < 75:
        exercise_status = "VERY_LOW"
        priorities.append("EXERCISE")

    elif weekly_exercise < 150:
        exercise_status = "LOW"
        priorities.append("EXERCISE")

    elif weekly_exercise <= 300:
        exercise_status = "GOOD"

    else:
        exercise_status = "HIGH"

    # weekly_exercise_volume cần thực sự biểu diễn
    # số phút vận động tương đương mỗi tuần.

    # --------------------------------------------------------
    # 9. GIẤC NGỦ
    # --------------------------------------------------------

    if sleep is None:
        sleep_status = "UNKNOWN"

    elif sleep < 7:
        sleep_status = "LOW"

        priorities.append("SLEEP")

        warnings.append(
            "Average sleep is below 7 hours."
        )

    elif sleep <= 9:
        sleep_status = "GOOD"

    else:
        sleep_status = "HIGH"

    # --------------------------------------------------------
    # 10. NƯỚC UỐNG
    # --------------------------------------------------------

    if hydration is None:
        hydration_status = "UNKNOWN"

    elif hydration < 0.8:
        hydration_status = "LOW"

        priorities.append("HYDRATION")

        warnings.append(
            "Estimated hydration intake is below "
            "the current reference target."
        )

    elif hydration <= 1.2:
        hydration_status = "GOOD"

    else:
        hydration_status = "HIGH"

    # --------------------------------------------------------
    # 11. HƯỚNG XỬ LÝ MỤC TIÊU
    # --------------------------------------------------------

    direction = "SUPPORT_SELECTED_GOAL"

    if (
        selected_goal == "weight_loss"
        and adult_bmi
        and bmi < 18.5
    ):
        direction = "PROFESSIONAL_REVIEW"

        reasons.append(
            "Automatic weight-loss guidance should be "
            "reviewed because adult BMI is below 18.5."
        )

        blocked_actions.add(
            "automatic_calorie_deficit"
        )

        blocked_actions.add(
            "aggressive_calorie_deficit"
        )

        _add_rule(
            triggered_rules,
            "GOAL-01",
            "goal",
            "REVIEW",
            "Weight loss is selected with low adult BMI.",
            90,
            "CDC_BMI",
            [
                "automatic_calorie_deficit",
                "aggressive_calorie_deficit",
            ],
            {"bmi": bmi, "goal": selected_goal},
        )

    elif (
        selected_goal == "weight_loss"
        and energy_status == "LARGE_DEFICIT"
    ):
        direction = "MAINTAIN_FIRST"

        reasons.append(
            "The estimated energy deficit is already large."
        )

        blocked_actions.add(
            "aggressive_calorie_deficit"
        )

    elif (
        selected_goal == "weight_gain"
        and adult_bmi
        and bmi >= 30
    ):
        direction = "PROFESSIONAL_REVIEW"

        reasons.append(
            "Automatic weight-gain guidance requires review "
            "in the context of current adult BMI."
        )

        blocked_actions.add(
            "automatic_calorie_surplus"
        )

        _add_rule(
            triggered_rules,
            "GOAL-02",
            "goal",
            "REVIEW",
            "Weight gain is selected with adult BMI >= 30.",
            80,
            "CDC_BMI",
            ["automatic_calorie_surplus"],
            {"bmi": bmi, "goal": selected_goal},
        )

    elif (
        selected_goal == "weight_gain"
        and energy_status == "LARGE_SURPLUS"
    ):
        direction = "MAINTAIN_FIRST"

        reasons.append(
            "The estimated energy surplus is already large."
        )

        blocked_actions.add(
            "automatic_calorie_surplus"
        )

    elif (
        conflict_level == "HIGH"
        and confidence is not None
        and confidence >= 0.80
    ):
        direction = "REVIEW_GOAL"

        reasons.append(
            "The selected and predicted goals "
            "strongly differ."
        )

    # --------------------------------------------------------
    # 12. ĐÁNH GIÁ SỰ PHÙ HỢP CỦA MỤC TIÊU
    # --------------------------------------------------------

    if (
        recommended_goal is not None
        and selected_goal != recommended_goal
        and direction == "SUPPORT_SELECTED_GOAL"
    ):
        direction = "REVIEW_GOAL"

        reasons.append(
            "The selected goal should be reviewed "
            "against the expert-recommended goal."
        )

    # --------------------------------------------------------
    # 13. LUẬT BỆNH LÝ NỀN
    # --------------------------------------------------------

    if "diabetes" in medical_conditions:

        priorities.append("MEDICAL_REVIEW")

        _add_rule(
            triggered_rules,
            "MED-01",
            "medical",
            "REVIEW",
            "Diabetes was reported. Major dietary and "
            "exercise changes may require treatment review.",
            90,
            "ADA_2026",
            evidence={"condition": "diabetes"},
        )

        warnings.append(
            "Diabetes was reported; recommendations "
            "should consider current treatment."
        )

        if selected_goal == "weight_loss":

            blocked_actions.add(
                "aggressive_calorie_deficit"
            )

            _add_rule(
                triggered_rules,
                "MED-02",
                "medical",
                "REVIEW",
                "Do not automatically prescribe an aggressive "
                "calorie deficit without treatment review.",
                95,
                "ADA_2026",
                ["aggressive_calorie_deficit"],
                {"condition": "diabetes"},
            )

    if "hypertension" in medical_conditions:

        priorities.append("MEDICAL_REVIEW")

        blocked_actions.add(
            "high_sodium_plan"
        )

        _add_rule(
            triggered_rules,
            "MED-03",
            "medical",
            "REVIEW",
            "Review sodium content in dietary recommendations.",
            85,
            "WHO_DIET",
            ["high_sodium_plan"],
            {"condition": "hypertension"},
        )

        warnings.append(
            "Hypertension was reported; dietary sodium "
            "recommendations need attention."
        )

    if "kidney_disease" in medical_conditions:

        priorities.append("MEDICAL_REVIEW")

        blocked_actions.update({
            "automatic_high_protein_plan",
            "automatic_high_water_plan",
        })

        _add_rule(
            triggered_rules,
            "MED-05",
            "medical",
            "REVIEW",
            "Protein recommendations need individualized "
            "review in chronic kidney disease.",
            95,
            "KDIGO_2024",
            ["automatic_high_protein_plan"],
            {"condition": "kidney_disease"},
        )

        _add_rule(
            triggered_rules,
            "MED-06",
            "medical",
            "REVIEW",
            "Do not automatically increase fluid targets "
            "without knowing clinical circumstances.",
            95,
            "KDIGO_2024",
            ["automatic_high_water_plan"],
            {"condition": "kidney_disease"},
        )

        warnings.append(
            "Chronic kidney disease was reported; automatic "
            "high-protein and high-fluid plans are withheld."
        )

    # --------------------------------------------------------
    # 14. LUẬT DỊ ỨNG
    # --------------------------------------------------------

    for rec in recommendations:

        if rec.get("type") != "food":
            continue

        action_id = rec.get("action_id")

        if not action_id:
            continue

        food_allergens = rec.get("allergens")

        if allergies and food_allergens is None:

            blocked_actions.add(action_id)

            _add_rule(
                triggered_rules,
                "ALG-01",
                "allergy",
                "REVIEW",
                "Food allergen information is missing.",
                100,
                "FDA_ALLERGY",
                [action_id],
                {"food": rec.get("name")},
            )

        elif allergies:

            matched = allergies.intersection(
                set(food_allergens or [])
            )

            if matched:

                blocked_actions.add(action_id)

                _add_rule(
                    triggered_rules,
                    "ALG-02",
                    "allergy",
                    "EXCLUDE",
                    "Food contains a reported allergen.",
                    100,
                    "FDA_ALLERGY",
                    [action_id],
                    {
                        "food": rec.get("name"),
                        "allergens": sorted(matched),
                    },
                )

    # --------------------------------------------------------
    # 15. GIẢI QUYẾT XUNG ĐỘT
    # --------------------------------------------------------

    allowed_recommendations = [
        rec
        for rec in recommendations
        if rec.get("action_id") not in blocked_actions
    ]

    requires_review = any(
        rule["category"] == "medical"
        and rule["action"] == "REVIEW"
        for rule in triggered_rules
    )

    if requires_review:
        direction = "PROFESSIONAL_REVIEW"

    # --------------------------------------------------------
    # 16. TỔNG HỢP KẾT QUẢ
    # --------------------------------------------------------

    triggered_rules.sort(
        key=lambda rule: rule["priority"],
        reverse=True,
    )

    priorities = _unique(priorities)
    warnings = _unique(warnings)
    reasons = _unique(reasons)

    return {
        # Các khóa cũ: giữ nguyên
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
        "warnings": warnings,

        # Mục tiêu sức khỏe theo expert
        "recommended_goal": recommended_goal,
        "goal_assessment": goal_assessment,

        "mlp_expert_agreement": (
            predicted_goal == recommended_goal
            if recommended_goal is not None
            else None
        ),

        # Các khóa an toàn cũ
        "medical_conditions": sorted(medical_conditions),
        "allergies": sorted(allergies),
        "triggered_rules": triggered_rules,
        "blocked_actions": sorted(blocked_actions),
        "allowed_recommendations": allowed_recommendations,
        "requires_professional_review": requires_review,
    }


# ============================================================
# DETAILED ANALYSIS
# ============================================================

def build_detailed_analysis(health_status, language="en"):
    """
    Giữ nguyên giao diện hàm và cấu trúc trả về cũ.
    """

    stable_items = []
    warning_items = []

    message_key = (
        "vi_message"
        if language == "vi"
        else "en_message"
    )

    for item in health_status.get("stable", []):

        stable_items.append({
            "code": item.get("code", ""),
            "value": item.get("value", ""),
            "unit": item.get("unit", ""),
            "message": item.get(message_key, ""),
        })

    for item in health_status.get("warnings", []):

        warning_items.append({
            "code": item.get("code", ""),
            "value": item.get("value", ""),
            "unit": item.get("unit", ""),
            "message": item.get(message_key, ""),
        })

    stable_count = health_status.get(
        "stable_count",
        len(stable_items),
    )

    warning_count = health_status.get(
        "warning_count",
        len(warning_items),
    )

    if language == "vi":

        if warning_count == 0:

            summary = (
                "Các chỉ số được hệ thống theo dõi hiện tương đối "
                "ổn định. Bạn có thể tiếp tục duy trì những thói "
                "quen đang phù hợp."
            )

        elif stable_count == 0:

            summary = (
                "Nhiều chỉ số hiện tại cần được cân nhắc điều "
                "chỉnh. Bạn nên ưu tiên cải thiện từng yếu tố "
                "một thay vì thay đổi quá nhiều cùng lúc."
            )

        else:

            summary = (
                f"Hiện có {stable_count} chỉ số tương đối ổn định "
                f"và {warning_count} chỉ số cần được cân nhắc "
                "cải thiện."
            )

    else:

        if warning_count == 0:

            summary = (
                "The indicators monitored by the system are "
                "currently relatively stable. You can continue "
                "maintaining the habits that are working well."
            )

        elif stable_count == 0:

            summary = (
                "Several current indicators may need adjustment. "
                "Consider improving them gradually rather than "
                "making many major changes at once."
            )

        else:

            summary = (
                f"There are currently {stable_count} stable "
                f"indicators and {warning_count} indicators "
                "that may need attention."
            )

    return {
        "summary": summary,
        "stable": stable_items,
        "warnings": warning_items,
    }

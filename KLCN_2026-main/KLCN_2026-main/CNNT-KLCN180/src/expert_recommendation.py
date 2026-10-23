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


def build_detailed_analysis(
    health_status,
    language="en"
):
    """Build detailed explanations from current health status."""
    stable_items = []
    warning_items = []

    message_key = (
        "vi_message"
        if language == "vi"
        else "en_message"
    )

    # ========================================================
    # 1. STABLE INDICATORS
    # ========================================================

    for item in health_status.get("stable", []):
        stable_items.append(
            {
                "code": item.get(
                    "code",
                    ""
                ),
                "value": item.get(
                    "value",
                    ""
                ),
                "unit": item.get(
                    "unit",
                    ""
                ),
                "message": item.get(
                    message_key,
                    ""
                )
            }
        )

    # ========================================================
    # 2. WARNING INDICATORS
    # ========================================================

    for item in health_status.get("warnings", []):
        warning_items.append(
            {
                "code": item.get(
                    "code",
                    ""
                ),
                "value": item.get(
                    "value",
                    ""
                ),
                "unit": item.get(
                    "unit",
                    ""
                ),
                "message": item.get(
                    message_key,
                    ""
                )
            }
        )

    # ========================================================
    # 3. COUNTS
    # ========================================================

    stable_count = health_status.get(
        "stable_count",
        len(stable_items)
    )

    warning_count = health_status.get(
        "warning_count",
        len(warning_items)
    )

    # ========================================================
    # 4. OVERALL ANALYSIS
    # ========================================================

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

    # ========================================================
    # 5. RESULT
    # ========================================================

    return {
        "summary": summary,
        "stable": stable_items,
        "warnings": warning_items
    }


# ========================================================
# 6. WEEKLY MEAL & WORKOUT PLAN GENERATOR (7 DAYS)
# ========================================================

def generate_weekly_plan(goal="healthy_lifestyle"):
    """
    Tạo lộ trình ăn uống và tập luyện 7 ngày riêng biệt, 
    không trùng lặp món ăn và tự động điều chỉnh theo mục tiêu.
    """
    # Hệ số điều chỉnh calo dựa theo mục tiêu từ GOAL_LABELS
    if goal == "weight_loss":
        cal_offset = -100
        portion_note = " (khẩu phần giảm tinh bột)"
    elif goal == "weight_gain":
        cal_offset = 150
        portion_note = " (tăng cường đạm & tinh bột)"
    else:
        cal_offset = 0
        portion_note = ""

    # Dữ liệu 7 ngày riêng biệt - Đảm bảo không trùng lặp món ăn
    base_plan = [
        {
            "day_number": 1,
            "meals": [
                {"time": "Sáng", "food": "Yến mạch nấu sữa tươi không đường & chuối", "calories": 350 + cal_offset},
                {"time": "Trưa", "food": "Cơm gạo lứt, ức gà áp chảo, bông cải xanh luộc" + portion_note, "calories": 550 + cal_offset},
                {"time": "Tối", "food": "Salad cá ngừ đại dương trộn dầu oliu", "calories": 350 + cal_offset}
            ],
            "workouts": [
                {"name": "Chạy bộ bền (Cardio)", "duration": "30 phút"},
                {"name": "Giãn cơ toàn thân", "duration": "10 phút"}
            ]
        },
        {
            "day_number": 2,
            "meals": [
                {"time": "Sáng", "food": "Bánh mì nguyên cám kẹp trứng ốp la & bơ", "calories": 400 + cal_offset},
                {"time": "Trưa", "food": "Khoai lang luộc, thịt bò xào măng tây" + portion_note, "calories": 600 + cal_offset},
                {"time": "Tối", "food": "Cá hồi nướng măng tây & súp bí đỏ", "calories": 450 + cal_offset}
            ],
            "workouts": [
                {"name": "Tập tạ thân trên (Upper Body Strength)", "duration": "40 phút"},
                {"name": "Plank & Gập bụng", "duration": "10 phút"}
            ]
        },
        {
            "day_number": 3,
            "meals": [
                {"time": "Sáng", "food": "Phở gà (bỏ da, ít bánh phở, nhiều giá đỗ)", "calories": 420 + cal_offset},
                {"time": "Trưa", "food": "Bún gạo lứt trộn thịt heo nạc & rau củ" + portion_note, "calories": 520 + cal_offset},
                {"time": "Tối", "food": "Đậu hũ non sốt nấm đông cô & cải thìa luộc", "calories": 320 + cal_offset}
            ],
            "workouts": [
                {"name": "Đạp xe hoặc Nhảy dây (HIIT)", "duration": "25 phút"},
                {"name": "Bài tập linh hoạt khớp", "duration": "15 phút"}
            ]
        },
        {
            "day_number": 4,
            "meals": [
                {"time": "Sáng", "food": "Sữa chua Hy Lạp trộn hạt điều, hạnh nhân & táo", "calories": 330 + cal_offset},
                {"time": "Trưa", "food": "Cơm gạo lứt, tôm rim nhạt, canh bí đao" + portion_note, "calories": 530 + cal_offset},
                {"time": "Tối", "food": "Ức gà xé phay trộn hành tây, rau răm & dưa leo", "calories": 360 + cal_offset}
            ],
            "workouts": [
                {"name": "Tập thân dưới: Squat & Lunges (Lower Body)", "duration": "40 phút"},
                {"name": "Đi bộ thả lỏng", "duration": "15 phút"}
            ]
        },
        {
            "day_number": 5,
            "meals": [
                {"time": "Sáng", "food": "Khoai lang mật hấp & 2 quả trứng gà luộc", "calories": 380 + cal_offset},
                {"time": "Trưa", "food": "Mì Ý nguyên cám sốt bò bằm cà chua" + portion_note, "calories": 580 + cal_offset},
                {"time": "Tối", "food": "Cá diêu hồng hấp cuốn bánh tráng rau sống", "calories": 400 + cal_offset}
            ],
            "workouts": [
                {"name": "Bài tập toàn thân (Full-body Circuit)", "duration": "35 phút"},
                {"name": "Giãn cơ lưng và vai", "duration": "10 phút"}
            ]
        },
        {
            "day_number": 6,
            "meals": [
                {"time": "Sáng", "food": "Sinh tố bơ chuối pha sữa hạt (ít đường)", "calories": 360 + cal_offset},
                {"time": "Trưa", "food": "Cơm trắng/gạo lứt, cá thu sốt cà, rau muống luộc" + portion_note, "calories": 560 + cal_offset},
                {"time": "Tối", "food": "Súp ức gà nấm hương & ngô ngọt", "calories": 340 + cal_offset}
            ],
            "workouts": [
                {"name": "Bơi lội hoặc Cầu lông / Thể thao ngoài trời", "duration": "45 phút"}
            ]
        },
        {
            "day_number": 7,
            "meals": [
                {"time": "Sáng", "food": "Bún bò Huế (chọn thịt bắp bò nạc, ít nước béo)", "calories": 450 + cal_offset},
                {"time": "Trưa", "food": "Thịt thăn heo áp chảo, salad trộn dầu giấm, 1 củ khoai" + portion_note, "calories": 540 + cal_offset},
                {"time": "Tối", "food": "Canh rong biển thịt bằm & đậu phụ luộc", "calories": 310 + cal_offset}
            ],
            "workouts": [
                {"name": "Yoga phục hồi hoặc Đi bộ nhẹ nhàng (Active Recovery)", "duration": "30 phút"}
            ]
        }
    ]

    return base_plan
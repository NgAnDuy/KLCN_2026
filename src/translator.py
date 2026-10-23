"""Translation utilities for the health recommendation system."""


TRANSLATIONS = {
    "vi": {
        # Goals
        "weight_loss": "Giảm cân",
        "weight_gain": "Tăng cân",
        "maintenance": "Duy trì cân nặng",
        "fitness_improvement": "Cải thiện thể chất",
        "healthy_lifestyle": "Lối sống lành mạnh",

        # BMI
        "UNDERWEIGHT": "Thiếu cân",
        "NORMAL_BMI": "BMI bình thường",
        "OVERWEIGHT": "Thừa cân",
        "OBESE": "Béo phì",

        # Energy
        "LARGE_DEFICIT": "Thâm hụt năng lượng cao",
        "CALORIE_DEFICIT": "Thâm hụt năng lượng",
        "BALANCED_ENERGY": "Năng lượng cân bằng",
        "CALORIE_SURPLUS": "Dư thừa năng lượng",
        "LARGE_SURPLUS": "Dư thừa năng lượng cao",

        # Exercise
        "LOW_EXERCISE": "Vận động thấp",
        "MODERATE_EXERCISE": "Vận động vừa phải",
        "GOOD_EXERCISE": "Mức vận động tốt",
        "HIGH_EXERCISE": "Mức vận động cao",

        # Sleep
        "LOW_SLEEP": "Ngủ chưa đủ",
        "NORMAL_SLEEP": "Giấc ngủ ổn định",
        "HIGH_SLEEP": "Thời gian ngủ cao",

        # Hydration
        "LOW_HYDRATION": "Uống chưa đủ nước",
        "NORMAL_HYDRATION": "Lượng nước ổn định",
        "HIGH_HYDRATION": "Lượng nước cao",

        # Generic
        "stable": "Ổn định",
        "warning": "Cần cân nhắc",
        "low": "Thấp",
        "moderate": "Trung bình",
        "high": "Cao",
        "none": "Không có",

        # Conflict
        "NO_CONFLICT": "Không xung đột",
        "LOW_CONFLICT": "Xung đột thấp",
        "MODERATE_CONFLICT": "Xung đột trung bình",
        "HIGH_CONFLICT": "Xung đột cao",
        "CRITICAL_CONFLICT": "Xung đột nghiêm trọng",

        # Directions
        "FOLLOW_GOAL": "Có thể tiếp tục mục tiêu",
        "ADJUST_GOAL": "Nên điều chỉnh mục tiêu",
        "REVIEW_GOAL": "Nên xem xét lại mục tiêu",
        "MAINTAIN": "Nên duy trì",

        # Day names
        "monday": "Thứ Hai",
        "tuesday": "Thứ Ba",
        "wednesday": "Thứ Tư",
        "thursday": "Thứ Năm",
        "friday": "Thứ Sáu",
        "saturday": "Thứ Bảy",
        "sunday": "Chủ Nhật",

        # Meal slots
        "breakfast": "Bữa sáng",
        "lunch": "Bữa trưa",
        "dinner": "Bữa tối",
        "snack": "Bữa phụ",

        # Exercise focus
        "cardio": "Cardio",
        "strength_upper": "Kháng lực thân trên",
        "strength_lower": "Kháng lực thân dưới",
        "flexibility": "Linh hoạt & Giãn cơ",
        "full_body": "Toàn thân",
        "recovery": "Nghỉ ngơi phục hồi",

        # Recovery tips
        "PRIORITIZE_SLEEP": "Ưu tiên ngủ đủ 7-8 giờ",
        "INCREASE_HYDRATION": "Tăng cường uống nước",
        "LIGHT_STRETCHING": "Giãn cơ nhẹ nhàng",

        # Split labels
        "3_DAYS_PER_WEEK": "3 buổi tập / tuần",
        "4_DAYS_PER_WEEK": "4 buổi tập / tuần",
        "5_DAYS_PER_WEEK": "5 buổi tập / tuần",

        # Difficulty
        "beginner": "Người mới",
        "intermediate": "Trung bình",
        "advanced": "Nâng cao",
    },

    "en": {
        # Goals
        "weight_loss": "Weight Loss",
        "weight_gain": "Weight Gain",
        "maintenance": "Weight Maintenance",
        "fitness_improvement": "Fitness Improvement",
        "healthy_lifestyle": "Healthy Lifestyle",

        # BMI
        "UNDERWEIGHT": "Underweight",
        "NORMAL_BMI": "Normal BMI",
        "OVERWEIGHT": "Overweight",
        "OBESE": "Obese",

        # Energy
        "LARGE_DEFICIT": "Large Calorie Deficit",
        "CALORIE_DEFICIT": "Calorie Deficit",
        "BALANCED_ENERGY": "Balanced Energy",
        "CALORIE_SURPLUS": "Calorie Surplus",
        "LARGE_SURPLUS": "Large Calorie Surplus",

        # Exercise
        "LOW_EXERCISE": "Low Exercise",
        "MODERATE_EXERCISE": "Moderate Exercise",
        "GOOD_EXERCISE": "Good Exercise Level",
        "HIGH_EXERCISE": "High Exercise Level",

        # Sleep
        "LOW_SLEEP": "Insufficient Sleep",
        "NORMAL_SLEEP": "Stable Sleep",
        "HIGH_SLEEP": "High Sleep Duration",

        # Hydration
        "LOW_HYDRATION": "Low Hydration",
        "NORMAL_HYDRATION": "Stable Hydration",
        "HIGH_HYDRATION": "High Hydration",

        # Generic
        "stable": "Stable",
        "warning": "Needs Attention",
        "low": "Low",
        "moderate": "Moderate",
        "high": "High",
        "none": "None",

        # Conflict
        "NO_CONFLICT": "No Conflict",
        "LOW_CONFLICT": "Low Conflict",
        "MODERATE_CONFLICT": "Moderate Conflict",
        "HIGH_CONFLICT": "High Conflict",
        "CRITICAL_CONFLICT": "Critical Conflict",

        # Directions
        "FOLLOW_GOAL": "Goal Can Be Continued",
        "ADJUST_GOAL": "Goal Should Be Adjusted",
        "REVIEW_GOAL": "Goal Should Be Reviewed",
        "MAINTAIN": "Maintain Current Direction",

        # Day names
        "monday": "Monday",
        "tuesday": "Tuesday",
        "wednesday": "Wednesday",
        "thursday": "Thursday",
        "friday": "Friday",
        "saturday": "Saturday",
        "sunday": "Sunday",

        # Meal slots
        "breakfast": "Breakfast",
        "lunch": "Lunch",
        "dinner": "Dinner",
        "snack": "Snack",

        # Exercise focus
        "cardio": "Cardio",
        "strength_upper": "Upper Body Strength",
        "strength_lower": "Lower Body Strength",
        "flexibility": "Flexibility & Stretching",
        "full_body": "Full Body",
        "recovery": "Rest & Recovery",

        # Recovery tips
        "PRIORITIZE_SLEEP": "Prioritize 7-8 hours of sleep",
        "INCREASE_HYDRATION": "Increase water intake",
        "LIGHT_STRETCHING": "Light stretching recommended",

        # Split labels
        "3_DAYS_PER_WEEK": "3 sessions / week",
        "4_DAYS_PER_WEEK": "4 sessions / week",
        "5_DAYS_PER_WEEK": "5 sessions / week",

        # Difficulty
        "beginner": "Beginner",
        "intermediate": "Intermediate",
        "advanced": "Advanced",
    }
}


def normalize_key(value):
    """Normalize a value before translation."""
    if value is None:
        return ""

    return str(value).strip()


def format_label(value):
    """Convert internal labels into readable labels."""
    if value is None:
        return ""

    text = str(value).strip()
    text = text.replace("_", " ")

    return text.title()


def translate(value, language="en"):
    """Translate an internal value for presentation."""
    key = normalize_key(value)

    if not key:
        return ""

    language_data = TRANSLATIONS.get(
        language,
        TRANSLATIONS["en"]
    )

    if key in language_data:
        return language_data[key]

    upper_key = key.upper()

    if upper_key in language_data:
        return language_data[upper_key]

    lower_key = key.lower()

    if lower_key in language_data:
        return language_data[lower_key]

    return format_label(key)
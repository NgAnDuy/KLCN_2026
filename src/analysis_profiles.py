"""Reference profiles used by the Flask analysis flow."""

CURRENT = "current"
VIETNAM_ASIA = "vietnam_asia"
VALID_PROFILES = frozenset({CURRENT, VIETNAM_ASIA})


def validate_profile(profile):
    if profile not in VALID_PROFILES:
        raise ValueError("Invalid analysis profile.")
    return profile


def classify_bmi(bmi, profile=CURRENT):
    """Classify adult BMI without rounding values at category boundaries."""
    validate_profile(profile)
    if bmi < 18.5:
        return "UNDERWEIGHT"
    if profile == VIETNAM_ASIA:
        if bmi < 23:
            return "NORMAL_BMI"
        if bmi < 25:
            return "OVERWEIGHT"
        if bmi < 30:
            return "OBESE_I"
        return "OBESE_II"
    if bmi < 25:
        return "NORMAL_BMI"
    if bmi < 30:
        return "OVERWEIGHT"
    return "OBESE"


def asia_bmi_goal_points(category):
    """Experimental +2/+4 points documented by the project team."""
    mapping = {
        "UNDERWEIGHT": ("weight_gain", 2),
        "NORMAL_BMI": ("maintenance", 2),
        "OVERWEIGHT": ("weight_loss", 2),
        "OBESE_I": ("weight_loss", 4),
        "OBESE_II": ("weight_loss", 4),
    }
    goal, points = mapping[category]
    return {goal: points}

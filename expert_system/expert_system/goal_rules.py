
from .knowledge_base import Finding


def evaluate_goal_rules(data, goal):
    findings = []

    age = data.get("age")
    bmi = data.get("bmi")

    if age is None or age < 20 or bmi is None:
        return findings

    if goal == "weight_loss" and bmi < 18.5:
        findings.append(Finding(
            rule_id="GOAL-01",
            category="goal",
            action="REVIEW",
            message="Người dùng thuộc nhóm BMI thiếu cân nhưng lựa chọn giảm cân. Cần đánh giá mục tiêu trước khi đề xuất.",
            priority=80,
            source_id="CDC_BMI",
            blocked_actions=["automatic_calorie_deficit"],
            evidence={"goal": goal, "bmi": bmi}
        ))

    if goal == "weight_gain" and bmi >= 30:
        findings.append(Finding(
            rule_id="GOAL-02",
            category="goal",
            action="REVIEW",
            message="Mục tiêu tăng cân cần được xem xét thêm trong bối cảnh BMI hiện tại.",
            priority=60,
            source_id="CDC_BMI",
            evidence={"goal": goal, "bmi": bmi}
        ))

    return findings

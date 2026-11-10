
from .health_rules import evaluate_health_rules
from .goal_rules import evaluate_goal_rules
from .medical_rules import evaluate_medical_rules
from .allergy_rules import evaluate_allergy_rules


def evaluate_rules(data, recommendations=None):
    recommendations = recommendations or []

    findings = []

    findings.extend(evaluate_health_rules(data))
    findings.extend(
        evaluate_goal_rules(data, data.get("goal"))
    )
    findings.extend(evaluate_medical_rules(data, recommendations))
    findings.extend(
        evaluate_allergy_rules(data, recommendations)
    )

    # Xác định các hành động không được tự động đề xuất.
    blocked_actions = set()

    for finding in findings:
        blocked_actions.update(finding.blocked_actions)

    # Loại khuyến nghị xung đột.
    allowed_recommendations = [
        rec for rec in recommendations
        if rec.get("action_id") not in blocked_actions
    ]

    # Sắp xếp các kết luận theo độ ưu tiên.
    findings.sort(
        key=lambda finding: finding.priority,
        reverse=True
    )

    # Loại các kết luận trùng mã và dữ kiện.
    unique_findings = []
    seen = set()

    for finding in findings:
        key = (
            finding.rule_id,
            repr(sorted(finding.evidence.items()))
        )

        if key not in seen:
            seen.add(key)
            unique_findings.append(finding)

    return {
        "findings": [
            finding.to_dict()
            for finding in unique_findings
        ],
        "recommendations": allowed_recommendations,
        "blocked_actions": sorted(blocked_actions),
        "triggered_rule_ids": [
            finding.rule_id
            for finding in unique_findings
        ]
    }

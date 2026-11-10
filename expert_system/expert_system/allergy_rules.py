
from .knowledge_base import Finding


SUPPORTED_ALLERGENS = {
    "milk", "egg", "fish", "shellfish",
    "tree_nuts", "peanut", "wheat",
    "soy", "sesame"
}


def evaluate_allergy_rules(data, recommendations):
    findings = []
    allergies = set(data.get("allergies") or [])

    for rec in recommendations:
        if rec.get("type") != "food":
            continue

        action_id = rec.get("action_id")
        if not action_id:
            continue

        allergens = rec.get("allergens")

        # Không xác nhận an toàn nếu không biết dị nguyên.
        if allergies and allergens is None:
            findings.append(Finding(
                rule_id="ALG-01",
                category="allergy",
                action="REVIEW",
                message="Chưa có thông tin dị nguyên của thực phẩm. Cần kiểm tra thành phần trước khi sử dụng.",
                priority=100,
                source_id="FDA_ALLERGY",
                blocked_actions=[action_id],
                evidence={"food": rec.get("name")}
            ))
            continue

        known_allergens = set(allergens or [])
        conflicts = allergies.intersection(known_allergens)

        if conflicts:
            findings.append(Finding(
                rule_id="ALG-02",
                category="allergy",
                action="EXCLUDE",
                message="Thực phẩm chứa dị nguyên mà người dùng đã khai báo.",
                priority=100,
                source_id="FDA_ALLERGY",
                blocked_actions=[action_id],
                evidence={
                    "food": rec.get("name"),
                    "matched_allergens": sorted(conflicts)
                }
            ))

    return findings

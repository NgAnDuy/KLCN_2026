
import math

from .knowledge_base import Finding


# Project screening cutoff per food item, not a clinical daily prescription.
# WHO/KDIGO discuss daily sodium intake; this per-item cutoff is a
# conservative implementation choice pending dietitian review.
SODIUM_SCREEN_MG_PER_ITEM = 500


def evaluate_medical_rules(data, recommendations=None):
    findings = []
    conditions = set(data.get("medical_conditions") or [])
    goal = data.get("goal")

    if "diabetes" in conditions:
        findings.append(Finding(
            rule_id="MED-01",
            category="medical",
            action="REVIEW",
            message="Người dùng khai báo đái tháo đường. Các thay đổi lớn về chế độ ăn và vận động cần xét đến phương pháp điều trị hiện tại.",
            priority=90,
            source_id="ADA_2026",
            evidence={"condition": "diabetes"}
        ))

        if goal == "weight_loss":
            findings.append(Finding(
                rule_id="MED-02",
                category="medical",
                action="REVIEW",
                message="Không tự động áp dụng chế độ giảm năng lượng mạnh khi chưa đánh giá điều trị và nguy cơ hạ đường huyết.",
                priority=95,
                source_id="ADA_2026",
                blocked_actions=["aggressive_calorie_deficit"],
                evidence={"condition": "diabetes", "goal": goal}
            ))

    if "hypertension" in conditions:
        findings.append(Finding(
            rule_id="MED-03",
            category="medical",
            action="INFORM",
            message="Người dùng khai báo tăng huyết áp. Cần lưu ý lượng natri trong các khuyến nghị ăn uống.",
            priority=70,
            source_id="WHO_DIET",
            evidence={"condition": "hypertension"}
        ))

        findings.append(Finding(
            rule_id="MED-04",
            category="medical",
            action="REVIEW",
            message="Không tự động khuyến nghị chế độ ăn nhiều natri.",
            priority=85,
            source_id="WHO_DIET",
            blocked_actions=["high_sodium_plan"],
            evidence={"condition": "hypertension"}
        ))

    if "kidney_disease" in conditions:
        findings.append(Finding(
            rule_id="MED-05",
            category="medical",
            action="REVIEW",
            message="Người dùng khai báo bệnh thận mạn. Nhu cầu protein cần được cá nhân hóa theo tình trạng bệnh và điều trị.",
            priority=95,
            source_id="KDIGO_2024",
            blocked_actions=["automatic_high_protein_plan"],
            evidence={"condition": "kidney_disease"}
        ))

        findings.append(Finding(
            rule_id="MED-06",
            category="medical",
            action="REVIEW",
            message="Không tự động đưa ra mục tiêu uống nhiều nước khi chưa biết tình trạng chức năng thận và chỉ định điều trị.",
            priority=95,
            source_id="KDIGO_2024",
            blocked_actions=["automatic_high_water_plan"],
            evidence={"condition": "kidney_disease"}
        ))

    sodium_conditions = conditions.intersection({"hypertension", "kidney_disease"})
    if sodium_conditions:
        source_id = "KDIGO_2024" if "kidney_disease" in conditions else "WHO_DIET"
        for rec in recommendations or []:
            if rec.get("type") != "food" or not rec.get("action_id"):
                continue
            try:
                sodium = float(rec.get("sodium_mg"))
                if not math.isfinite(sodium) or sodium < 0:
                    sodium = None
            except (TypeError, ValueError):
                sodium = None

            if sodium is None:
                findings.append(Finding(
                    rule_id="MED-07", category="medical", action="REVIEW",
                    message="Chưa có số natri đáng tin cậy cho món này; không tự động đề xuất khi có bệnh thận hoặc tăng huyết áp.",
                    priority=100, source_id=source_id,
                    blocked_actions=[rec["action_id"]],
                    evidence={"food": rec.get("name"), "sodium_mg": None},
                ))
            elif sodium > SODIUM_SCREEN_MG_PER_ITEM:
                findings.append(Finding(
                    rule_id="MED-08", category="medical", action="EXCLUDE",
                    message="Món vượt ngưỡng natri sàng lọc trên một khẩu phần của đồ án.",
                    priority=100, source_id=source_id,
                    blocked_actions=[rec["action_id"]],
                    evidence={
                        "food": rec.get("name"), "sodium_mg": sodium,
                        "project_cutoff_mg_per_item": SODIUM_SCREEN_MG_PER_ITEM,
                    },
                ))

    return findings

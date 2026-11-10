
from .knowledge_base import Finding


def evaluate_health_rules(data):
    findings = []

    age = data.get("age")
    bmi = data.get("bmi")
    sleep = data.get("sleep_hours")
    activity = data.get("activity_minutes_week")

    # BMI chỉ áp dụng ngưỡng người trưởng thành.
    if age is not None and age >= 20 and bmi is not None:
        if bmi < 18.5:
            findings.append(Finding(
                rule_id="HLT-01",
                category="health",
                action="INFORM",
                message="BMI thuộc nhóm thiếu cân theo phân loại BMI người trưởng thành.",
                priority=40,
                source_id="CDC_BMI",
                evidence={"bmi": bmi}
            ))

        elif bmi >= 25:
            findings.append(Finding(
                rule_id="HLT-02",
                category="health",
                action="INFORM",
                message="BMI từ 25 trở lên theo phân loại BMI người trưởng thành; cần xem xét thêm các chỉ số khác.",
                priority=40,
                source_id="CDC_BMI",
                evidence={"bmi": bmi}
            ))

    # Khuyến cáo vận động áp dụng cho người trưởng thành.
    if age is not None and age >= 18 and activity is not None:
        if activity < 150:
            findings.append(Finding(
                rule_id="HLT-03",
                category="health",
                action="SUGGEST",
                message="Thời lượng vận động aerobic mức vừa được ghi nhận dưới 150 phút mỗi tuần.",
                priority=30,
                source_id="WHO_PA_2020",
                evidence={"activity_minutes_week": activity}
            ))

    # Chỉ ghi nhận thời gian ngủ; không kết luận bệnh.
    if sleep is not None and sleep < 7 and age is not None and age >= 18:
        findings.append(Finding(
            rule_id="HLT-04",
            category="health",
            action="INFORM",
            message="Thời gian ngủ được ghi nhận dưới 7 giờ mỗi đêm; nên đánh giá thêm chất lượng giấc ngủ.",
            priority=25,
            evidence={"sleep_hours": sleep}
        ))

    return findings

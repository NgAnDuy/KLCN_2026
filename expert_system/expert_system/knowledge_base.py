
from dataclasses import dataclass, field
from typing import Any

SOURCES = {
    "WHO_PA_2020": {
        "organization": "WHO",
        "document": "WHO Guidelines on Physical Activity and Sedentary Behaviour",
        "year": 2020,
        "url": "https://www.who.int/publications/i/item/9789240015128"
    },
    "WHO_DIET": {
        "organization": "WHO",
        "document": "Healthy Diet",
        "url": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet"
    },
    "CDC_BMI": {
        "organization": "CDC",
        "document": "Adult BMI Categories",
        "url": "https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html"
    },
    "ADA_2026": {
        "organization": "ADA",
        "document": "Standards of Care in Diabetes—2026",
        "year": 2026,
        "url": "https://professional.diabetes.org/standards-of-care"
    },
    "KDIGO_2024": {
        "organization": "KDIGO",
        "document": "2024 CKD Guideline",
        "year": 2024,
        "url": "https://kdigo.org/guidelines/ckd-evaluation-and-management/"
    },
    "FDA_ALLERGY": {
        "organization": "FDA",
        "document": "Food Allergies: What You Need to Know",
        "url": "https://www.fda.gov/food/buy-store-serve-safe-food/food-allergies-what-you-need-know"
    }
}


@dataclass
class Finding:
    rule_id: str
    category: str
    action: str
    message: str
    priority: int
    source_id: str = ""
    blocked_actions: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)
    review_status: str = "PENDING_CLINICAL_REVIEW"

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "category": self.category,
            "action": self.action,
            "message": self.message,
            "priority": self.priority,
            "source": SOURCES.get(self.source_id),
            "blocked_actions": self.blocked_actions,
            "evidence": self.evidence,
            "review_status": self.review_status
        }

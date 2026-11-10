"""Adapt food rows to the supplied expert rules before ranking dishes."""

from collections import Counter

import pandas as pd

from expert_system import evaluate_rules
from expert_system.expert_system.allergy_rules import SUPPORTED_ALLERGENS


def parse_allergens(value):
    """Return None when allergen data is missing or cannot be interpreted."""
    if pd.isna(value):
        return None
    tokens = {part.strip().lower() for part in str(value).split(",")}
    if not tokens or tokens.intersection({"unknown", "", "nan"}):
        return None
    if tokens == {"none"}:
        return []
    # The older CSV uses "gluten" where the form asks about wheat.
    if "gluten" in tokens:
        tokens.remove("gluten")
        tokens.add("wheat")
    if not tokens.issubset(SUPPORTED_ALLERGENS):
        return None
    return sorted(tokens)


def screen_food_candidates(food_data, medical_conditions=(), allergies=()):
    """Exclude flagged foods; return data and a compact screening report."""
    conditions = set(medical_conditions or ())
    allergies = set(allergies or ())
    if not conditions and not allergies:
        return food_data.copy(), {
            "excluded_count": 0, "remaining_count": len(food_data),
            "rule_counts": {},
        }

    candidates = []
    for _, food in food_data.iterrows():
        candidates.append({
            "type": "food",
            "action_id": str(food["food_id"]),
            "name": str(food["food_name"]),
            "sodium_mg": pd.to_numeric(food["sodium_mg"], errors="coerce"),
            "allergens": parse_allergens(food["allergens"]),
        })
    evaluation = evaluate_rules({
        "medical_conditions": sorted(conditions),
        "allergies": sorted(allergies),
    }, candidates)
    allowed_ids = {rec["action_id"] for rec in evaluation["recommendations"]}
    remaining = food_data[
        food_data["food_id"].astype(str).isin(allowed_ids)
    ].copy()
    counts = Counter(
        finding["rule_id"] for finding in evaluation["findings"]
        if finding["rule_id"] in {"MED-07", "MED-08", "ALG-01", "ALG-02"}
    )
    return remaining, {
        "excluded_count": len(food_data) - len(remaining),
        "remaining_count": len(remaining),
        "rule_counts": dict(counts),
    }

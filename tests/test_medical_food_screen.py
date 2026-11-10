import unittest

import pandas as pd

from expert_system import evaluate_rules
from src.food_recommender import FoodRecommender
from src.medical_food_screen import parse_allergens, screen_food_candidates


class MedicalFoodScreenTests(unittest.TestCase):
    def setUp(self):
        self.foods = pd.DataFrame([
            {"food_id": "LOW", "food_name": "Low sodium", "sodium_mg": 200, "allergens": "none"},
            {"food_id": "HIGH", "food_name": "High sodium", "sodium_mg": 1326, "allergens": "none"},
            {"food_id": "MISSING", "food_name": "Unknown sodium", "sodium_mg": None, "allergens": "unknown"},
            {"food_id": "FISH", "food_name": "Fish dish", "sodium_mg": 250, "allergens": "fish"},
        ])

    def test_kidney_disease_excludes_high_and_missing_sodium(self):
        remaining, report = screen_food_candidates(
            self.foods, medical_conditions=["kidney_disease"]
        )
        self.assertEqual(set(remaining.food_id), {"LOW", "FISH"})
        self.assertEqual(report["rule_counts"]["MED-07"], 1)
        self.assertEqual(report["rule_counts"]["MED-08"], 1)

    def test_allergy_excludes_matching_and_unknown_allergens(self):
        remaining, report = screen_food_candidates(
            self.foods, allergies=["fish"]
        )
        self.assertEqual(set(remaining.food_id), {"LOW", "HIGH"})
        self.assertEqual(report["rule_counts"]["ALG-01"], 1)
        self.assertEqual(report["rule_counts"]["ALG-02"], 1)
        self.assertEqual(parse_allergens("gluten"), ["wheat"])

    def test_real_pho_is_not_recommended_for_kidney_sodium_screen(self):
        recommender = FoodRecommender()
        foods = recommender.recommend(
            "maintenance",
            {"direction": "SUPPORT_SELECTED_GOAL", "energy_status": "BALANCED"},
            medical_conditions=["kidney_disease"],
        )
        self.assertTrue(foods)
        self.assertTrue(all(pd.notna(food["sodium_mg"]) and food["sodium_mg"] <= 500 for food in foods))
        self.assertNotIn("F151", {food["food_id"] for food in foods})

    def test_supplied_rules_report_kidney_review(self):
        result = evaluate_rules({"medical_conditions": ["kidney_disease"]})
        self.assertIn("MED-05", result["triggered_rule_ids"])
        self.assertIn("MED-06", result["triggered_rule_ids"])


if __name__ == "__main__":
    unittest.main()

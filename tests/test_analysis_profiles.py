import unittest
import json
from pathlib import Path

import pandas as pd

from src.analysis_profiles import (
    asia_bmi_goal_points, classify_bmi, validate_profile,
)
from src.expert_recommendation import analyze_goal_conflict
from src.feature_engineering import create_health_features
from src.predictor import _load_inference_module


class AnalysisProfileTests(unittest.TestCase):
    def test_current_keeps_existing_bmi_boundaries(self):
        self.assertEqual(classify_bmi(23, "current"), "NORMAL_BMI")
        self.assertEqual(classify_bmi(25, "current"), "OVERWEIGHT")
        self.assertEqual(classify_bmi(30, "current"), "OBESE")

    def test_vietnam_asia_boundaries_and_experimental_points(self):
        cases = (
            (18.49, "UNDERWEIGHT", {"weight_gain": 2}),
            (18.5, "NORMAL_BMI", {"maintenance": 2}),
            (22.99, "NORMAL_BMI", {"maintenance": 2}),
            (23, "OVERWEIGHT", {"weight_loss": 2}),
            (25, "OBESE_I", {"weight_loss": 4}),
            (30, "OBESE_II", {"weight_loss": 4}),
        )
        for bmi, expected_category, expected_points in cases:
            with self.subTest(bmi=bmi):
                category = classify_bmi(bmi, "vietnam_asia")
                self.assertEqual(category, expected_category)
                self.assertEqual(asia_bmi_goal_points(category), expected_points)

    def test_invalid_profile_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_profile("unknown")

    def test_asian_profile_changes_bmi_review_at_23(self):
        features = pd.DataFrame([{
            "bmi": 23.5,
            "calorie_balance": 0,
            "calorie_balance_pct": 0,
            "calorie_intake_ratio": 1,
            "avg_steps_7d": 7500,
            "avg_sleep_hours_7d": 8,
            "hydration_ratio": 1,
            "weekly_exercise_volume": 150,
        }])
        kwargs = dict(
            selected_goal="weight_gain", predicted_goal="maintenance",
            confidence=0.5, features=features,
        )
        current = analyze_goal_conflict(**kwargs, profile="current")
        asia = analyze_goal_conflict(**kwargs, profile="vietnam_asia")
        self.assertEqual(current["body_status"], "NORMAL_BMI")
        self.assertEqual(current["direction"], "SUPPORT_SELECTED_GOAL")
        self.assertEqual(asia["body_status"], "HIGH_BMI")
        self.assertEqual(asia["direction"], "REVIEW_GOAL")
        self.assertEqual(asia["bmi_goal_points"], {"weight_loss": 2})

    def test_goal_conflict_levels_for_report_cases(self):
        features = pd.DataFrame([{
            "bmi": 22,
            "calorie_balance": 0,
            "calorie_balance_pct": 0,
            "calorie_intake_ratio": 1,
            "avg_steps_7d": 7500,
            "avg_sleep_hours_7d": 8,
            "hydration_ratio": 1,
            "weekly_exercise_volume": 150,
        }])
        cases = (
            ("weight_loss", "weight_loss", "NONE"),
            ("maintenance", "fitness_improvement", "MODERATE"),
            ("healthy_lifestyle", "maintenance", "MODERATE"),
            ("weight_gain", "weight_loss", "HIGH"),
            ("weight_loss", "weight_gain", "HIGH"),
        )
        for selected, predicted, expected in cases:
            with self.subTest(selected=selected, predicted=predicted):
                result = analyze_goal_conflict(
                    selected_goal=selected, predicted_goal=predicted,
                    confidence=0.9, features=features,
                )
                self.assertEqual(result["conflict_level"], expected)

    def test_exported_expert_adds_bmi_points_only_for_asia(self):
        features, _ = create_health_features(
            age=30, gender="Female", height_cm=170, weight_kg=68,
            activity_level="Moderate", calories_consumed=2100,
            avg_steps_7d=7000, avg_sleep_hours_7d=8, water_intake_l=2,
            avg_exercise_minutes_7d=30, exercise_sessions_7d=3,
            avg_calories_burned_7d=200,
        )
        module = _load_inference_module()
        row = features.iloc[0]
        config = json.loads(
            (Path(__file__).resolve().parents[1] / "models" / "config.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(set(config["feature_columns"]), set(features.columns))
        _, current_scores, _ = module.expert_predict(
            row, return_details=True, profile="current"
        )
        _, asia_scores, asia_reasons = module.expert_predict(
            row, return_details=True, profile="vietnam_asia"
        )
        self.assertEqual(
            asia_scores["weight_loss"], current_scores["weight_loss"] + 2
        )
        self.assertTrue(any("experimental score" in reason for reason in asia_reasons))


if __name__ == "__main__":
    unittest.main()

import unittest

from src.food_portions import load_food_portions
from src.food_recommender import FoodRecommender
from src.weekly_meal_planner import WeeklyMealPlanner


EXPERT = {"direction": "MAINTAIN", "energy_status": "BALANCED"}


class FoodPortionTests(unittest.TestCase):
    def test_pho_serving_matches_source_breakdown(self):
        portion = load_food_portions()["F151"]
        amounts = {
            ingredient["name_vi"]: (ingredient["quantity"], ingredient["unit"])
            for ingredient in portion["ingredients"]
        }
        self.assertEqual(amounts["Bánh phở"], (140, "g"))
        self.assertEqual(amounts["Thịt bò"], (55, "g"))
        self.assertEqual(amounts["Nước dùng"], (370, "ml"))

    def test_recommendations_include_documented_serving(self):
        recommender = FoodRecommender()
        for goal in (
            "maintenance", "weight_loss", "weight_gain",
            "fitness_improvement", "healthy_lifestyle",
        ):
            with self.subTest(goal=goal):
                foods = recommender.recommend(goal, EXPERT)
                sourced = [food for food in foods if "portion" in food]
                self.assertTrue(sourced)
                self.assertTrue(sourced[0]["portion"]["source_url"].startswith("https://"))

    def test_weekly_plan_keeps_totals_when_using_complete_dish(self):
        plan = WeeklyMealPlanner().generate(
            "maintenance", EXPERT, {"tdee": 2000, "bmr": 1400}
        )
        breakfast = plan["days"][0]["meals"]["breakfast"]
        self.assertTrue(breakfast["has_portion"])
        self.assertIn("portion", breakfast["items"][0])
        self.assertEqual(
            breakfast["total_calories"],
            round(sum(item["calories"] for item in breakfast["items"])),
        )
        portion_ids = [
            meal["items"][0]["food_id"]
            for day in plan["days"]
            for meal in (day["meals"]["breakfast"],)
            if meal["has_portion"]
        ]
        self.assertEqual(len(portion_ids), len(set(portion_ids)))


if __name__ == "__main__":
    unittest.main()

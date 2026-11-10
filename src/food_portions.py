"""Source-backed, single-serving ingredient breakdown for Vietnamese dishes."""

import csv
from functools import lru_cache
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache(maxsize=1)
def load_food_portions():
    """Return verified portions keyed by food_id; keep CSV values JSON-safe."""
    with (DATA_DIR / "food_portions.csv").open(encoding="utf-8-sig", newline="") as stream:
        portions = {row["food_id"]: {**row, "ingredients": []} for row in csv.DictReader(stream)}

    with (DATA_DIR / "food_ingredients.csv").open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["food_id"] not in portions:
                raise ValueError(f"Unknown food_id in food_ingredients.csv: {row['food_id']}")
            portions[row["food_id"]]["ingredients"].append({
                "name_vi": row["ingredient_vi"],
                "name_en": row["ingredient_en"],
                "quantity": float(row["quantity"]),
                "unit": row["unit"],
            })

    if any(not portion["ingredients"] for portion in portions.values()):
        raise ValueError("Every food portion must have at least one ingredient")
    return portions


def attach_food_portion(food):
    """Add a verified ingredient breakdown when one exists."""
    portion = load_food_portions().get(str(food["food_id"]))
    if portion:
        food = dict(food)
        food["portion"] = portion
    return food

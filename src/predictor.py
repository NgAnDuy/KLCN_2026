"""Flask adapter for the exported MLP + Expert + Hybrid inference bundle."""

import importlib.util
from pathlib import Path


MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
INFERENCE_PATH = MODEL_DIR / "health_inference.py"


def _load_inference_module():
    # The repository also has models.py for SQLAlchemy; importing
    # models.health_inference would collide with that module.
    spec = importlib.util.spec_from_file_location(
        "health_inference_bundle", INFERENCE_PATH
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load inference bundle: {INFERENCE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HealthGoalPredictor:
    """Keep the app's prediction interface while exposing Hybrid details."""

    def __init__(self):
        self.bundle = _load_inference_module().HealthPredictor(MODEL_DIR)

    def predict(self, features, profile="current"):
        results = self.bundle.predict(features, profile=profile)
        if len(results) != 1:
            raise ValueError("Expected exactly one health profile for analysis")
        result = results[0]
        return {
            "goal": result["mlp_goal"],
            "confidence": result["mlp_confidence"],
            "probabilities": result["probabilities"],
            "expert_goal": result["expert_goal"],
            "expert_scores": result["expert_scores"],
            "expert_reasons": result["expert_reasons"],
            "threshold": result["threshold"],
            "final_goal": result["final_goal"],
            "decision_reason": result["decision_reason"],
            "profile": result["profile"],
        }

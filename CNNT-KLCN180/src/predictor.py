from pathlib import Path

import joblib
import numpy as np
import tensorflow as tf


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = MODEL_DIR / "health_mlp.keras"
PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.pkl"
LABEL_ENCODER_PATH = MODEL_DIR / "label_encoder.pkl"


class HealthGoalPredictor:

    def __init__(self):
        self.model = tf.keras.models.load_model(
            MODEL_PATH
        )

        self.preprocessor = joblib.load(
            PREPROCESSOR_PATH
        )

        self.label_encoder = joblib.load(
            LABEL_ENCODER_PATH
        )

    def predict(self, features):
        processed_features = (
            self.preprocessor.transform(
                features
            )
        )

        probabilities = self.model.predict(
            processed_features,
            verbose=0
        )[0]

        predicted_index = int(
            np.argmax(probabilities)
        )

        predicted_goal = (
            self.label_encoder
            .inverse_transform(
                [predicted_index]
            )[0]
        )

        confidence = float(
            probabilities[predicted_index]
        )

        probability_result = {}

        for goal, probability in zip(
            self.label_encoder.classes_,
            probabilities
        ):
            probability_result[goal] = float(
                probability
            )

        return {
            "goal": predicted_goal,
            "confidence": confidence,
            "probabilities": probability_result
        }
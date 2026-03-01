import numpy as np
from sklearn.ensemble import IsolationForest
import pickle
import os

MODEL_PATH = "ai/model.pkl"

class AnomalyModel:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42, n_estimators=50)
        self.trained = False
        self.baseline_data = []

    def add_sample(self, cpu: float, mem: float, procs: int, conns: int):
        self.baseline_data.append([cpu, mem, procs, conns])
        if len(self.baseline_data) >= 20 and not self.trained:
            self.train()

    def train(self):
        X = np.array(self.baseline_data)
        self.model.fit(X)
        self.trained = True

    def predict(self, cpu: float, mem: float, procs: int, conns: int) -> dict:
        if not self.trained:
            # Not enough data yet — return neutral score
            return {"anomaly": False, "risk_score": 1.0, "confidence": 0.0}

        sample = np.array([[cpu, mem, procs, conns]])
        pred = self.model.predict(sample)[0]         # -1 = anomaly, 1 = normal
        score = self.model.decision_function(sample)[0]  # lower = more anomalous

        # Normalize score to 0–10 risk scale
        # decision_function range is roughly -0.5 to 0.5
        normalized = max(0, min(10, (0.5 - score) * 10))

        return {
            "anomaly": pred == -1,
            "risk_score": round(normalized, 2),
            "confidence": round(abs(score), 3)
        }

    def save(self):
        os.makedirs("ai", exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load():
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, "rb") as f:
                return pickle.load(f)
        return AnomalyModel()

# Singleton instance
_model_instance = None

def get_model() -> AnomalyModel:
    global _model_instance
    if _model_instance is None:
        _model_instance = AnomalyModel.load()
    return _model_instance

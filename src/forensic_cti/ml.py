import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans

from .schema import NormalizedEvent


class ThreatModel:
    def __init__(self) -> None:
        self.anomaly_detector = IsolationForest(random_state=42, contamination=0.01)
        self.cluster_model = KMeans(n_clusters=2, random_state=42)
        self.trained = False

    def _build_feature_matrix(self, events: list[NormalizedEvent]) -> pd.DataFrame:
        rows = []
        for event in events:
            rows.append(
                {
                    "timestamp": event.timestamp.timestamp(),
                    "source_ip_present": int(bool(event.source_ip)),
                    "destination_ip_present": int(bool(event.destination_ip)),
                    "severity_score": {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(event.severity, 1),
                }
            )
        return pd.DataFrame(rows)

    def train(self, events: list[NormalizedEvent]) -> None:
        data = self._build_feature_matrix(events)
        if data.empty:
            return
        self.anomaly_detector.fit(data)
        self.cluster_model.fit(data)
        self.trained = True

    def score_event(self, event: NormalizedEvent) -> dict:
        data = self._build_feature_matrix([event])
        if data.empty or not self.trained:
            return {"score": 0.0, "is_anomaly": False}
        score = self.anomaly_detector.decision_function(data)[0]
        anomaly_label = self.anomaly_detector.predict(data)[0] < 0
        return {
            "score": float(score),
            "is_anomaly": bool(anomaly_label),
            "severity": event.severity,
        }

    def cluster_events(self, events: list[NormalizedEvent]) -> dict:
        data = self._build_feature_matrix(events)
        if data.empty or not self.trained:
            return {"clusters": [], "counts": {}}
        labels = self.cluster_model.predict(data)
        counts = {int(label): int((labels == label).sum()) for label in np.unique(labels)}
        return {"clusters": labels.tolist(), "counts": counts}

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from ipaddress import ip_address
from math import cos, pi, sin
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import MODEL_PATH, logger as config_logger
from .schema import NormalizedEvent, SeverityLevel

logger = config_logger.getChild(__name__)

SEVERITY_SCORE: dict[str, int] = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}

# Thresholds de decisão baseados em dados reais
CONTAMINATION_ESTIMATE = 0.05  # 5% de anomalias é mais realista
MIN_EVENTS_TO_TRAIN = 50  # Requer mais dados para treinar


def _normalize_ip(ip_value: Any) -> str | None:
    if ip_value is None:
        return None
    try:
        return str(ip_address(str(ip_value).strip()))
    except ValueError:
        return None


def _is_private_ip(ip_value: Any) -> int:
    normalized = _normalize_ip(ip_value)
    if normalized is None:
        return 0
    return int(ip_address(normalized).is_private)


def _cyclical(value: int, period: int) -> tuple[float, float]:
    radians = 2 * pi * value / period
    return sin(radians), cos(radians)


def _count_metadata_fields(metadata: dict) -> int:
    """Conta campos em metadata (feature de complexidade)."""
    return len(metadata) if metadata else 0


def _estimate_event_volume(timestamp: datetime, reference: datetime) -> int:
    """Estima volume implícito (proxy para atividade de período)."""
    hour_bin = timestamp.hour // 4  # 6 bins diários
    day_bin = timestamp.isoweekday()
    return (hour_bin * day_bin) % 10


@dataclass
class FeatureExtractor:
    """
    Extrai features para modelo de ML.
    
    Melhoria: Features mais sofisticadas para capturar comportamento real
    """
    reference_timestamp: datetime | None = None
    event_type_counts: dict[str, int] | None = None

    def fit(self, events: list[NormalizedEvent]) -> None:
        """Calcula estatísticas de treinamento."""
        if not events:
            self.reference_timestamp = datetime.utcnow()
            self.event_type_counts = {}
            return
        
        self.reference_timestamp = min(event.timestamp for event in events)
        
        # Calcula distribuição de event_type
        self.event_type_counts = {}
        for event in events:
            event_type = str(event.event_type).lower().strip()
            self.event_type_counts[event_type] = self.event_type_counts.get(event_type, 0) + 1

    def _severity_score(self, severity: Any) -> int:
        """Converte severidade para score ordinal."""
        if isinstance(severity, SeverityLevel):
            return SEVERITY_SCORE[severity.value]
        value = str(severity).strip().lower()
        return SEVERITY_SCORE.get(value, SEVERITY_SCORE["low"])

    def _event_type_frequency(self, event_type: str) -> float:
        """Retorna frequência normalizada do tipo de evento."""
        if not self.event_type_counts:
            return 0.5
        
        total = sum(self.event_type_counts.values())
        count = self.event_type_counts.get(event_type.lower().strip(), 0)
        return count / total if total > 0 else 0.5

    def transform(self, events: list[NormalizedEvent]) -> pd.DataFrame:
        """
        Transforma eventos em features para ML.
        
        Melhoria: Features mais explicáveis e relevantes
        """
        if self.reference_timestamp is None:
            self.reference_timestamp = datetime.utcnow()
        if self.event_type_counts is None:
            self.event_type_counts = {}

        rows: list[dict[str, Any]] = []
        for event in events:
            source_ip = _normalize_ip(event.source_ip)
            destination_ip = _normalize_ip(event.destination_ip)
            hour_sin, hour_cos = _cyclical(event.timestamp.hour, 24)
            weekday_sin, weekday_cos = _cyclical(event.timestamp.isoweekday(), 7)
            age_days = (event.timestamp - self.reference_timestamp).total_seconds() / 86400.0
            
            # Normaliza age_days para evitar valores extremos
            age_days_normalized = min(age_days / 365.0, 1.0)  # Normalize to 0-1
            
            event_type_str = str(event.event_type).lower().strip()
            metadata_field_count = _count_metadata_fields(event.metadata)
            event_volume_proxy = _estimate_event_volume(event.timestamp, self.reference_timestamp)

            rows.append(
                {
                    # Temporal features
                    "age_days_normalized": age_days_normalized,
                    "hour_sin": hour_sin,
                    "hour_cos": hour_cos,
                    "weekday_sin": weekday_sin,
                    "weekday_cos": weekday_cos,
                    
                    # Severity features
                    "severity_score": self._severity_score(event.severity),
                    
                    # IP presence features
                    "source_ip_present": int(bool(source_ip)),
                    "destination_ip_present": int(bool(destination_ip)),
                    "source_ip_private": _is_private_ip(source_ip),
                    "destination_ip_private": _is_private_ip(destination_ip),
                    "ip_pair_present": int(bool(source_ip and destination_ip)),
                    
                    # Behavioral features
                    "event_type": event_type_str,
                    "event_type_frequency": self._event_type_frequency(event_type_str),
                    "metadata_field_count": metadata_field_count,
                    "event_volume_proxy": event_volume_proxy,
                }
            )
        
        return pd.DataFrame(rows)


class ThreatModel:
    """
    Modelo ML para detecção de anomalias e clustering.
    
    Melhorias:
    - Features mais sofisticadas
    - Melhor validação
    - Métricas de confiança
    - Explicabilidade
    """
    
    def __init__(self) -> None:
        self.anomaly_detector = IsolationForest(random_state=42, contamination=CONTAMINATION_ESTIMATE)
        self.cluster_model = KMeans(n_clusters=3, random_state=42, n_init=10)  # n_init para convergência
        self.feature_extractor = FeatureExtractor()
        self.pipeline: Pipeline | None = None
        self.trained = False
        self.training_stats: dict[str, Any] = {}
        self._model_path = Path(MODEL_PATH)
        self._load()

    def _build_pipeline(self) -> Pipeline:
        numeric_features = [
            "age_days_normalized",
            "hour_sin",
            "hour_cos",
            "weekday_sin",
            "weekday_cos",
            "severity_score",
            "source_ip_present",
            "destination_ip_present",
            "source_ip_private",
            "destination_ip_private",
            "ip_pair_present",
            "event_type_frequency",
            "metadata_field_count",
            "event_volume_proxy",
        ]
        categorical_features = ["event_type"]

        preprocessor = ColumnTransformer(
            transformers=[
                ("numeric", StandardScaler(), numeric_features),
                (
                    "categorical",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False,),
                    categorical_features,
                ),
            ],
            remainder="drop",
        )
        return Pipeline([("preprocessor", preprocessor)])

    def _prepare(self, events: list[NormalizedEvent]) -> pd.DataFrame:
        self.feature_extractor.fit(events)
        data = self.feature_extractor.transform(events)
        if self.pipeline is None:
            self.pipeline = self._build_pipeline()
        return data

    def train(self, events: list[NormalizedEvent]) -> None:
        """
        Treina modelo de anomalias.
        
        Melhoria: Melhor validação e logging de métricas
        """
        if len(events) < MIN_EVENTS_TO_TRAIN:
            logger.warning("Insuficientes eventos para treinar: %d < %d", len(events), MIN_EVENTS_TO_TRAIN)
            self.trained = False
            self.training_stats = {"error": "insufficient_events", "events": len(events)}
            return

        try:
            data = self._prepare(events)
            assert self.pipeline is not None
            features = self.pipeline.fit_transform(data)
            
            # Treina anomaly detector
            self.anomaly_detector.fit(features)
            
            # Treina clustering se temos dados suficientes
            optimal_clusters = min(3, max(2, len(events) // 20))  # Heurística: 1 cluster per 20 eventos
            if len(features) >= optimal_clusters:
                self.cluster_model = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
                self.cluster_model.fit(features)
            
            # Calcula métricas de treinamento
            anomaly_scores = self.anomaly_detector.score_samples(features)
            n_anomalies = (self.anomaly_detector.predict(features) == -1).sum()
            
            self.training_stats = {
                "events_trained": len(events),
                "features_shape": features.shape,
                "anomalies_detected": int(n_anomalies),
                "anomaly_percentage": round(100 * n_anomalies / len(events), 2),
                "anomaly_score_min": round(float(anomaly_scores.min()), 4),
                "anomaly_score_max": round(float(anomaly_scores.max()), 4),
                "anomaly_score_mean": round(float(anomaly_scores.mean()), 4),
                "clusters": int(self.cluster_model.n_clusters),
            }
            
            self.trained = True
            self.save()
            logger.info("Modelo treinado: %s", self.training_stats)
        except Exception as exc:
            logger.exception("Erro ao treinar modelo")
            self.trained = False
            self.training_stats = {"error": str(exc)}

    def save(self) -> None:
        """Salva modelo em disco."""
        if self.pipeline is None:
            logger.warning("Pipeline não inicializado, pulando save")
            return

        self._model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "anomaly_detector": self.anomaly_detector,
                "cluster_model": self.cluster_model,
                "feature_extractor": self.feature_extractor,
                "pipeline": self.pipeline,
                "trained": self.trained,
                "training_stats": self.training_stats,
            },
            self._model_path,
        )
        logger.info("Modelo salvo em %s", self._model_path)

    def _load(self) -> None:
        """Carrega modelo persistido."""
        if not self._model_path.exists():
            logger.info("Nenhum modelo persistido em %s", self._model_path)
            return

        try:
            state = joblib.load(self._model_path)
            self.anomaly_detector = state.get("anomaly_detector", self.anomaly_detector)
            self.cluster_model = state.get("cluster_model", self.cluster_model)
            self.feature_extractor = state.get("feature_extractor", self.feature_extractor)
            self.pipeline = state.get("pipeline")
            self.trained = bool(state.get("trained", True))
            self.training_stats = state.get("training_stats", {})
            logger.info("Modelo carregado: trained=%s", self.trained)
        except Exception as exc:
            logger.exception("Erro ao carregar modelo persistido")
            self.trained = False

    def score_event(self, event: NormalizedEvent) -> dict[str, Any]:
        """
        Escore de anomalia com explicação.
        
        Melhoria: Retorna detalhes de por que é/não é anomalia
        """
        if not self.trained or self.pipeline is None:
            logger.warning("Score requisitado antes do treinamento")
            return {
                "score": 0.0,
                "is_anomaly": False,
                "severity": str(event.severity),
                "reason": "model_not_trained",
                "confidence": 0.0,
            }

        try:
            data = self.feature_extractor.transform([event])
            features = self.pipeline.transform(data)
            
            # Decision function (score negativo = anomalia)
            score = float(self.anomaly_detector.decision_function(features)[0])
            anomaly_label = int(self.anomaly_detector.predict(features)[0] < 0)
            
            # Calcula confiança
            all_scores = self.anomaly_detector.score_samples([features[0]])
            decision_boundary = -0.5  # Heurística
            distance_from_boundary = abs(score - decision_boundary)
            confidence = min(1.0, distance_from_boundary / 2.0)
            
            result = {
                "score": round(score, 4),
                "is_anomaly": bool(anomaly_label),
                "severity": str(event.severity),
                "reason": "anomaly_detected" if anomaly_label else "normal_behavior",
                "confidence": round(confidence, 4),
                "explanation": self._generate_explanation(event, anomaly_label, score),
            }
            logger.debug("Evento %s avaliado: anomaly=%s, score=%.4f", event.event_id, anomaly_label, score)
            return result
        except Exception as exc:
            logger.exception("Erro ao avaliar evento")
            return {
                "score": 0.0,
                "is_anomaly": False,
                "severity": str(event.severity),
                "reason": "scoring_error",
                "confidence": 0.0,
                "error": str(exc),
            }

    def _generate_explanation(self, event: NormalizedEvent, is_anomaly: bool, score: float) -> str:
        """Gera explicação legível sobre o score."""
        if not is_anomaly:
            return f"Evento dentro de padrão normal. Score: {score:.4f}"
        
        reasons = []
        
        if event.severity == SeverityLevel.critical:
            reasons.append("Severidade crítica")
        elif event.severity == SeverityLevel.high:
            reasons.append("Severidade alta")
        
        if event.source_ip and not event.destination_ip:
            reasons.append("IP origem sem destino")
        
        if len(event.metadata) > 10:
            reasons.append("Metadata complexa")
        
        if not reasons:
            reasons.append("Padrão atípico detectado")
        
        return f"Anomalia: {'; '.join(reasons)}. Score: {score:.4f}"

    def cluster_events(self, events: list[NormalizedEvent]) -> dict[str, Any]:
        """
        Agrupa eventos em clusters.
        
        Melhoria: Melhor tratamento de edge cases
        """
        if not self.trained or self.pipeline is None:
            logger.warning("Cluster request com modelo não treinado")
            return {"clusters": [], "counts": {}, "error": "model_not_trained"}

        if len(events) < self.cluster_model.n_clusters:
            logger.warning("Insuficientes eventos para clustering: %d < %d clusters", 
                          len(events), self.cluster_model.n_clusters)
            return {
                "clusters": [], 
                "counts": {}, 
                "error": "insufficient_events",
                "required_minimum": self.cluster_model.n_clusters
            }

        try:
            data = self.feature_extractor.transform(events)
            features = self.pipeline.transform(data)
            labels = self.cluster_model.predict(features)
            
            counts = {int(label): int((labels == label).sum()) for label in np.unique(labels)}
            
            logger.info("Agrupados %d eventos em %d clusters", len(events), len(counts))
            return {
                "clusters": labels.tolist(),
                "counts": counts,
                "cluster_sizes": sorted(counts.values(), reverse=True),
            }
        except Exception as exc:
            logger.exception("Erro ao fazer clustering")
            return {"clusters": [], "counts": {}, "error": str(exc)}

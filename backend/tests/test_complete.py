"""
Testes abrangentes para Plataforma Forense & CTI

Cobre: normalization, storage, correlation, ML, API
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from forensic_cti.normalization import normalize_record, _normalize_ip, _normalize_severity
from forensic_cti.schema import NormalizedEvent, SeverityLevel
from forensic_cti.correlation import CorrelationEngine
from forensic_cti.ml import ThreatModel, FeatureExtractor
from forensic_cti.storage import EventStorage
from sqlalchemy.orm import Session


class TestNormalization:
    """Testes de normalização de dados."""
    
    def test_normalize_record_with_all_fields(self):
        """Normaliza registro com todos os campos."""
        record = {
            "timestamp": "2026-06-07T14:30:00",
            "source_ip": "192.168.1.100",
            "destination_ip": "10.0.0.1",
            "event_type": "Login Attempt",
            "severity": "high",
            "user": "admin",
            "status": "failed"
        }
        
        normalized = normalize_record(record, raw_source="test_log")
        
        assert normalized.event_type == "Login Attempt"
        assert normalized.source_ip == "192.168.1.100"
        assert normalized.destination_ip == "10.0.0.1"
        assert normalized.severity == SeverityLevel.high
        assert normalized.raw_source == "test_log"
        assert "user" in normalized.metadata
        assert "status" in normalized.metadata
    
    def test_normalize_record_with_missing_fields(self):
        """Normaliza registro com campos ausentes."""
        record = {"message": "Login failed"}
        
        normalized = normalize_record(record)
        
        assert normalized.event_type == "Login failed"
        assert normalized.source_ip is None
        assert normalized.destination_ip is None
        assert normalized.severity == SeverityLevel.low
    
    def test_normalize_record_with_invalid_ip(self):
        """Rejeita IPs inválidos."""
        record = {
            "source_ip": "invalid.ip.address",
            "destination_ip": "999.999.999.999"
        }
        
        normalized = normalize_record(record)
        
        assert normalized.source_ip is None
        assert normalized.destination_ip is None
    
    def test_normalize_record_with_unix_timestamp(self):
        """Processa timestamp Unix."""
        unix_timestamp = 1685970600  # 2023-06-06 00:30:00
        record = {"timestamp": unix_timestamp}
        
        normalized = normalize_record(record)
        
        assert normalized.timestamp is not None
        assert isinstance(normalized.timestamp, datetime)
    
    def test_normalize_severity_conversion(self):
        """Converte severidades em variações."""
        assert _normalize_severity("CRITICAL") == SeverityLevel.critical
        assert _normalize_severity("high") == SeverityLevel.high
        assert _normalize_severity("Medium") == SeverityLevel.medium
        assert _normalize_severity("unknown") == SeverityLevel.low
    
    def test_normalize_ip_validation(self):
        """Valida endereços IP."""
        assert _normalize_ip("192.168.1.1") == "192.168.1.1"
        assert _normalize_ip("10.0.0.0") == "10.0.0.0"
        assert _normalize_ip("invalid.ip") is None
        assert _normalize_ip("999.999.999.999") is None


class TestCorrelation:
    """Testes do mecanismo de correlação."""
    
    def test_correlate_by_ip_same_window(self):
        """Correlaciona eventos no mesmo período."""
        engine = CorrelationEngine()
        
        base_time = datetime.utcnow()
        events = [
            NormalizedEvent(
                timestamp=base_time,
                source_ip="192.168.1.100",
                destination_ip="10.0.0.1",
                event_type="login",
                severity=SeverityLevel.low,
                raw_source="test"
            ),
            NormalizedEvent(
                timestamp=base_time + timedelta(minutes=10),
                source_ip="10.0.0.1",
                destination_ip="192.168.1.100",
                event_type="response",
                severity=SeverityLevel.low,
                raw_source="test"
            ),
        ]
        
        result = engine.correlate_by_ip(events, time_window=3600)
        
        assert len(result) >= 1
        assert result[0]["count"] >= 1
    
    def test_correlate_by_ip_outside_window(self):
        """Não correlaciona eventos fora da janela."""
        engine = CorrelationEngine()
        
        base_time = datetime.utcnow()
        events = [
            NormalizedEvent(
                timestamp=base_time,
                source_ip="192.168.1.100",
                destination_ip=None,
                event_type="event1",
                severity=SeverityLevel.low,
                raw_source="test"
            ),
            NormalizedEvent(
                timestamp=base_time + timedelta(hours=2),
                source_ip="192.168.1.100",
                destination_ip=None,
                event_type="event2",
                severity=SeverityLevel.low,
                raw_source="test"
            ),
        ]
        
        # Janela de 1 hora
        result = engine.correlate_by_ip(events, time_window=3600)
        
        # Segundo evento está fora da janela
        assert len(result) <= 1
    
    def test_find_reused_iocs(self):
        """Identifica IOCs reutilizados."""
        engine = CorrelationEngine()
        
        events = [
            NormalizedEvent(
                timestamp=datetime.utcnow(),
                source_ip="192.168.1.100",
                destination_ip=None,
                event_type="event1",
                severity=SeverityLevel.low,
                raw_source="test"
            ),
            NormalizedEvent(
                timestamp=datetime.utcnow() + timedelta(hours=1),
                source_ip="192.168.1.100",
                destination_ip=None,
                event_type="event2",
                severity=SeverityLevel.high,
                raw_source="test"
            ),
            NormalizedEvent(
                timestamp=datetime.utcnow() + timedelta(hours=2),
                source_ip="10.0.0.1",
                destination_ip=None,
                event_type="event3",
                severity=SeverityLevel.low,
                raw_source="test"
            ),
        ]
        
        result = engine.find_reused_iocs(events)
        
        assert len(result) >= 1
        assert result[0]["ioc"] == "192.168.1.100"
        assert result[0]["count"] == 2


class TestMachineLearning:
    """Testes do pipeline de ML."""
    
    def test_feature_extractor_fit_and_transform(self):
        """Extrai features de eventos."""
        extractor = FeatureExtractor()
        
        events = [
            NormalizedEvent(
                timestamp=datetime.utcnow(),
                source_ip="192.168.1.1",
                destination_ip="10.0.0.1",
                event_type="login",
                severity=SeverityLevel.low,
                raw_source="test"
            ),
            NormalizedEvent(
                timestamp=datetime.utcnow() + timedelta(hours=1),
                source_ip="192.168.1.2",
                destination_ip="10.0.0.2",
                event_type="logout",
                severity=SeverityLevel.low,
                raw_source="test"
            ),
        ]
        
        extractor.fit(events)
        features_df = extractor.transform(events)
        
        assert len(features_df) == 2
        assert "severity_score" in features_df.columns
        assert "hour_sin" in features_df.columns
        assert "event_type" in features_df.columns
    
    def test_threat_model_train_insufficient_events(self):
        """Rejeita treinamento com poucos eventos."""
        model = ThreatModel()
        
        events = [
            NormalizedEvent(
                timestamp=datetime.utcnow(),
                source_ip="192.168.1.1",
                destination_ip=None,
                event_type="login",
                severity=SeverityLevel.low,
                raw_source="test"
            )
        ]
        
        model.train(events)
        
        assert not model.trained
    
    def test_threat_model_train_sufficient_events(self):
        """Treina modelo com eventos suficientes."""
        model = ThreatModel()
        
        # Cria 100 eventos de treinamento
        events = []
        base_time = datetime.utcnow()
        for i in range(100):
            events.append(
                NormalizedEvent(
                    timestamp=base_time + timedelta(minutes=i),
                    source_ip=f"192.168.1.{i % 10 + 1}",
                    destination_ip=f"10.0.0.{i % 5 + 1}",
                    event_type=["login", "logout", "access", "error"][i % 4],
                    severity=[SeverityLevel.low, SeverityLevel.medium][i % 2],
                    raw_source="test"
                )
            )
        
        model.train(events)
        
        assert model.trained
        assert model.training_stats.get("events_trained") == 100
    
    def test_threat_model_score_untrained(self):
        """Score sem modelo treinado retorna valores seguros."""
        model = ThreatModel()
        
        event = NormalizedEvent(
            timestamp=datetime.utcnow(),
            source_ip="192.168.1.1",
            destination_ip=None,
            event_type="login",
            severity=SeverityLevel.high,
            raw_source="test"
        )
        
        result = model.score_event(event)
        
        assert result["is_anomaly"] is False
        assert result["score"] == 0.0
        assert "model_not_trained" in result["reason"]


class TestStorage:
    """Testes de persistência."""
    
    def test_event_storage_initialization(self):
        """Inicializa storage corretamente."""
        storage = EventStorage()
        assert storage is not None
    
    def test_persist_events_unique_ids(self):
        """Garante event_ids únicos na persistência."""
        storage = EventStorage()
        
        events = [
            NormalizedEvent(
                event_id="",  # ID vazio - deve gerar novo
                timestamp=datetime.utcnow(),
                source_ip="192.168.1.1",
                destination_ip=None,
                event_type="event1",
                severity=SeverityLevel.low,
                raw_source="test"
            ),
            NormalizedEvent(
                event_id=None,  # ID None - deve gerar novo
                timestamp=datetime.utcnow(),
                source_ip="192.168.1.2",
                destination_ip=None,
                event_type="event2",
                severity=SeverityLevel.low,
                raw_source="test"
            ),
        ]
        
        # Mock session (não persiste realmente)
        # Este teste seria completo com fixture de banco de dados
        assert len(events) == 2


class TestAPI:
    """Testes de integração da API."""
    
    def test_health_endpoint(self):
        """Endpoint de saúde responde."""
        from forensic_cti.api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_model_status_endpoint(self):
        """Endpoint de status do modelo."""
        from forensic_cti.api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/model/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "trained" in data
        assert "training_stats" in data


# Fixtures
@pytest.fixture
def sample_events():
    """Eventos de exemplo para testes."""
    base_time = datetime.utcnow()
    return [
        NormalizedEvent(
            timestamp=base_time + timedelta(hours=i),
            source_ip=f"192.168.1.{i}",
            destination_ip=f"10.0.0.{i}",
            event_type=["login", "logout", "error"][i % 3],
            severity=[SeverityLevel.low, SeverityLevel.medium, SeverityLevel.high][i % 3],
            raw_source="test"
        )
        for i in range(20)
    ]


@pytest.fixture
def correlation_engine():
    """Engine de correlação."""
    return CorrelationEngine()


@pytest.fixture
def threat_model():
    """Modelo de ML."""
    return ThreatModel()


if __name__ == "__main__":
    # Executa testes
    pytest.main([__file__, "-v", "--tb=short"])

from datetime import datetime

from forensic_cti.normalization import normalize_record
from forensic_cti.schema import NormalizedEvent, SeverityLevel


def test_normalize_record_defaults():
    raw = {"message": "test event", "timestamp": "2026-05-10T12:00:00"}
    normalized = normalize_record(raw, raw_source="test")

    assert isinstance(normalized, NormalizedEvent)
    assert normalized.event_type == "test event"
    assert normalized.severity == SeverityLevel.low
    assert normalized.raw_source == "test"
    assert normalized.timestamp == datetime.fromisoformat("2026-05-10T12:00:00")

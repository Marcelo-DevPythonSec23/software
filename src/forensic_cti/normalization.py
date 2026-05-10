from datetime import datetime
from typing import Any, Dict

from .schema import NormalizedEvent


DEFAULT_SCHEMA = {
    "timestamp": None,
    "source_ip": None,
    "destination_ip": None,
    "event_type": "unknown",
    "severity": "low",
    "raw_source": "unknown",
    "metadata": {},
}


def normalize_record(record: Dict[str, Any], raw_source: str = "unknown") -> NormalizedEvent:
    timestamp = record.get("timestamp") or record.get("time") or record.get("datetime")
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            timestamp = datetime.utcnow()
    elif timestamp is None:
        timestamp = datetime.utcnow()

    event_type = record.get("event_type") or record.get("type") or record.get("message", "unknown")
    severity = record.get("severity") or record.get("level") or "low"
    metadata = {k: v for k, v in record.items() if k not in {"timestamp", "time", "datetime", "event_type", "type", "severity", "level", "message", "source_ip", "destination_ip"}}

    return NormalizedEvent(
        timestamp=timestamp,
        source_ip=record.get("source_ip") or record.get("src_ip") or record.get("ip_src"),
        destination_ip=record.get("destination_ip") or record.get("dst_ip") or record.get("ip_dst"),
        event_type=str(event_type),
        severity=str(severity).lower(),
        raw_source=raw_source,
        metadata=metadata,
    )

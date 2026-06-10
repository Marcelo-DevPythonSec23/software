from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class EventModel(BaseModel):
    event_id: Optional[str] = Field(default_factory=lambda: str(uuid4()), description="Identificador único do evento")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_ip: Optional[str] = Field(None, description="IP de origem")
    destination_ip: Optional[str] = Field(None, description="IP de destino")
    event_type: str = Field(..., description="Tipo de evento")
    severity: SeverityLevel = Field(default=SeverityLevel.low)
    raw_source: str = Field(..., description="Origem bruta do evento")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Dados suplementares normalizados")


class NormalizedEvent(EventModel):
    pass


class QueryResponse(BaseModel):
    total: int
    items: list[NormalizedEvent]


class AnomalyScore(BaseModel):
    event_id: str
    score: float
    is_anomaly: bool
    reason: Optional[str] = None

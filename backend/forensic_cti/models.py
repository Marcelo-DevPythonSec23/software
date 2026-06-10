import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Index, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class EventRecord(Base):
    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("event_id", name="uq_event_id"),
        # Índices para melhor performance
        Index("ix_events_timestamp", "timestamp"),
        Index("ix_events_timestamp_source_ip", "timestamp", "source_ip"),
        Index("ix_events_timestamp_dest_ip", "timestamp", "destination_ip"),
        Index("ix_events_source_dest_ip", "source_ip", "destination_ip"),
        Index("ix_events_event_type_severity", "event_type", "severity"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), nullable=False, unique=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    source_ip = Column(String(64), nullable=True, index=True)
    destination_ip = Column(String(64), nullable=True, index=True)
    event_type = Column(String(128), nullable=False, index=True)
    severity = Column(String(16), nullable=False, index=True)
    raw_source = Column(String(128), nullable=False)
    event_metadata = Column("metadata", JSON, nullable=False, default=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "source_ip": self.source_ip,
            "destination_ip": self.destination_ip,
            "event_type": self.event_type,
            "severity": self.severity,
            "raw_source": self.raw_source,
            "metadata": self.event_metadata,
        }

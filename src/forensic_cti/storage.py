from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .db import init_db
from .models import EventRecord
from .schema import NormalizedEvent


class StorageError(Exception):
    pass


class EventStorage:
    def __init__(self) -> None:
        init_db()

    def persist_events(self, session: Session, events: List[NormalizedEvent]) -> int:
        records = []
        for event in events:
            records.append(
                EventRecord(
                    event_id=event.event_id or str(uuid4()),
                    timestamp=event.timestamp,
                    source_ip=event.source_ip,
                    destination_ip=event.destination_ip,
                    event_type=event.event_type,
                    severity=event.severity.value,
                    raw_source=event.raw_source,
                    event_metadata=event.metadata,
                )
            )

        session.add_all(records)
        try:
            session.commit()
            return len(records)
        except SQLAlchemyError as exc:
            session.rollback()
            raise StorageError(f"Erro ao persistir eventos: {exc}") from exc

    def query_events(
        self,
        session: Session,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        stmt = select(EventRecord).limit(limit)
        if filters:
            for key, value in filters.items():
                if hasattr(EventRecord, key):
                    stmt = stmt.where(getattr(EventRecord, key) == value)

        rows = session.execute(stmt).scalars().all()
        return [record.to_dict() for record in rows]

    def search_by_ioc(self, session: Session, ioc: str, limit: int = 100) -> List[Dict[str, Any]]:
        stmt = select(EventRecord).where(
            or_(EventRecord.source_ip == ioc, EventRecord.destination_ip == ioc)
        )
        rows = session.execute(stmt).scalars().all()

        matches: List[Dict[str, Any]] = []
        query = ioc.lower()
        for record in rows:
            metadata_text = str(record.event_metadata or {}).lower()
            if record.source_ip == ioc or record.destination_ip == ioc or query in metadata_text:
                matches.append(record.to_dict())
                if len(matches) >= limit:
                    break
        return matches

import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .config import logger as config_logger
from .db import init_db
from .models import EventRecord
from .schema import NormalizedEvent

logger = config_logger.getChild(__name__)


class StorageError(Exception):
    pass


class EventStorage:
    def __init__(self) -> None:
        init_db()
        logger.info("Initialized event storage with database URL")

    def persist_events(self, session: Session, events: List[NormalizedEvent]) -> int:
        """
        Persiste eventos normalizados.
        
        Corrige: BUG #5 - Garantir UUID único
        """
        records = []
        for event in events:
            # Garante que event_id é sempre definido
            event_id = event.event_id
            if not event_id or event_id.strip() == "":
                event_id = str(uuid4())
                logger.debug("Gerado novo event_id %s para evento sem ID", event_id)
            
            records.append(
                EventRecord(
                    event_id=event_id,
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
            logger.info("Persistidos %d eventos com sucesso", len(records))
            return len(records)
        except SQLAlchemyError as exc:
            session.rollback()
            logger.exception("Erro ao persistir eventos")
            raise StorageError(f"Erro ao persistir eventos: {exc}") from exc

    def query_events(
        self,
        session: Session,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Consulta eventos com filtros e paginação.
        """
        stmt = select(EventRecord).offset(offset).limit(limit)
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(EventRecord, key) and value is not None:
                    if isinstance(value, str):
                        # Busca case-insensitive para strings
                        conditions.append(getattr(EventRecord, key).ilike(f"%{value}%"))
                    else:
                        conditions.append(getattr(EventRecord, key) == value)
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
        
        rows = session.execute(stmt).scalars().all()
        logger.debug("Consultados %d eventos com filtros=%s", len(rows), filters)
        return [record.to_dict() for record in rows]

    def search_by_ioc(self, session: Session, ioc: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Busca por IOC (IP, domínio, hash).
        
        Corrige: BUG #2 - Performance e lógica circular
        """
        if not ioc or not ioc.strip():
            logger.warning("Busca por IOC vazio")
            return []
        
        ioc = ioc.strip()
        
        # Busca por IP exato (eficiente com índice)
        stmt = select(EventRecord).where(
            or_(
                EventRecord.source_ip == ioc,
                EventRecord.destination_ip == ioc
            )
        ).limit(limit)
        
        matches = session.execute(stmt).scalars().all()
        result = [record.to_dict() for record in matches]
        
        # Se encontrou muitos matches exatos, retorna
        if len(result) >= limit:
            logger.info("Encontrados %d matches exatos para IOC %s", len(result), ioc)
            return result
        
        # Busca em metadata APENAS se não encontrou suficiente
        if len(result) < limit:
            query_lower = ioc.lower()
            metadata_matches = []
            
            # Busca em metadata com limite
            remaining_limit = limit - len(result)
            stmt_meta = select(EventRecord).limit(remaining_limit * 5)  # Busca mais para filtrar
            
            for record in session.execute(stmt_meta).scalars().all():
                metadata_text = str(record.event_metadata or {}).lower()
                
                if query_lower in metadata_text:
                    # Evita duplicatas
                    if record.event_id not in {r.get("event_id") for r in result}:
                        metadata_matches.append(record.to_dict())
                        if len(metadata_matches) >= remaining_limit:
                            break
            
            result.extend(metadata_matches)
        
        logger.info("Encontrados %d matches para IOC %s", len(result), ioc)
        return result[:limit]

    def get_event_count(self, session: Session) -> int:
        """Retorna contagem total de eventos."""
        stmt = select(EventRecord)
        return session.query(EventRecord).count()

    def delete_old_events(self, session: Session, days: int = 90) -> int:
        """Remove eventos mais antigos que N dias."""
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        stmt = select(EventRecord).where(EventRecord.timestamp < cutoff)
        old_events = session.execute(stmt).scalars().all()
        count = len(old_events)
        
        for event in old_events:
            session.delete(event)
        
        try:
            session.commit()
            logger.info("Deletados %d eventos antigos (> %d dias)", count, days)
            return count
        except SQLAlchemyError as exc:
            session.rollback()
            logger.exception("Erro ao deletar eventos antigos")
            raise StorageError(f"Erro ao deletar eventos: {exc}") from exc

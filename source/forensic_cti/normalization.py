import logging
from datetime import datetime
from ipaddress import ip_address
from typing import Any, Dict, Optional

from .config import logger as config_logger
from .schema import NormalizedEvent, SeverityLevel

logger = config_logger.getChild(__name__)


def _parse_timestamp(value: Any, record_id: str = "unknown") -> datetime:
    """
    Faz parse de timestamp com logging de erros.
    
    Corrige: BUG #3 - Tratamento silencioso de erros
    """
    if isinstance(value, datetime):
        return value
    
    if isinstance(value, (int, float)):
        try:
            return datetime.utcfromtimestamp(value)
        except (OverflowError, OSError, ValueError) as e:
            logger.warning("Timestamp inválido (numérico): valor=%s, record=%s, erro=%s", value, record_id, e)
            return datetime.utcnow()

    if isinstance(value, str):
        value = value.strip()
        
        # Tenta ISO format primeiro (mais comum)
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass
        
        # Tenta Unix timestamp string
        if value.isdigit():
            try:
                return datetime.utcfromtimestamp(int(value))
            except (OverflowError, OSError, ValueError) as e:
                logger.warning("Timestamp numérico inválido: valor=%s, record=%s, erro=%s", value, record_id, e)
                return datetime.utcnow()
        
        # Fallback com logging
        logger.warning("Timestamp inválido (string): valor=%s, record=%s", value, record_id)
        return datetime.utcnow()
    
    # Nenhum tipo reconhecido
    logger.warning("Timestamp tipo desconhecido: tipo=%s, record=%s", type(value).__name__, record_id)
    return datetime.utcnow()


def _normalize_ip(value: Any) -> Optional[str]:
    """Normaliza e valida endereço IP."""
    if value is None:
        return None
    try:
        return str(ip_address(str(value).strip()))
    except ValueError:
        return None


def _normalize_severity(value: Any) -> SeverityLevel:
    """Normaliza nível de severidade."""
    normalized = str(value).strip().lower() if value is not None else "low"
    try:
        return SeverityLevel(normalized)
    except ValueError:
        logger.debug("Severidade desconhecida: %s, usando 'low'", value)
        return SeverityLevel.low


def _extract_ips_from_metadata(metadata: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
    """
    Busca IPs adicionais em campos de metadata.
    
    Melhoria: Melhor extração de IPs
    """
    source_ip = None
    destination_ip = None
    
    # Procura padrões comuns de IP em metadata
    ip_patterns = [
        "remote_ip", "client_ip", "attacker_ip", "sender_ip", "from_ip",
        "dest_ip", "target_ip", "server_ip", "receiver_ip", "to_ip",
        "request_ip", "response_ip"
    ]
    
    metadata_lower = {k.lower(): v for k, v in metadata.items()}
    
    for pattern in ip_patterns:
        if pattern in metadata_lower and not source_ip:
            ip = _normalize_ip(metadata_lower[pattern])
            if ip:
                source_ip = ip
                break
    
    return source_ip, destination_ip


def normalize_record(record: Dict[str, Any], raw_source: str = "unknown", record_id: str = "unknown") -> NormalizedEvent:
    """
    Normaliza um registro bruto para NormalizedEvent.
    
    Melhoria: Melhor logging, melhor extração de IPs, melhor tratamento de erros
    """
    # Parse timestamp com logging
    timestamp = _parse_timestamp(
        record.get("timestamp") or record.get("time") or record.get("datetime"),
        record_id=record_id
    )

    # Extrai event type
    event_type = record.get("event_type") or record.get("type") or record.get("message") or "unknown"
    event_type = str(event_type).strip() or "unknown"
    
    # Normaliza severidade
    severity = _normalize_severity(record.get("severity") or record.get("level") or "low")

    # Extrai IPs com múltiplos padrões
    source_ip = _normalize_ip(
        record.get("source_ip") or record.get("src_ip") or record.get("ip_src")
    )
    destination_ip = _normalize_ip(
        record.get("destination_ip") or record.get("dst_ip") or record.get("ip_dst")
    )
    
    # Extrai metadata (tudo que não foi explicitamente capturado)
    excluded_fields = {
        "timestamp", "time", "datetime",
        "event_type", "type", "severity", "level", "message",
        "source_ip", "destination_ip", "src_ip", "dst_ip", "ip_src", "ip_dst",
    }
    
    metadata = {
        k: v
        for k, v in record.items()
        if k.lower() not in {f.lower() for f in excluded_fields}
    }
    
    logger.debug(
        "Normalizado: event_type=%s, source_ip=%s, dest_ip=%s, severity=%s",
        event_type, source_ip, destination_ip, severity.value
    )
    
    return NormalizedEvent(
        timestamp=timestamp,
        source_ip=source_ip,
        destination_ip=destination_ip,
        event_type=event_type,
        severity=severity,
        raw_source=str(raw_source),
        metadata=metadata,
    )

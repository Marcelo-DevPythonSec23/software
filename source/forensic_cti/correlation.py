import logging
from collections import defaultdict
from datetime import timedelta
from ipaddress import ip_address
from typing import Any, Dict, List, Optional

from .config import logger as config_logger
from .schema import NormalizedEvent

logger = config_logger.getChild(__name__)


def _validate_ip(ip_str: Optional[str]) -> bool:
    """Valida se uma string é um IP válido."""
    if not ip_str:
        return False
    try:
        ip_address(ip_str)
        return True
    except ValueError:
        return False


class CorrelationEngine:
    def correlate_by_ip(
        self, 
        events: List[NormalizedEvent], 
        time_window: int = 3600,
        min_matches: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Correlaciona eventos por IP dentro de janela temporal.
        
        Corrige: BUG #1 - Lógica circular de histórico
        """
        if not events:
            return []
            
        events_sorted = sorted(events, key=lambda ev: ev.timestamp)
        correlated: List[Dict[str, Any]] = []
        
        # Index com eventos por IP (sem histórico mutável)
        ip_index: Dict[str, List[NormalizedEvent]] = defaultdict(list)
        
        for event in events_sorted:
            candidates = {ip for ip in (event.source_ip, event.destination_ip) if _validate_ip(ip)}
            
            if not candidates:
                continue
            
            window_start = event.timestamp - timedelta(seconds=time_window)
            related: List[NormalizedEvent] = []
            
            # Busca eventos relacionados dentro da janela
            for ioc in candidates:
                for prior_event in ip_index[ioc]:
                    if prior_event.timestamp >= window_start:
                        related.append(prior_event)
            
            # Remove duplicatas mantendo ordem
            unique_related = []
            seen = set()
            for e in related:
                if e.event_id not in seen:
                    unique_related.append(e)
                    seen.add(e.event_id)
            
            if len(unique_related) >= min_matches:
                correlated.append({
                    "anchor": event,
                    "matches": unique_related,
                    "count": len(unique_related),
                    "time_window_seconds": time_window,
                })
            
            # Adiciona evento ao índice (DEPOIS de processar, não antes)
            for ioc in candidates:
                ip_index[ioc].append(event)
        
        logger.info("Correlação por IP: %d eventos correlacionados de %d", len(correlated), len(events))
        return correlated

    def find_reused_iocs(
        self, 
        events: List[NormalizedEvent], 
        min_reuse: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Encontra IPs reutilizados em múltiplos eventos.
        
        Corrige: BUG #6 - Sem validação de IP
        """
        ioc_index: Dict[str, List[NormalizedEvent]] = defaultdict(list)
        
        for event in events:
            # Valida IPs antes de indexar
            for candidate in (event.source_ip, event.destination_ip):
                if _validate_ip(candidate):
                    ioc_index[candidate].append(event)
        
        reused = [
            {
                "ioc": ioc, 
                "events": matches, 
                "count": len(matches),
                "first_seen": min(e.timestamp for e in matches),
                "last_seen": max(e.timestamp for e in matches),
                "severity_max": max(e.severity for e in matches),
            }
            for ioc, matches in ioc_index.items()
            if len(matches) >= min_reuse
        ]
        
        logger.info("IPs reutilizados: %d IOCs encontrados em %d eventos", len(reused), len(events))
        return sorted(reused, key=lambda item: item["count"], reverse=True)

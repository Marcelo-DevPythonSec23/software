from datetime import timedelta
from typing import Any, Dict, List

from .schema import NormalizedEvent


class CorrelationEngine:
    def correlate_by_ip(self, events: List[NormalizedEvent], time_window: int = 3600) -> List[Dict[str, Any]]:
        events_sorted = sorted(events, key=lambda ev: ev.timestamp)
        correlated = []

        for index, event in enumerate(events_sorted):
            window_start = event.timestamp - timedelta(seconds=time_window)
            related = [
                e for e in events_sorted[:index]
                if e.timestamp >= window_start
                and (e.source_ip == event.source_ip or e.destination_ip == event.destination_ip or e.source_ip == event.destination_ip or e.destination_ip == event.source_ip)
            ]
            if related:
                correlated.append({
                    "anchor": event,
                    "matches": related,
                    "count": len(related),
                })
        return correlated

    def find_reused_iocs(self, events: List[NormalizedEvent]) -> List[Dict[str, Any]]:
        ioc_index: Dict[str, List[NormalizedEvent]] = {}
        for event in events:
            for candidate in [event.source_ip, event.destination_ip]:
                if candidate:
                    ioc_index.setdefault(candidate, []).append(event)

        reused = [
            {"ioc": ioc, "events": matches, "count": len(matches)}
            for ioc, matches in ioc_index.items()
            if len(matches) > 1
        ]
        return sorted(reused, key=lambda item: item["count"], reverse=True)

import csv
import json
from pathlib import Path
from typing import Any

from .schema import NormalizedEvent
from .normalization import normalize_record


class IngestionError(Exception):
    pass


class FileIngestor:
    """Ingestão de arquivos CSV, JSON e LOG para eventos normalizados."""

    def ingest_csv(self, path: Path) -> list[NormalizedEvent]:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            reader = csv.DictReader(handle)
            return [normalize_record(dict(row), raw_source=str(path)) for row in reader]

    def ingest_json(self, path: Path) -> list[NormalizedEvent]:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            data = json.load(handle)
            if isinstance(data, list):
                return [normalize_record(item, raw_source=str(path)) for item in data]
            if isinstance(data, dict):
                return [normalize_record(data, raw_source=str(path))]
            raise IngestionError("JSON precisa ser lista ou objeto")

    def ingest_log(self, path: Path) -> list[NormalizedEvent]:
        events = []
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                trimmed = line.strip()
                if not trimmed:
                    continue
                events.append(normalize_record({"message": trimmed}, raw_source=str(path)))
        return events

    def ingest_path(self, path: Path) -> list[NormalizedEvent]:
        if not path.exists():
            raise IngestionError(f"Arquivo não encontrado: {path}")
        if path.suffix.lower() == ".csv":
            return self.ingest_csv(path)
        if path.suffix.lower() == ".json":
            return self.ingest_json(path)
        return self.ingest_log(path)


class ExternalSourceIngestor:
    """Stub para coletores de fontes externas como VirusTotal, Shodan e AbuseIPDB."""

    def ingest_virus_total(self, query: str) -> list[NormalizedEvent]:
        return [normalize_record({"message": f"VirusTotal query {query}"}, raw_source="virustotal")]

    def ingest_shodan(self, query: str) -> list[NormalizedEvent]:
        return [normalize_record({"message": f"Shodan query {query}"}, raw_source="shodan")]

    def ingest_abuse_ipdb(self, ip_address: str) -> list[NormalizedEvent]:
        return [normalize_record({"message": f"AbuseIPDB lookup {ip_address}"}, raw_source="abuseipdb")]

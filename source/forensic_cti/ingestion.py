import csv
import json
import logging
from pathlib import Path
from typing import Any

from .config import logger as config_logger
from .normalization import normalize_record
from .schema import NormalizedEvent

logger = config_logger.getChild(__name__)


class IngestionError(Exception):
    pass


class FileIngestor:
    """Ingestão de arquivos CSV, JSON e LOG para eventos normalizados."""

    def ingest_csv(self, path: Path) -> list[NormalizedEvent]:
        logger.info("Ingesting CSV file: %s", path)
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            reader = csv.DictReader(handle)
            events = [normalize_record(dict(row), raw_source=str(path)) for row in reader]
        logger.info("Ingested %d events from CSV file %s", len(events), path)
        return events

    def ingest_json(self, path: Path) -> list[NormalizedEvent]:
        logger.info("Ingesting JSON file: %s", path)
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            data = json.load(handle)
            if isinstance(data, list):
                events = [normalize_record(item, raw_source=str(path)) for item in data]
            elif isinstance(data, dict):
                events = [normalize_record(data, raw_source=str(path))]
            else:
                raise IngestionError("JSON precisa ser lista ou objeto")
        logger.info("Ingested %d events from JSON file %s", len(events), path)
        return events

    def ingest_log(self, path: Path) -> list[NormalizedEvent]:
        logger.info("Ingesting log file: %s", path)
        events: list[NormalizedEvent] = []
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                trimmed = line.strip()
                if not trimmed:
                    continue
                events.append(normalize_record({"message": trimmed}, raw_source=str(path)))
        logger.info("Ingested %d events from log file %s", len(events), path)
        return events

    def ingest_path(self, path: Path) -> list[NormalizedEvent]:
        if not path.exists():
            logger.error("Ingest path does not exist: %s", path)
            raise IngestionError(f"Arquivo não encontrado: {path}")
        if path.suffix.lower() == ".csv":
            return self.ingest_csv(path)
        if path.suffix.lower() == ".json":
            return self.ingest_json(path)
        return self.ingest_log(path)


class ExternalSourceIngestor:
    """Stub para coletores de fontes externas como VirusTotal, Shodan e AbuseIPDB."""

    def ingest_virus_total(self, query: str) -> list[NormalizedEvent]:
        logger.info("Ingesting external VirusTotal data for query: %s", query)
        return [normalize_record({"message": f"VirusTotal query {query}"}, raw_source="virustotal")]

    def ingest_shodan(self, query: str) -> list[NormalizedEvent]:
        logger.info("Ingesting external Shodan data for query: %s", query)
        return [normalize_record({"message": f"Shodan query {query}"}, raw_source="shodan")]

    def ingest_abuse_ipdb(self, ip_address: str) -> list[NormalizedEvent]:
        logger.info("Ingesting external AbuseIPDB data for IP: %s", ip_address)
        return [normalize_record({"message": f"AbuseIPDB lookup {ip_address}"}, raw_source="abuseipdb")]

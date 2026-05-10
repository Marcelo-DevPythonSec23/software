from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .correlation import CorrelationEngine
from .db import get_session, init_db
from .ingestion import ExternalSourceIngestor, FileIngestor
from .ml import ThreatModel
from .schema import AnomalyScore, NormalizedEvent, QueryResponse
from .storage import EventStorage, StorageError

app = FastAPI(
    title="Plataforma Forense & CTI",
    description="API para ingestão, normalização, correlação e análise de eventos de segurança.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage = EventStorage()
correlation = CorrelationEngine()
threat_model = ThreatModel()
file_ingestor = FileIngestor()
external_ingestor = ExternalSourceIngestor()


class UploadResponse(BaseModel):
    ingested: int


@app.on_event("startup")
async def on_startup() -> None:
    init_db()


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "forensic_cti"}


@app.post("/ingest/file", response_model=UploadResponse, tags=["ingestion"])
async def ingest_file(path: str, session: Session = Depends(get_session)) -> UploadResponse:
    try:
        events = file_ingestor.ingest_path(Path(path))
        count = storage.persist_events(session=session, events=events)
        return UploadResponse(ingested=count)
    except StorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/events", response_model=QueryResponse, tags=["events"])
async def list_events(
    limit: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
) -> QueryResponse:
    items = storage.query_events(session=session, limit=limit)
    return QueryResponse(total=len(items), items=[NormalizedEvent(**item) for item in items])


@app.get("/events/search", response_model=QueryResponse, tags=["events"])
async def search_ioc(
    ioc: str,
    limit: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
) -> QueryResponse:
    items = storage.search_by_ioc(session=session, ioc=ioc, limit=limit)
    return QueryResponse(total=len(items), items=[NormalizedEvent(**item) for item in items])


@app.get("/correlation/ip", tags=["correlation"])
async def correlate_ip(
    limit: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    items = storage.query_events(session=session, limit=limit)
    events = [NormalizedEvent(**item) for item in items]
    matches = correlation.correlate_by_ip(events)
    reused = correlation.find_reused_iocs(events)
    return {"matches": matches, "reused_iocs": reused}


@app.post("/ml/train", tags=["machine-learning"])
async def train_model(
    limit: int = Query(500, ge=1, le=1000),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    items = storage.query_events(session=session, limit=limit)
    events = [NormalizedEvent(**item) for item in items]
    threat_model.train(events)
    return {"trained": threat_model.trained, "events": len(events)}


@app.post("/ml/score", response_model=AnomalyScore, tags=["machine-learning"])
async def score_event(event: NormalizedEvent) -> AnomalyScore:
    result = threat_model.score_event(event)
    return AnomalyScore(
        event_id=event.event_id,
        score=result["score"],
        is_anomaly=result["is_anomaly"],
        reason=result.get("reason"),
    )


@app.post("/external/virustotal", response_model=UploadResponse, tags=["external"])
async def ingest_virustotal(query: str, session: Session = Depends(get_session)) -> UploadResponse:
    events = external_ingestor.ingest_virus_total(query)
    count = storage.persist_events(session=session, events=events)
    return UploadResponse(ingested=count)


@app.post("/external/shodan", response_model=UploadResponse, tags=["external"])
async def ingest_shodan(query: str, session: Session = Depends(get_session)) -> UploadResponse:
    events = external_ingestor.ingest_shodan(query)
    count = storage.persist_events(session=session, events=events)
    return UploadResponse(ingested=count)


@app.post("/external/abuseipdb", response_model=UploadResponse, tags=["external"])
async def ingest_abuseipdb(ip_address: str, session: Session = Depends(get_session)) -> UploadResponse:
    events = external_ingestor.ingest_abuse_ipdb(ip_address)
    count = storage.persist_events(session=session, events=events)
    return UploadResponse(ingested=count)

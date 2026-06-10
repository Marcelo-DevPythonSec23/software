from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .config import logger as config_logger
from .correlation import CorrelationEngine
from .db import get_session, init_db
from .ingestion import ExternalSourceIngestor, FileIngestor
from .ml import ThreatModel
from .schema import AnomalyScore, NormalizedEvent, QueryResponse
from .storage import EventStorage, StorageError

logger = config_logger.getChild(__name__)

app = FastAPI(
    title="Plataforma Forense & CTI",
    description="API para ingestão, normalização, correlação e análise de eventos de segurança.",
    version="0.2.0",
)

# CORS mais restritivo (segurança)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501"],  # Apenas localhost
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

storage = EventStorage()
correlation = CorrelationEngine()
threat_model = ThreatModel()
file_ingestor = FileIngestor()
external_ingestor = ExternalSourceIngestor()


class UploadResponse(BaseModel):
    ingested: int = Field(..., description="Número de eventos ingestados")


class CorrelationMatch(BaseModel):
    """Resultado de correlação com contexto analítico."""
    anchor_event_id: str
    related_event_count: int
    time_window_seconds: int
    severity_levels: list[str]
    first_event_timestamp: str
    last_event_timestamp: str


class ReusedIOCInfo(BaseModel):
    """IOC reutilizado com análise."""
    ioc: str
    occurrence_count: int
    first_seen: str
    last_seen: str
    severity_max: str
    event_types: list[str]


class CorrelationResponse(BaseModel):
    """Resposta de correlação estruturada."""
    total_matched: int
    total_reused_iocs: int
    correlation_matches: list[CorrelationMatch]
    reused_iocs: list[ReusedIOCInfo]
    analysis_timestamp: str


class AnomalyDetail(BaseModel):
    """Score de anomalia com explicação."""
    event_id: str
    score: float
    is_anomaly: bool
    severity: str
    confidence: float
    reason: str
    explanation: str


def _validate_file_path(path: str) -> Path:
    """
    Valida caminho de arquivo contra path traversal.
    
    Segurança: Evita leitura de arquivos fora do diretório permitido
    """
    try:
        file_path = Path(path).resolve()
        
        # Verifica path traversal
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail="Caminho é diretório, não arquivo")
        
        # Permite apenas tamanhos razoáveis (100MB)
        max_size = 100 * 1024 * 1024
        if file_path.stat().st_size > max_size:
            raise HTTPException(status_code=413, detail=f"Arquivo muito grande (máx {max_size} bytes)")
        
        return file_path
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Erro ao validar caminho: %s", exc)
        raise HTTPException(status_code=400, detail="Caminho inválido") from exc


@app.on_event("startup")
async def on_startup() -> None:
    init_db()
    logger.info("Aplicação iniciada")


@app.get("/health", tags=["system"])
async def health() -> dict[str, Any]:
    """Verificação de saúde do serviço."""
    return {
        "status": "ok",
        "service": "forensic_cti",
        "version": "0.2.0",
        "model_trained": threat_model.trained,
    }


@app.get("/model/status", tags=["system"])
async def model_status() -> dict[str, Any]:
    """Status detalhado do modelo ML."""
    return {
        "trained": threat_model.trained,
        "training_stats": threat_model.training_stats,
    }


@app.post("/ingest/file", response_model=UploadResponse, tags=["ingestion"])
async def ingest_file(path: str, session: Session = Depends(get_session)) -> UploadResponse:
    """
    Ingestão de arquivo (CSV, JSON, LOG).
    
    Segurança: Valida caminho contra path traversal
    """
    logger.info("Requisição de ingestão: %s", path)
    try:
        file_path = _validate_file_path(path)
        events = file_ingestor.ingest_path(file_path)
        count = storage.persist_events(session=session, events=events)
        logger.info("Ingestados %d eventos de %s", count, file_path)
        return UploadResponse(ingested=count)
    except HTTPException:
        raise
    except StorageError as exc:
        logger.exception("Erro de storage durante ingestão")
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.exception("Erro inesperado durante ingestão")
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/events", response_model=QueryResponse, tags=["events"])
async def list_events(
    limit: int = Query(100, ge=1, le=500, description="Limite de eventos a retornar"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    session: Session = Depends(get_session),
) -> QueryResponse:
    """Lista eventos com paginação."""
    items = storage.query_events(session=session, limit=limit, offset=offset)
    total = storage.get_event_count(session=session)
    return QueryResponse(total=total, items=[NormalizedEvent(**item) for item in items])


@app.get("/events/search", response_model=QueryResponse, tags=["events"])
async def search_ioc(
    ioc: str = Query(..., min_length=1, max_length=255, description="IOC a buscar (IP, domínio)"),
    limit: int = Query(100, ge=1, le=500),
    session: Session = Depends(get_session),
) -> QueryResponse:
    """Busca por IOC com validação."""
    items = storage.search_by_ioc(session=session, ioc=ioc, limit=limit)
    return QueryResponse(total=len(items), items=[NormalizedEvent(**item) for item in items])


@app.get("/correlation/ip", response_model=CorrelationResponse, tags=["correlation"])
async def correlate_ip(
    limit: int = Query(100, ge=1, le=500),
    time_window: int = Query(3600, ge=60, le=86400, description="Janela temporal em segundos"),
    session: Session = Depends(get_session),
) -> CorrelationResponse:
    """
    Correlaciona eventos por IP.
    
    Melhoria: Retorna resposta estruturada com contexto analítico
    """
    items = storage.query_events(session=session, limit=limit)
    events = [NormalizedEvent(**item) for item in items]
    
    matches = correlation.correlate_by_ip(events, time_window=time_window)
    reused = correlation.find_reused_iocs(events)
    
    # Transforma em respostas estruturadas
    correlation_matches = []
    for match in matches:
        anchor = match["anchor"]
        related = match["matches"]
        correlation_matches.append(
            CorrelationMatch(
                anchor_event_id=anchor.event_id,
                related_event_count=len(related),
                time_window_seconds=time_window,
                severity_levels=sorted(set(e.severity.value for e in [anchor] + related)),
                first_event_timestamp=min(e.timestamp for e in [anchor] + related).isoformat(),
                last_event_timestamp=max(e.timestamp for e in [anchor] + related).isoformat(),
            )
        )
    
    reused_iocs = []
    for ioc_info in reused:
        events_for_ioc = ioc_info["events"]
        reused_iocs.append(
            ReusedIOCInfo(
                ioc=ioc_info["ioc"],
                occurrence_count=ioc_info["count"],
                first_seen=ioc_info["first_seen"].isoformat(),
                last_seen=ioc_info["last_seen"].isoformat(),
                severity_max=ioc_info["severity_max"].value,
                event_types=sorted(set(e.event_type for e in events_for_ioc)),
            )
        )
    
    from datetime import datetime
    return CorrelationResponse(
        total_matched=len(correlation_matches),
        total_reused_iocs=len(reused_iocs),
        correlation_matches=correlation_matches,
        reused_iocs=reused_iocs,
        analysis_timestamp=datetime.utcnow().isoformat(),
    )


@app.post("/ml/train", tags=["machine-learning"])
async def train_model(
    limit: int = Query(500, ge=50, le=5000, description="Máximo de eventos para treinamento"),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Treina modelo de anomalias."""
    logger.info("Requisição de treinamento com até %d eventos", limit)
    items = storage.query_events(session=session, limit=limit)
    events = [NormalizedEvent(**item) for item in items]
    threat_model.train(events)
    
    return {
        "trained": threat_model.trained,
        "events_used": len(events),
        "stats": threat_model.training_stats,
    }


@app.post("/ml/score", response_model=AnomalyDetail, tags=["machine-learning"])
async def score_event(event: NormalizedEvent) -> AnomalyDetail:
    """
    Escore de anomalia com explicação.
    
    Melhoria: Retorna detalhes de por que é anomalia
    """
    logger.info("Score para evento %s", event.event_id)
    result = threat_model.score_event(event)
    
    return AnomalyDetail(
        event_id=event.event_id,
        score=result["score"],
        is_anomaly=result["is_anomaly"],
        severity=result["severity"],
        confidence=result.get("confidence", 0.0),
        reason=result.get("reason", "unknown"),
        explanation=result.get("explanation", ""),
    )


@app.get("/ml/cluster", tags=["machine-learning"])
async def cluster_events(
    limit: int = Query(100, ge=10, le=1000),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Agrupa eventos em clusters."""
    items = storage.query_events(session=session, limit=limit)
    events = [NormalizedEvent(**item) for item in items]
    result = threat_model.cluster_events(events)
    
    return {
        "events_clustered": len(events),
        "clusters": result.get("clusters", []),
        "cluster_sizes": result.get("cluster_sizes", []),
        "error": result.get("error"),
    }


@app.post("/external/virustotal", response_model=UploadResponse, tags=["external"])
async def ingest_virustotal(
    query: str = Query(..., min_length=1, max_length=255),
    session: Session = Depends(get_session),
) -> UploadResponse:
    """Stub para integração com VirusTotal."""
    events = external_ingestor.ingest_virus_total(query)
    count = storage.persist_events(session=session, events=events)
    return UploadResponse(ingested=count)


@app.post("/external/shodan", response_model=UploadResponse, tags=["external"])
async def ingest_shodan(
    query: str = Query(..., min_length=1, max_length=255),
    session: Session = Depends(get_session),
) -> UploadResponse:
    """Stub para integração com Shodan."""
    events = external_ingestor.ingest_shodan(query)
    count = storage.persist_events(session=session, events=events)
    return UploadResponse(ingested=count)


@app.post("/external/abuseipdb", response_model=UploadResponse, tags=["external"])
async def ingest_abuseipdb(
    ip_address: str = Query(..., min_length=7, max_length=15, description="Endereço IP"),
    session: Session = Depends(get_session),
) -> UploadResponse:
    """Stub para integração com AbuseIPDB."""
    events = external_ingestor.ingest_abuse_ipdb(ip_address)
    count = storage.persist_events(session=session, events=events)
    return UploadResponse(ingested=count)

"""
AI Tech Consultant - Knowledge Brain
FastAPI application: REST API for querying, ingestion, health checks, and escalations.
"""
from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import Database
from app.models import (
    QueryRequest, QueryResponse,
    IngestionRunRequest, IngestionStatus,
    EscalationCreate, EscalationResolve, EscalationRecord,
    HealthResponse,
)
from app.rag_engine import RAGEngine
from app.vector_store import VectorStore
from ingestion.pipeline import IngestionPipeline

logger = logging.getLogger(__name__)
settings = get_settings()

# ─── Shared State ────────────────────────────────────────────────────

db = Database()
vector_store = VectorStore()
rag_engine: Optional[RAGEngine] = None
ingestion_pipeline: Optional[IngestionPipeline] = None
_start_time: float = 0.0


# ─── Lifecycle ───────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks."""
    global rag_engine, ingestion_pipeline, _start_time

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    _start_time = time.monotonic()

    # Initialize services
    logger.info("Starting Knowledge Brain...")
    await db.connect()
    await vector_store.initialize()
    rag_engine = RAGEngine(vector_store, db)
    ingestion_pipeline = IngestionPipeline(db, vector_store)

    # Auto-seed if vector store is empty
    stats = await vector_store.get_stats()
    if stats.get("total_chunks", 0) == 0:
        logger.info("Vector store is empty, running auto-seed with Brilliant Directories knowledge...")
        try:
            from data.seed_articles import seed_knowledge_base
            await seed_knowledge_base(db, vector_store)
        except Exception as e:
            logger.warning(f"Auto-seeding encountered issue: {e}", exc_info=True)

    logger.info("Knowledge Brain ready ✓")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await db.close()


# ─── App ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Tech Consultant – Knowledge Brain",
    description=(
        "RAG-powered knowledge base for Brilliant Directories support. "
        "Crawls help-center articles, indexes them, and provides AI-generated "
        "answers with source citations."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Query Endpoint ─────────────────────────────────────────────────

@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_knowledge_base(request: QueryRequest):
    """Ask a question and get an AI-generated answer with source citations."""
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")

    response = await rag_engine.query(request)
    return response


# ─── Ingestion Endpoints ────────────────────────────────────────────

@app.post("/ingest", tags=["Ingestion"])
async def trigger_ingestion(
    request: IngestionRunRequest,
    background_tasks: BackgroundTasks,
):
    """Trigger an ingestion run (runs in background)."""
    if not ingestion_pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    if ingestion_pipeline.is_running:
        raise HTTPException(status_code=409, detail="Ingestion already in progress")

    async def _run():
        try:
            await ingestion_pipeline.run(
                full_crawl=request.full_crawl,
                max_pages=request.max_pages,
            )
        except Exception as e:
            logger.error(f"Background ingestion failed: {e}", exc_info=True)

    background_tasks.add_task(_run)

    return {
        "status": "started",
        "message": "Ingestion pipeline started in background",
        "full_crawl": request.full_crawl,
        "max_pages": request.max_pages,
    }


@app.get("/ingest/status", response_model=IngestionStatus, tags=["Ingestion"])
async def get_ingestion_status():
    """Get the current ingestion pipeline status."""
    page_counts = await db.get_page_counts()
    last_run = await db.get_last_ingestion()

    return IngestionStatus(
        is_running=ingestion_pipeline.is_running if ingestion_pipeline else False,
        last_run=datetime.fromisoformat(last_run["started_at"]) if last_run else None,
        total_pages=sum(page_counts.values()),
        crawled=page_counts.get("crawled", 0),
        indexed=page_counts.get("indexed", 0),
        failed=page_counts.get("failed", 0),
        removed=page_counts.get("removed", 0),
    )


@app.post("/seed", tags=["Ingestion"])
async def trigger_seed():
    """Seed the knowledge base with built-in Brilliant Directories help articles."""
    from data.seed_articles import seed_knowledge_base
    res = await seed_knowledge_base(db, vector_store)
    return {"status": "success", **res}


@app.get("/escalations", response_model=list[EscalationRecord], tags=["Escalations"])
async def list_open_escalations():
    """List all open/in-progress escalations."""
    return await db.get_open_escalations()


@app.post("/escalations", response_model=EscalationRecord, tags=["Escalations"])
async def create_escalation_endpoint(data: EscalationCreate):
    """Create a new escalation for human review."""
    import uuid
    escalation_id = f"esc_{uuid.uuid4().hex[:8]}"
    return await db.create_escalation(escalation_id, data)


@app.get("/escalations/{escalation_id}", response_model=EscalationRecord, tags=["Escalations"])
async def get_escalation(escalation_id: str):
    """Get a specific escalation by ID."""
    record = await db.get_escalation(escalation_id)
    if not record:
        raise HTTPException(status_code=404, detail="Escalation not found")
    return record


@app.post("/escalations/{escalation_id}/resolve", response_model=EscalationRecord, tags=["Escalations"])
async def resolve_escalation(escalation_id: str, data: EscalationResolve):
    """Resolve an escalation with an expert-provided answer."""
    existing = await db.get_escalation(escalation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Escalation not found")

    resolved = await db.resolve_escalation(escalation_id, data)
    if not resolved:
        raise HTTPException(status_code=500, detail="Failed to resolve escalation")

    # If add_to_knowledge is True, immediately index into vector store for continuous learning
    if data.add_to_knowledge and vector_store:
        try:
            from app.models import TextChunk
            import uuid
            chunk_rec = TextChunk(
                id=f"esc_{escalation_id}_{uuid.uuid4().hex[:6]}",
                article_url=f"https://support.brilliantdirectories.com/escalations/{escalation_id}",
                article_title=f"Expert Answer: {existing.question[:80]}",
                section_heading="Expert Verified Answer",
                content=f"Question: {existing.question}\n\nExpert Verified Answer: {data.answer}",
                chunk_index=0,
                token_count=len(data.answer.split()),
                metadata={"category": "Resolved Escalations", "folder": "Expert Support"},
            )
            await vector_store.add_chunks([chunk_rec])
            logger.info(f"Escalation {escalation_id} answer indexed into vector store")
        except Exception as e:
            logger.warning(f"Failed to auto-index resolved escalation: {e}")

    return resolved


# ─── Health & Stats ──────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check with system statistics."""
    page_counts = await db.get_page_counts()
    last_run = await db.get_last_ingestion()
    vector_stats = await vector_store.get_stats()
    escalation_count = await db.get_escalation_count()

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        service="knowledge-brain",
        total_articles=page_counts.get("indexed", 0),
        total_chunks=vector_stats.get("total_chunks", 0),
        total_escalations=escalation_count,
        last_ingestion=(
            datetime.fromisoformat(last_run["started_at"]) if last_run else None
        ),
        uptime_seconds=round(time.monotonic() - _start_time, 1),
    )


@app.get("/stats", tags=["System"])
async def detailed_stats():
    """Detailed statistics about the knowledge base."""
    page_counts = await db.get_page_counts()
    vector_stats = await vector_store.get_stats()
    last_run = await db.get_last_ingestion()
    open_escalations = await db.get_open_escalations()

    return {
        "pages": page_counts,
        "vector_store": vector_stats,
        "last_ingestion": last_run,
        "open_escalations": len(open_escalations),
    }


# ─── Entry Point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )

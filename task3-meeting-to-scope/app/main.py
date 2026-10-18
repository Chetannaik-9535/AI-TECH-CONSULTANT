"""
AI Tech Consultant - Meeting to Scope
FastAPI REST API & Interactive Discovery Scoping Dashboard on Port 8001.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.models import (
    MeetingInput, MeetingMetadata, DiscoveryAnalysis, ScopeOfWork,
)
from app.extractor import MeetingExtractor
from app.scope_generator import ScopeGenerator
from data.seed_meetings import SEED_MEETINGS

logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title="AI Tech Consultant – Meeting to Scope",
    description="Analyzes discovery call transcripts, extracts technical requirements, and generates professional Scopes of Work (SOW) for Brilliant Directories projects.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage initialized from seed meetings
meetings_db: dict[str, MeetingInput] = {}
sows_db: dict[str, ScopeOfWork] = {}

extractor = MeetingExtractor()
generator = ScopeGenerator(hourly_rate=settings.default_hourly_rate)

# Initialize seed meetings
for m in SEED_MEETINGS:
    meta = MeetingMetadata(**m["metadata"])
    meetings_db[meta.id] = MeetingInput(
        metadata=meta,
        transcript=m["transcript"],
        custom_notes=m.get("custom_notes", "")
    )

# Static and Templates paths
BASE_DIR = Path(__file__).parent.parent
static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)
(static_dir / "css").mkdir(parents=True, exist_ok=True)
(static_dir / "js").mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ─── API Endpoints ───────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "meeting-to-scope",
        "port": settings.port,
        "meetings_count": len(meetings_db),
        "sows_count": len(sows_db),
    }


@app.get("/api/meetings", tags=["Meetings"])
async def list_meetings():
    """List all discovery meetings available for analysis."""
    return [
        {
            "id": m.metadata.id,
            "title": m.metadata.title,
            "client_name": m.metadata.client_name,
            "client_company": m.metadata.client_company,
            "date": m.metadata.date,
            "duration_minutes": m.metadata.duration_minutes,
            "participants": m.metadata.participants,
            "has_custom_notes": bool(m.custom_notes),
            "transcript_preview": m.transcript[:180] + "...",
        }
        for m in meetings_db.values()
    ]


@app.get("/api/meetings/{meeting_id}", tags=["Meetings"])
async def get_meeting(meeting_id: str):
    """Retrieve full transcript and metadata for a specific meeting."""
    if meeting_id not in meetings_db:
        raise HTTPException(status_code=404, detail="Meeting transcript not found")
    return meetings_db[meeting_id]


@app.post("/api/meetings", tags=["Meetings"])
async def create_meeting(meeting_input: MeetingInput):
    """Upload or ingest a new client discovery meeting transcript."""
    m_id = meeting_input.metadata.id
    if not m_id:
        m_id = f"MEET-{len(meetings_db) + 2001}"
        meeting_input.metadata.id = m_id

    meetings_db[m_id] = meeting_input
    logger.info(f"Ingested meeting transcript: {m_id} - {meeting_input.metadata.title}")
    return meeting_input


@app.post("/api/meetings/{meeting_id}/analyze", response_model=DiscoveryAnalysis, tags=["Scoping Engine"])
async def analyze_meeting(meeting_id: str):
    """Run requirement extraction & discovery analysis on the meeting."""
    if meeting_id not in meetings_db:
        raise HTTPException(status_code=404, detail="Meeting transcript not found")

    meeting = meetings_db[meeting_id]
    analysis = await extractor.analyze_meeting(meeting)
    return analysis


@app.post("/api/meetings/{meeting_id}/generate-sow", response_model=ScopeOfWork, tags=["Scoping Engine"])
async def generate_sow_for_meeting(
    meeting_id: str,
    hourly_rate: Optional[float] = None,
):
    """Analyze meeting and generate full Scope of Work document."""
    if meeting_id not in meetings_db:
        raise HTTPException(status_code=404, detail="Meeting transcript not found")

    meeting = meetings_db[meeting_id]
    analysis = await extractor.analyze_meeting(meeting)
    rate = hourly_rate if hourly_rate and hourly_rate > 0 else settings.default_hourly_rate
    sow = generator.generate_sow(analysis, custom_rate=rate)

    sows_db[sow.sow_id] = sow
    return sow


@app.get("/api/sow/{sow_id}", response_model=ScopeOfWork, tags=["Scoping Engine"])
async def get_sow(sow_id: str):
    """Retrieve a previously generated Scope of Work."""
    if sow_id not in sows_db:
        raise HTTPException(status_code=404, detail="Scope of Work document not found")
    return sows_db[sow_id]


@app.get("/api/sow/{sow_id}/markdown", response_class=PlainTextResponse, tags=["Scoping Engine"])
async def download_sow_markdown(sow_id: str):
    """Download raw Markdown format of the Scope of Work."""
    if sow_id not in sows_db:
        raise HTTPException(status_code=404, detail="Scope of Work document not found")
    return sows_db[sow_id].markdown_document


# ─── Frontend Dashboard Serving ──────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
async def render_dashboard():
    """Serve the interactive Meeting to Scope web dashboard."""
    template_path = BASE_DIR / "templates" / "index.html"
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")
    return "<h1>Meeting to Scope Dashboard initializing...</h1>"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )

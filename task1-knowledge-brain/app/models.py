"""
AI Tech Consultant - Knowledge Brain
Pydantic models for API requests, responses, and internal data structures.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ─── Enums ───────────────────────────────────────────────────────────

class PageStatus(str, Enum):
    PENDING = "pending"
    CRAWLED = "crawled"
    PARSED = "parsed"
    CHUNKED = "chunked"
    INDEXED = "indexed"
    FAILED = "failed"
    REMOVED = "removed"


class AnswerStatus(str, Enum):
    ANSWERED = "answered"
    PARTIAL = "partial"
    INSUFFICIENT = "insufficient"
    ESCALATED = "escalated"
    ERROR = "error"


class EscalationStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


# ─── Ingestion Models ────────────────────────────────────────────────

class SitemapEntry(BaseModel):
    """A single URL entry from the sitemap XML."""
    url: str
    lastmod: Optional[str] = None
    changefreq: Optional[str] = None
    priority: Optional[float] = None


class PageRecord(BaseModel):
    """Tracks the ingestion state of one help-center page."""
    id: Optional[int] = None
    url: str
    status: PageStatus = PageStatus.PENDING
    content_hash: Optional[str] = None
    title: Optional[str] = None
    last_crawled: Optional[datetime] = None
    last_modified: Optional[str] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ArticleImage(BaseModel):
    """An image found within a help-center article."""
    id: Optional[int] = None
    article_url: str
    image_url: str
    alt_text: Optional[str] = None
    context_text: Optional[str] = None  # surrounding text
    description: Optional[str] = None  # AI-generated description
    position_index: int = 0
    processed: bool = False


class ArticleContent(BaseModel):
    """Parsed content from a single help-center article."""
    url: str
    title: str
    category: Optional[str] = None
    folder: Optional[str] = None
    content_text: str
    content_html: Optional[str] = None
    headings: list[str] = Field(default_factory=list)
    images: list[ArticleImage] = Field(default_factory=list)
    content_hash: str = ""
    word_count: int = 0
    parsed_at: datetime = Field(default_factory=datetime.utcnow)


class TextChunk(BaseModel):
    """A meaningful section of an article for embedding and retrieval."""
    id: Optional[str] = None
    article_url: str
    article_title: str
    section_heading: Optional[str] = None
    content: str
    chunk_index: int = 0
    token_count: int = 0
    image_refs: list[str] = Field(default_factory=list)
    image_descriptions: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


# ─── API Models ──────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    """Request to ask a question to the Knowledge Brain."""
    question: str = Field(..., min_length=3, max_length=2000, description="The question to ask")
    max_sources: int = Field(default=5, ge=1, le=10)
    include_images: bool = Field(default=True)
    conversation_id: Optional[str] = None


class SourceReference(BaseModel):
    """A cited source used in the answer."""
    title: str
    url: str
    section: Optional[str] = None
    relevance_score: float = Field(ge=0.0, le=1.0)
    snippet: Optional[str] = None


class ImageReference(BaseModel):
    """An image relevant to the answer."""
    image_url: str
    article_url: str
    description: str
    relevance: Optional[str] = None


class QueryResponse(BaseModel):
    """Response from the Knowledge Brain query endpoint."""
    answer: str
    status: AnswerStatus
    sources: list[SourceReference] = Field(default_factory=list)
    images: list[ImageReference] = Field(default_factory=list)
    confidence_note: Optional[str] = None
    needs_human: bool = False
    escalation_id: Optional[str] = None
    request_id: str = ""
    model_used: str = ""
    latency_ms: float = 0.0
    token_usage: dict = Field(default_factory=dict)


class IngestionRunRequest(BaseModel):
    """Request to trigger an ingestion job."""
    full_crawl: bool = Field(default=False, description="Force full re-crawl")
    max_pages: Optional[int] = Field(default=None, description="Limit pages to process")


class IngestionStatus(BaseModel):
    """Status of the ingestion pipeline."""
    is_running: bool = False
    last_run: Optional[datetime] = None
    total_pages: int = 0
    crawled: int = 0
    indexed: int = 0
    failed: int = 0
    removed: int = 0
    new_since_last: int = 0
    updated_since_last: int = 0
    next_scheduled: Optional[datetime] = None


class EscalationCreate(BaseModel):
    """Create a human escalation task."""
    question: str
    context: Optional[str] = None
    retrieved_sources: list[str] = Field(default_factory=list)
    reason: str = "insufficient_evidence"


class EscalationResolve(BaseModel):
    """Resolve an escalation with an expert answer."""
    answer: str
    expert_name: Optional[str] = None
    supporting_urls: list[str] = Field(default_factory=list)
    add_to_knowledge: bool = Field(default=True)


class EscalationRecord(BaseModel):
    """A recorded escalation with its resolution."""
    id: str
    question: str
    context: Optional[str] = None
    reason: str
    status: EscalationStatus = EscalationStatus.OPEN
    answer: Optional[str] = None
    expert_name: Optional[str] = None
    supporting_urls: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    service: str = "knowledge-brain"
    total_articles: int = 0
    total_chunks: int = 0
    total_escalations: int = 0
    last_ingestion: Optional[datetime] = None
    uptime_seconds: float = 0.0

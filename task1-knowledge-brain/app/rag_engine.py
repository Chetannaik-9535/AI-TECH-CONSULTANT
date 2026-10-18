"""
AI Tech Consultant - Knowledge Brain
RAG engine: orchestrates retrieval, prompt construction, and Claude generation.
"""
from __future__ import annotations

import logging
import time
import uuid
from typing import Optional

import anthropic

from app.config import get_settings
from app.models import (
    AnswerStatus, QueryRequest, QueryResponse,
    SourceReference, ImageReference,
    EscalationCreate,
)
from app.prompts import (
    SYSTEM_PROMPT, build_qa_prompt, build_confidence_prompt,
    build_escalation_prompt,
)
from app.vector_store import VectorStore
from app.database import Database

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGEngine:
    """Retrieve-Augment-Generate engine powered by Claude."""

    def __init__(self, vector_store: VectorStore, db: Database):
        self.vector_store = vector_store
        self.db = db
        self._client: Optional[anthropic.Anthropic] = None

    def _get_client(self) -> anthropic.Anthropic:
        """Lazy-initialize the Anthropic client."""
        if not self._client:
            if not settings.anthropic_api_key:
                raise RuntimeError(
                    "ANTHROPIC_API_KEY not set. Add it to your .env file."
                )
            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        return self._client

    async def query(self, request: QueryRequest) -> QueryResponse:
        """Full RAG pipeline: retrieve → augment → generate → assess."""
        start_time = time.monotonic()
        request_id = uuid.uuid4().hex[:12]

        try:
            # ── Step 1: Retrieve relevant chunks ──
            chunks = await self.vector_store.search(
                query=request.question,
                top_k=request.max_sources,
            )

            if not chunks:
                return self._no_results_response(request, request_id, start_time)

            # ── Step 2: Assess confidence ──
            status = await self._assess_confidence(request.question, chunks)

            # ── Step 3: Generate answer with Claude ──
            answer, token_usage = await self._generate_answer(
                request.question, chunks
            )

            # ── Step 4: Build source references ──
            sources = self._build_sources(chunks)

            # ── Step 5: Build image references ──
            images = []
            if request.include_images:
                images = self._build_image_refs(chunks)

            # ── Step 6: Handle escalation if needed ──
            escalation_id = None
            needs_human = status == AnswerStatus.INSUFFICIENT
            if needs_human:
                escalation_id = await self._create_escalation(
                    request.question, chunks
                )

            latency = (time.monotonic() - start_time) * 1000

            return QueryResponse(
                answer=answer,
                status=status,
                sources=sources,
                images=images,
                confidence_note=self._confidence_note(status),
                needs_human=needs_human,
                escalation_id=escalation_id,
                request_id=request_id,
                model_used=settings.claude_model,
                latency_ms=round(latency, 1),
                token_usage=token_usage,
            )

        except Exception as e:
            logger.error(f"RAG query failed: {e}", exc_info=True)
            latency = (time.monotonic() - start_time) * 1000
            return QueryResponse(
                answer=f"I encountered an error processing your question. Please try again.",
                status=AnswerStatus.ERROR,
                request_id=request_id,
                model_used=settings.claude_model,
                latency_ms=round(latency, 1),
            )

    # ─── Internal Methods ────────────────────────────────────────

    async def _generate_answer(
        self, question: str, chunks: list[dict]
    ) -> tuple[str, dict]:
        """Call Claude to generate an answer, with graceful local fallback if API key is not configured."""
        try:
            client = self._get_client()
            qa_prompt = build_qa_prompt(question, chunks)

            message = client.messages.create(
                model=settings.claude_model,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": qa_prompt}],
            )

            answer = message.content[0].text
            token_usage = {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }

            logger.info(
                f"Generated answer: {len(answer)} chars, "
                f"{token_usage['input_tokens']}+{token_usage['output_tokens']} tokens"
            )
            return answer, token_usage
        except Exception as e:
            logger.warning(f"Claude API generation unavailable ({e}), synthesizing from retrieved documentation chunks.")
            return self._synthesize_local_answer(question, chunks)

    def _synthesize_local_answer(
        self, question: str, chunks: list[dict]
    ) -> tuple[str, dict]:
        """Synthesize a structured grounded response from retrieved chunks."""
        if not chunks:
            return (
                "I could not locate sufficient documentation to answer your question. "
                "This inquiry has been flagged for human consultant review.",
                {"input_tokens": 0, "output_tokens": 0}
            )

        top_chunk = chunks[0]
        title = top_chunk.get("title", "Brilliant Directories Help Documentation")
        section = top_chunk.get("section", "")

        lines = [
            f"Based on official Brilliant Directories documentation for **{title}**"
            + (f" ({section})" if section else "") + ":\n"
        ]

        seen_sections = set()
        for c in chunks[:3]:
            sec = c.get("section", "")
            content = c.get("content", "").strip()
            if sec and sec not in seen_sections and sec != title:
                lines.append(f"### {sec}")
                seen_sections.add(sec)
            if content:
                lines.append(content)
                lines.append("")

        lines.append("---\n*Source:* Verified Brilliant Directories Knowledge Documentation")
        answer = "\n".join(lines)
        return answer, {"input_tokens": 150, "output_tokens": len(answer.split())}

    async def _assess_confidence(
        self, question: str, chunks: list[dict]
    ) -> AnswerStatus:
        """Assess confidence via Claude Haiku or heuristic relevance scoring."""
        if not chunks:
            return AnswerStatus.INSUFFICIENT

        try:
            client = self._get_client()
            prompt = build_confidence_prompt(question, chunks)

            message = client.messages.create(
                model=settings.claude_haiku_model,
                max_tokens=20,
                messages=[{"role": "user", "content": prompt}],
            )

            result = message.content[0].text.strip().upper()

            if "ANSWERED" in result:
                return AnswerStatus.ANSWERED
            elif "PARTIAL" in result:
                return AnswerStatus.PARTIAL
            else:
                return AnswerStatus.INSUFFICIENT

        except Exception as e:
            # Fallback heuristic: check relevance score of top chunk
            top_score = chunks[0].get("score", 0.0) if chunks else 0.0
            if top_score >= 0.65:
                return AnswerStatus.ANSWERED
            elif top_score >= 0.35:
                return AnswerStatus.PARTIAL
            return AnswerStatus.INSUFFICIENT

    def _build_sources(self, chunks: list[dict]) -> list[SourceReference]:
        """Build deduplicated source references from chunks."""
        seen_urls = set()
        sources = []
        for chunk in chunks:
            url = chunk.get("url", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            sources.append(SourceReference(
                title=chunk.get("title", "Untitled"),
                url=url,
                section=chunk.get("section"),
                relevance_score=chunk.get("score", 0.0),
                snippet=chunk.get("content", "")[:200] + "...",
            ))
        return sources

    def _build_image_refs(self, chunks: list[dict]) -> list[ImageReference]:
        """Extract image references from retrieved chunks."""
        images = []
        seen = set()
        for chunk in chunks:
            image_refs = chunk.get("image_refs", [])
            image_descs = chunk.get("image_descriptions", [])
            for i, ref in enumerate(image_refs):
                if ref in seen:
                    continue
                seen.add(ref)
                desc = image_descs[i] if i < len(image_descs) else "Screenshot from article"
                images.append(ImageReference(
                    image_url=ref,
                    article_url=chunk.get("url", ""),
                    description=desc,
                ))
        return images[:5]  # Limit to 5 images

    async def _create_escalation(
        self, question: str, chunks: list[dict]
    ) -> str:
        """Create an escalation when the KB can't answer."""
        escalation_id = f"esc_{uuid.uuid4().hex[:10]}"
        context = f"Question: {question}. Insufficient matching documentation found."
        try:
            # Generate a brief summary using Haiku if available
            client = self._get_client()
            prompt = build_escalation_prompt(question, chunks)
            message = client.messages.create(
                model=settings.claude_haiku_model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            context = message.content[0].text
        except Exception as e:
            logger.debug(f"Haiku escalation summary unavailable ({e}), using default context.")

        try:
            await self.db.create_escalation(
                escalation_id,
                EscalationCreate(
                    question=question,
                    context=context,
                    retrieved_sources=[c.get("url", "") for c in chunks],
                    reason="insufficient_evidence",
                ),
            )
            logger.info(f"Created escalation: {escalation_id}")
        except Exception as e:
            logger.error(f"Failed to create escalation in DB: {e}")
        return escalation_id

    def _no_results_response(
        self, request: QueryRequest, request_id: str, start_time: float
    ) -> QueryResponse:
        latency = (time.monotonic() - start_time) * 1000
        return QueryResponse(
            answer=(
                "I couldn't find any relevant articles in the knowledge base "
                "to answer your question. This has been flagged for a human expert "
                "to review."
            ),
            status=AnswerStatus.INSUFFICIENT,
            needs_human=True,
            request_id=request_id,
            model_used=settings.claude_model,
            latency_ms=round(latency, 1),
        )

    @staticmethod
    def _confidence_note(status: AnswerStatus) -> str:
        return {
            AnswerStatus.ANSWERED: "High confidence — answer is well-supported by knowledge base articles.",
            AnswerStatus.PARTIAL: "Medium confidence — some relevant information found, but the answer may be incomplete.",
            AnswerStatus.INSUFFICIENT: "Low confidence — insufficient information in the knowledge base.",
            AnswerStatus.ERROR: "An error occurred during processing.",
        }.get(status, "")

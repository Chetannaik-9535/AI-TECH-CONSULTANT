"""
AI Tech Consultant - Knowledge Brain
Semantic text chunker: splits parsed articles into embedding-ready chunks
with section awareness, overlap, and metadata preservation.
"""
from __future__ import annotations

import logging
import re
import uuid
from typing import Optional

import tiktoken

from app.config import get_settings
from app.models import ArticleContent, TextChunk

logger = logging.getLogger(__name__)
settings = get_settings()

# Use cl100k_base (same tokenizer as text-embedding-3-small/large)
_encoder = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Count tokens using the embedding model's tokenizer."""
    return len(_encoder.encode(text))


class ArticleChunker:
    """Split articles into overlapping, section-aware chunks for embedding."""

    def __init__(
        self,
        chunk_size: int = settings.chunk_size,
        chunk_overlap: int = settings.chunk_overlap,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_article(self, article: ArticleContent) -> list[TextChunk]:
        """Split one article into semantically meaningful chunks."""
        sections = self._split_into_sections(article.content_text)

        if not sections:
            # No headings found — treat entire text as one section
            sections = [("General", article.content_text)]

        chunks: list[TextChunk] = []
        chunk_index = 0

        for section_heading, section_text in sections:
            section_chunks = self._split_section(section_text)

            for text in section_chunks:
                token_count = count_tokens(text)
                if token_count < 20:
                    # Skip tiny fragments
                    continue

                # Find image references within this chunk
                image_refs = []
                image_descs = []
                for img in article.images:
                    if img.context_text and self._text_overlaps(text, img.context_text):
                        image_refs.append(img.image_url)
                        if img.description:
                            image_descs.append(img.description)
                        elif img.alt_text:
                            image_descs.append(img.alt_text)

                chunk = TextChunk(
                    id=self._generate_chunk_id(article.url, chunk_index),
                    article_url=article.url,
                    article_title=article.title,
                    section_heading=section_heading,
                    content=text,
                    chunk_index=chunk_index,
                    token_count=token_count,
                    image_refs=image_refs,
                    image_descriptions=image_descs,
                    metadata={
                        "category": article.category or "",
                        "folder": article.folder or "",
                        "word_count": len(text.split()),
                        "has_images": len(image_refs) > 0,
                    },
                )
                chunks.append(chunk)
                chunk_index += 1

        logger.debug(
            f"Chunked '{article.title}' → {len(chunks)} chunks "
            f"(avg {sum(c.token_count for c in chunks) // max(len(chunks), 1)} tokens)"
        )
        return chunks

    def chunk_articles(self, articles: list[ArticleContent]) -> list[TextChunk]:
        """Chunk multiple articles."""
        all_chunks = []
        for article in articles:
            all_chunks.extend(self.chunk_article(article))
        logger.info(f"Total chunks from {len(articles)} articles: {len(all_chunks)}")
        return all_chunks

    # ─── Internal Methods ────────────────────────────────────────

    def _split_into_sections(self, text: str) -> list[tuple[str, str]]:
        """Split text by markdown-style headings (## Heading)."""
        # Match lines starting with # (markdown heading notation from parser)
        heading_pattern = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)
        matches = list(heading_pattern.finditer(text))

        if not matches:
            return []

        sections = []

        # Text before first heading
        pre_heading = text[: matches[0].start()].strip()
        if pre_heading and len(pre_heading) > 30:
            sections.append(("Introduction", pre_heading))

        # Each heading section
        for i, match in enumerate(matches):
            heading = match.group(2).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()

            if body and len(body) > 20:
                sections.append((heading, body))

        return sections

    def _split_section(self, text: str) -> list[str]:
        """Split a section into chunks with overlap if it's too long."""
        token_count = count_tokens(text)

        if token_count <= self.chunk_size:
            return [text.strip()]

        # Split by paragraphs first
        paragraphs = re.split(r"\n\s*\n", text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        chunks = []
        current_parts: list[str] = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = count_tokens(para)

            # If a single paragraph exceeds chunk_size, split by sentences
            if para_tokens > self.chunk_size:
                # Flush current buffer
                if current_parts:
                    chunks.append("\n\n".join(current_parts))
                    current_parts = []
                    current_tokens = 0

                sentence_chunks = self._split_by_sentences(para)
                chunks.extend(sentence_chunks)
                continue

            if current_tokens + para_tokens > self.chunk_size:
                # Flush current chunk
                chunks.append("\n\n".join(current_parts))

                # Keep overlap: take last paragraph(s) as overlap
                overlap_parts = []
                overlap_tokens = 0
                for part in reversed(current_parts):
                    pt = count_tokens(part)
                    if overlap_tokens + pt > self.chunk_overlap:
                        break
                    overlap_parts.insert(0, part)
                    overlap_tokens += pt

                current_parts = overlap_parts
                current_tokens = overlap_tokens

            current_parts.append(para)
            current_tokens += para_tokens

        if current_parts:
            chunks.append("\n\n".join(current_parts))

        return chunks

    def _split_by_sentences(self, text: str) -> list[str]:
        """Split a long paragraph into sentence-based chunks."""
        # Split on sentence boundaries
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks = []
        current_parts: list[str] = []
        current_tokens = 0

        for sentence in sentences:
            sent_tokens = count_tokens(sentence)
            if current_tokens + sent_tokens > self.chunk_size and current_parts:
                chunks.append(" ".join(current_parts))
                # Overlap: keep last sentence
                current_parts = current_parts[-1:] if current_parts else []
                current_tokens = count_tokens(" ".join(current_parts))

            current_parts.append(sentence)
            current_tokens += sent_tokens

        if current_parts:
            chunks.append(" ".join(current_parts))

        return chunks

    def _text_overlaps(self, chunk_text: str, context_text: str) -> bool:
        """Check if a chunk's text overlaps with an image's context."""
        # Simple word overlap check
        chunk_words = set(chunk_text.lower().split()[:50])
        context_words = set(context_text.lower().split()[:30])
        overlap = len(chunk_words & context_words)
        return overlap >= 5

    @staticmethod
    def _generate_chunk_id(url: str, index: int) -> str:
        """Generate a deterministic chunk ID."""
        base = f"{url}::chunk::{index}"
        return uuid.uuid5(uuid.NAMESPACE_URL, base).hex[:16]

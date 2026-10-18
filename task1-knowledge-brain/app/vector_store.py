"""
AI Tech Consultant - Knowledge Brain
ChromaDB vector store for embedding, indexing, and semantic retrieval of article chunks.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings
from app.models import TextChunk

logger = logging.getLogger(__name__)
settings = get_settings()


class VectorStore:
    """ChromaDB-backed vector store for article chunks."""

    COLLECTION_NAME = "knowledge_brain_articles"

    def __init__(self, persist_dir: str | Path = settings.chroma_persist_dir):
        self.persist_dir = Path(persist_dir)
        self._client: Optional[chromadb.ClientAPI] = None
        self._collection: Optional[chromadb.Collection] = None

    async def initialize(self) -> None:
        """Initialize the ChromaDB client and collection."""
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        count = self._collection.count()
        logger.info(f"Vector store initialized: {count} chunks in collection")

    @property
    def collection(self) -> chromadb.Collection:
        if not self._collection:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        return self._collection

    # ─── Indexing ────────────────────────────────────────────────

    async def add_chunks(self, chunks: list[TextChunk]) -> int:
        """Add or update chunks in the vector store."""
        if not chunks:
            return 0

        # ChromaDB handles embedding internally with its default model,
        # but we'll store documents + metadata for retrieval.
        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            chunk_id = chunk.id or f"chunk_{chunk.article_url}_{chunk.chunk_index}"
            ids.append(chunk_id)

            # Build a rich document for embedding
            doc_parts = []
            if chunk.article_title:
                doc_parts.append(f"Title: {chunk.article_title}")
            if chunk.section_heading:
                doc_parts.append(f"Section: {chunk.section_heading}")
            doc_parts.append(chunk.content)
            if chunk.image_descriptions:
                doc_parts.append("Images: " + "; ".join(chunk.image_descriptions))

            documents.append("\n".join(doc_parts))

            metadatas.append({
                "article_url": chunk.article_url,
                "article_title": chunk.article_title or "",
                "section_heading": chunk.section_heading or "",
                "chunk_index": chunk.chunk_index,
                "token_count": chunk.token_count,
                "category": chunk.metadata.get("category", ""),
                "folder": chunk.metadata.get("folder", ""),
                "has_images": str(chunk.metadata.get("has_images", False)),
                "image_refs": ",".join(chunk.image_refs) if chunk.image_refs else "",
                "image_descriptions": " | ".join(chunk.image_descriptions) if chunk.image_descriptions else "",
            })

        # Upsert in batches (ChromaDB has a batch limit)
        batch_size = 100
        added = 0
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i : i + batch_size]
            batch_docs = documents[i : i + batch_size]
            batch_meta = metadatas[i : i + batch_size]

            self.collection.upsert(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_meta,
            )
            added += len(batch_ids)

        logger.info(f"Indexed {added} chunks (total: {self.collection.count()})")
        return added

    async def delete_by_article(self, article_url: str) -> int:
        """Remove all chunks for a given article URL."""
        # Query for chunk IDs matching this article
        results = self.collection.get(
            where={"article_url": article_url},
            include=[],
        )
        if results["ids"]:
            self.collection.delete(ids=results["ids"])
            logger.info(f"Deleted {len(results['ids'])} chunks for {article_url}")
            return len(results["ids"])
        return 0

    # ─── Retrieval ───────────────────────────────────────────────

    async def search(
        self,
        query: str,
        top_k: int = settings.retrieval_top_k,
        min_score: float = settings.min_relevance_score,
        category_filter: Optional[str] = None,
    ) -> list[dict]:
        """Semantic search for chunks relevant to a query."""
        where_filter = None
        if category_filter:
            where_filter = {"category": category_filter}

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        if not results["ids"] or not results["ids"][0]:
            return []

        chunks = []
        for i, chunk_id in enumerate(results["ids"][0]):
            # ChromaDB cosine distance → similarity score
            distance = results["distances"][0][i]
            score = 1.0 - distance  # cosine distance to similarity

            if score < min_score:
                continue

            metadata = results["metadatas"][0][i]
            document = results["documents"][0][i]

            chunks.append({
                "id": chunk_id,
                "content": document,
                "score": round(score, 4),
                "title": metadata.get("article_title", ""),
                "url": metadata.get("article_url", ""),
                "section": metadata.get("section_heading", ""),
                "category": metadata.get("category", ""),
                "has_images": metadata.get("has_images", "False") == "True",
                "image_refs": [r for r in metadata.get("image_refs", "").split(",") if r],
                "image_descriptions": [
                    d.strip()
                    for d in metadata.get("image_descriptions", "").split("|")
                    if d.strip()
                ],
            })

        logger.debug(f"Search '{query[:50]}...' → {len(chunks)} results (top score: {chunks[0]['score'] if chunks else 'N/A'})")
        return chunks

    # ─── Stats ───────────────────────────────────────────────────

    async def get_stats(self) -> dict:
        """Get collection statistics."""
        count = self._collection.count() if self._collection else 0
        return {
            "total_chunks": count,
            "collection_name": self.COLLECTION_NAME,
            "persist_dir": str(self.persist_dir),
        }

    async def clear(self) -> None:
        """Delete and recreate the collection (use with caution)."""
        if self._client:
            self._client.delete_collection(self.COLLECTION_NAME)
            self._collection = self._client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
            logger.warning("Vector store cleared — collection recreated")

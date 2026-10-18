"""
AI Tech Consultant - Knowledge Brain
SQLite database for ingestion state, escalations, and expert knowledge.
"""
from __future__ import annotations

import aiosqlite
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.models import (
    PageRecord, PageStatus, ArticleImage,
    EscalationRecord, EscalationStatus, EscalationCreate, EscalationResolve,
)

logger = logging.getLogger(__name__)

DB_PATH = Path("./data/knowledge_brain.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    content_hash TEXT,
    title TEXT,
    last_crawled TEXT,
    last_modified TEXT,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS article_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_url TEXT NOT NULL,
    image_url TEXT NOT NULL,
    alt_text TEXT,
    context_text TEXT,
    description TEXT,
    position_index INTEGER DEFAULT 0,
    processed INTEGER DEFAULT 0,
    UNIQUE(article_url, image_url)
);

CREATE TABLE IF NOT EXISTS escalations (
    id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    context TEXT,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    retrieved_sources TEXT DEFAULT '[]',
    answer TEXT,
    expert_name TEXT,
    supporting_urls TEXT DEFAULT '[]',
    created_at TEXT NOT NULL,
    resolved_at TEXT
);

CREATE TABLE IF NOT EXISTS expert_knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    escalation_id TEXT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    expert_name TEXT,
    supporting_urls TEXT DEFAULT '[]',
    added_to_index INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (escalation_id) REFERENCES escalations(id)
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT DEFAULT 'running',
    total_pages INTEGER DEFAULT 0,
    new_pages INTEGER DEFAULT 0,
    updated_pages INTEGER DEFAULT 0,
    removed_pages INTEGER DEFAULT 0,
    failed_pages INTEGER DEFAULT 0,
    error TEXT
);

CREATE TABLE IF NOT EXISTS prompt_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_name TEXT NOT NULL,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    notes TEXT,
    UNIQUE(prompt_name, version)
);

CREATE INDEX IF NOT EXISTS idx_pages_status ON pages(status);
CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url);
CREATE INDEX IF NOT EXISTS idx_escalations_status ON escalations(status);
"""


class Database:
    """Async SQLite database manager."""

    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = Path(db_path)
        self._db: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        """Initialize the database connection and schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(str(self.db_path))
        self._db.row_factory = aiosqlite.Row
        await self._db.executescript(SCHEMA_SQL)
        await self._db.commit()
        logger.info(f"Database connected: {self.db_path}")

    async def close(self) -> None:
        if self._db:
            await self._db.close()

    @property
    def db(self) -> aiosqlite.Connection:
        if not self._db:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._db

    # ─── Page Management ─────────────────────────────────────────

    async def upsert_page(self, url: str, last_modified: Optional[str] = None) -> PageRecord:
        """Insert or update a page record."""
        now = datetime.utcnow().isoformat()
        await self.db.execute(
            """INSERT INTO pages (url, status, last_modified, created_at, updated_at)
               VALUES (?, 'pending', ?, ?, ?)
               ON CONFLICT(url) DO UPDATE SET
                   last_modified = COALESCE(excluded.last_modified, pages.last_modified),
                   updated_at = excluded.updated_at""",
            (url, last_modified, now, now)
        )
        await self.db.commit()
        return await self.get_page(url)

    async def get_page(self, url: str) -> Optional[PageRecord]:
        async with self.db.execute("SELECT * FROM pages WHERE url = ?", (url,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return PageRecord(**dict(row))
        return None

    async def update_page_status(
        self, url: str, status: PageStatus,
        content_hash: Optional[str] = None,
        title: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        now = datetime.utcnow().isoformat()
        await self.db.execute(
            """UPDATE pages SET status = ?, content_hash = COALESCE(?, content_hash),
               title = COALESCE(?, title), error_message = ?,
               last_crawled = ?, updated_at = ?,
               retry_count = CASE WHEN ? = 'failed' THEN retry_count + 1 ELSE retry_count END
               WHERE url = ?""",
            (status.value, content_hash, title, error_message, now, now, status.value, url)
        )
        await self.db.commit()

    async def get_pages_by_status(self, status: PageStatus, limit: int = 100) -> list[PageRecord]:
        async with self.db.execute(
            "SELECT * FROM pages WHERE status = ? ORDER BY updated_at LIMIT ?",
            (status.value, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [PageRecord(**dict(r)) for r in rows]

    async def get_all_page_urls(self) -> set[str]:
        async with self.db.execute("SELECT url FROM pages WHERE status != 'removed'") as cursor:
            rows = await cursor.fetchall()
            return {r["url"] for r in rows}

    async def mark_removed(self, urls: set[str]) -> int:
        if not urls:
            return 0
        placeholders = ",".join("?" for _ in urls)
        await self.db.execute(
            f"UPDATE pages SET status = 'removed', updated_at = ? WHERE url IN ({placeholders})",
            (datetime.utcnow().isoformat(), *urls)
        )
        await self.db.commit()
        return len(urls)

    async def get_page_counts(self) -> dict[str, int]:
        counts = {}
        async with self.db.execute(
            "SELECT status, COUNT(*) as cnt FROM pages GROUP BY status"
        ) as cursor:
            rows = await cursor.fetchall()
            for r in rows:
                counts[r["status"]] = r["cnt"]
        return counts

    async def get_pages_needing_update(self, sitemap_entries: dict[str, Optional[str]]) -> list[str]:
        """Find pages whose last_modified changed or are new."""
        needs_update = []
        for url, lastmod in sitemap_entries.items():
            page = await self.get_page(url)
            if not page:
                needs_update.append(url)
            elif page.status == PageStatus.REMOVED:
                needs_update.append(url)
            elif lastmod and page.last_modified != lastmod:
                needs_update.append(url)
        return needs_update

    # ─── Image Management ────────────────────────────────────────

    async def upsert_image(self, image: ArticleImage) -> None:
        await self.db.execute(
            """INSERT INTO article_images (article_url, image_url, alt_text, context_text, position_index)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(article_url, image_url) DO UPDATE SET
                   alt_text = COALESCE(excluded.alt_text, article_images.alt_text),
                   context_text = COALESCE(excluded.context_text, article_images.context_text)""",
            (image.article_url, image.image_url, image.alt_text, image.context_text, image.position_index)
        )
        await self.db.commit()

    async def update_image_description(self, article_url: str, image_url: str, description: str) -> None:
        await self.db.execute(
            "UPDATE article_images SET description = ?, processed = 1 WHERE article_url = ? AND image_url = ?",
            (description, article_url, image_url)
        )
        await self.db.commit()

    async def get_unprocessed_images(self, limit: int = 20) -> list[ArticleImage]:
        async with self.db.execute(
            "SELECT * FROM article_images WHERE processed = 0 LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [ArticleImage(**dict(r)) for r in rows]

    async def get_images_for_article(self, article_url: str) -> list[ArticleImage]:
        async with self.db.execute(
            "SELECT * FROM article_images WHERE article_url = ? ORDER BY position_index",
            (article_url,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [ArticleImage(**dict(r)) for r in rows]

    # ─── Escalation Management ───────────────────────────────────

    async def create_escalation(self, escalation_id: str, data: EscalationCreate) -> EscalationRecord:
        now = datetime.utcnow().isoformat()
        await self.db.execute(
            """INSERT INTO escalations (id, question, context, reason, status, retrieved_sources, created_at)
               VALUES (?, ?, ?, ?, 'open', ?, ?)""",
            (escalation_id, data.question, data.context, data.reason,
             json.dumps(data.retrieved_sources), now)
        )
        await self.db.commit()
        return await self.get_escalation(escalation_id)

    async def get_escalation(self, escalation_id: str) -> Optional[EscalationRecord]:
        async with self.db.execute("SELECT * FROM escalations WHERE id = ?", (escalation_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                d = dict(row)
                d["retrieved_sources"] = json.loads(d.get("retrieved_sources", "[]"))
                d["supporting_urls"] = json.loads(d.get("supporting_urls", "[]"))
                return EscalationRecord(**d)
        return None

    async def resolve_escalation(self, escalation_id: str, data: EscalationResolve) -> Optional[EscalationRecord]:
        now = datetime.utcnow().isoformat()
        await self.db.execute(
            """UPDATE escalations SET status = 'resolved', answer = ?, expert_name = ?,
               supporting_urls = ?, resolved_at = ? WHERE id = ?""",
            (data.answer, data.expert_name, json.dumps(data.supporting_urls), now, escalation_id)
        )

        if data.add_to_knowledge:
            await self.db.execute(
                """INSERT INTO expert_knowledge (escalation_id, question, answer, expert_name, supporting_urls, created_at)
                   VALUES (?, (SELECT question FROM escalations WHERE id = ?), ?, ?, ?, ?)""",
                (escalation_id, escalation_id, data.answer, data.expert_name,
                 json.dumps(data.supporting_urls), now)
            )
        await self.db.commit()
        return await self.get_escalation(escalation_id)

    async def get_open_escalations(self) -> list[EscalationRecord]:
        async with self.db.execute(
            "SELECT * FROM escalations WHERE status IN ('open', 'in_progress') ORDER BY created_at"
        ) as cursor:
            rows = await cursor.fetchall()
            results = []
            for row in rows:
                d = dict(row)
                d["retrieved_sources"] = json.loads(d.get("retrieved_sources", "[]"))
                d["supporting_urls"] = json.loads(d.get("supporting_urls", "[]"))
                results.append(EscalationRecord(**d))
            return results

    async def get_escalation_count(self) -> int:
        async with self.db.execute("SELECT COUNT(*) as cnt FROM escalations") as cursor:
            row = await cursor.fetchone()
            return row["cnt"] if row else 0

    # ─── Expert Knowledge ────────────────────────────────────────

    async def get_expert_answers(self) -> list[dict]:
        async with self.db.execute(
            "SELECT * FROM expert_knowledge WHERE added_to_index = 0"
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def mark_expert_indexed(self, ek_id: int) -> None:
        await self.db.execute(
            "UPDATE expert_knowledge SET added_to_index = 1 WHERE id = ?", (ek_id,)
        )
        await self.db.commit()

    # ─── Ingestion Run Tracking ──────────────────────────────────

    async def start_ingestion_run(self) -> int:
        now = datetime.utcnow().isoformat()
        cursor = await self.db.execute(
            "INSERT INTO ingestion_runs (started_at) VALUES (?)", (now,)
        )
        await self.db.commit()
        return cursor.lastrowid

    async def finish_ingestion_run(
        self, run_id: int, total: int, new: int, updated: int, removed: int, failed: int,
        error: Optional[str] = None
    ) -> None:
        now = datetime.utcnow().isoformat()
        status = "failed" if error else "completed"
        await self.db.execute(
            """UPDATE ingestion_runs SET finished_at = ?, status = ?,
               total_pages = ?, new_pages = ?, updated_pages = ?, removed_pages = ?,
               failed_pages = ?, error = ? WHERE id = ?""",
            (now, status, total, new, updated, removed, failed, error, run_id)
        )
        await self.db.commit()

    async def get_last_ingestion(self) -> Optional[dict]:
        async with self.db.execute(
            "SELECT * FROM ingestion_runs ORDER BY started_at DESC LIMIT 1"
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    # ─── Prompt Version Management ───────────────────────────────

    async def save_prompt_version(self, name: str, content: str, notes: str = "") -> int:
        # Get next version number
        async with self.db.execute(
            "SELECT MAX(version) as max_v FROM prompt_versions WHERE prompt_name = ?", (name,)
        ) as cursor:
            row = await cursor.fetchone()
            version = (row["max_v"] or 0) + 1

        now = datetime.utcnow().isoformat()
        # Deactivate previous
        await self.db.execute(
            "UPDATE prompt_versions SET is_active = 0 WHERE prompt_name = ?", (name,)
        )
        cursor = await self.db.execute(
            "INSERT INTO prompt_versions (prompt_name, version, content, created_at, notes) VALUES (?, ?, ?, ?, ?)",
            (name, version, content, now, notes)
        )
        await self.db.commit()
        return version

    async def get_active_prompt(self, name: str) -> Optional[str]:
        async with self.db.execute(
            "SELECT content FROM prompt_versions WHERE prompt_name = ? AND is_active = 1",
            (name,)
        ) as cursor:
            row = await cursor.fetchone()
            return row["content"] if row else None

"""
AI Tech Consultant - Knowledge Brain
End-to-end ingestion pipeline: sitemap → crawl → parse → chunk → embed.
Supports full and incremental runs with checkpoint-resume.
"""
from __future__ import annotations

import logging
from typing import Optional

from app.config import get_settings
from app.database import Database
from app.models import PageStatus, ArticleContent
from app.vector_store import VectorStore
from ingestion.crawler import SitemapParser, WebCrawler
from ingestion.parser import ArticleParser
from ingestion.chunker import ArticleChunker

logger = logging.getLogger(__name__)
settings = get_settings()


class IngestionPipeline:
    """Orchestrates the full ingestion workflow."""

    def __init__(self, db: Database, vector_store: VectorStore):
        self.db = db
        self.vector_store = vector_store
        self.sitemap_parser = SitemapParser()
        self.article_parser = ArticleParser()
        self.chunker = ArticleChunker()
        self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    async def run(
        self,
        full_crawl: bool = False,
        max_pages: Optional[int] = None,
    ) -> dict:
        """Run the complete ingestion pipeline.

        Args:
            full_crawl: If True, re-crawl all pages regardless of cache.
            max_pages: Limit the number of pages to process (for testing).

        Returns:
            Summary dict with counts of pages processed.
        """
        if self._is_running:
            return {"error": "Ingestion already in progress"}

        self._is_running = True
        run_id = await self.db.start_ingestion_run()

        stats = {
            "total_sitemap": 0,
            "articles_found": 0,
            "crawled": 0,
            "parsed": 0,
            "chunked": 0,
            "indexed": 0,
            "failed": 0,
            "removed": 0,
            "skipped": 0,
        }

        try:
            # ── Step 1: Fetch and parse sitemap ──
            logger.info("═" * 60)
            logger.info("Step 1/5: Fetching sitemap...")
            entries = await self.sitemap_parser.fetch_and_parse(settings.sitemap_url)
            stats["total_sitemap"] = len(entries)

            # Filter to article URLs only
            article_entries = self.sitemap_parser.filter_article_urls(entries)
            stats["articles_found"] = len(article_entries)
            logger.info(f"Found {stats['articles_found']} article URLs from {stats['total_sitemap']} sitemap entries")

            # ── Step 2: Detect removed pages ──
            if not full_crawl:
                current_urls = {e.url.rstrip("/") for e in article_entries}
                known_urls = await self.db.get_all_page_urls()
                removed_urls = known_urls - current_urls
                if removed_urls:
                    stats["removed"] = await self.db.mark_removed(removed_urls)
                    # Remove from vector store too
                    for url in removed_urls:
                        await self.vector_store.delete_by_article(url)
                    logger.info(f"Marked {stats['removed']} pages as removed")

            # ── Step 3: Crawl pages ──
            logger.info("═" * 60)
            logger.info("Step 2/5: Crawling pages...")
            crawler = WebCrawler(self.db)

            if full_crawl:
                crawl_results = await crawler.crawl_all(article_entries, max_pages)
            else:
                # Only crawl new/updated pages
                sitemap_dict = {e.url: e.lastmod for e in article_entries}
                needs_update = await self.db.get_pages_needing_update(sitemap_dict)
                if max_pages:
                    needs_update = needs_update[:max_pages]

                # Convert back to entries for crawl_all
                entry_map = {e.url: e for e in article_entries}
                entries_to_crawl = [entry_map[u] for u in needs_update if u in entry_map]
                crawl_results = await crawler.crawl_all(entries_to_crawl)

            crawl_stats = crawler.get_stats()
            stats["crawled"] = crawl_stats["fetched"]
            stats["skipped"] = crawl_stats["skipped"]
            logger.info(f"Crawled {stats['crawled']} pages, skipped {stats['skipped']}")

            # ── Step 4: Parse HTML → structured content ──
            logger.info("═" * 60)
            logger.info("Step 3/5: Parsing articles...")
            articles: list[ArticleContent] = []

            for url, html in crawl_results.items():
                if html is None:
                    continue
                article = self.article_parser.parse(html, url)
                if article:
                    articles.append(article)
                    await self.db.update_page_status(
                        url, PageStatus.PARSED, title=article.title
                    )
                    # Save images to DB
                    for img in article.images:
                        await self.db.upsert_image(img)
                    stats["parsed"] += 1
                else:
                    await self.db.update_page_status(
                        url, PageStatus.FAILED,
                        error_message="Parser returned no content"
                    )
                    stats["failed"] += 1

            logger.info(f"Parsed {stats['parsed']} articles ({stats['failed']} failed)")

            # ── Step 5: Chunk → Embed → Index ──
            logger.info("═" * 60)
            logger.info("Step 4/5: Chunking articles...")
            all_chunks = self.chunker.chunk_articles(articles)
            stats["chunked"] = len(all_chunks)
            logger.info(f"Created {stats['chunked']} chunks from {stats['parsed']} articles")

            logger.info("Step 5/5: Indexing in vector store...")
            indexed = await self.vector_store.add_chunks(all_chunks)
            stats["indexed"] = indexed

            # Mark pages as indexed
            for article in articles:
                await self.db.update_page_status(article.url, PageStatus.INDEXED)

            logger.info(f"Indexed {stats['indexed']} chunks in vector store")

            # ── Finish ──
            await self.db.finish_ingestion_run(
                run_id,
                total=stats["articles_found"],
                new=stats["crawled"],
                updated=0,
                removed=stats["removed"],
                failed=stats["failed"],
            )

            logger.info("═" * 60)
            logger.info("Ingestion complete!")
            logger.info(f"  Sitemap entries: {stats['total_sitemap']}")
            logger.info(f"  Articles found:  {stats['articles_found']}")
            logger.info(f"  Crawled:         {stats['crawled']}")
            logger.info(f"  Parsed:          {stats['parsed']}")
            logger.info(f"  Chunks created:  {stats['chunked']}")
            logger.info(f"  Indexed:         {stats['indexed']}")
            logger.info(f"  Failed:          {stats['failed']}")
            logger.info(f"  Removed:         {stats['removed']}")
            logger.info("═" * 60)

            return stats

        except Exception as e:
            logger.error(f"Ingestion pipeline failed: {e}", exc_info=True)
            await self.db.finish_ingestion_run(
                run_id,
                total=stats.get("articles_found", 0),
                new=stats.get("crawled", 0),
                updated=0,
                removed=stats.get("removed", 0),
                failed=stats.get("failed", 0),
                error=str(e),
            )
            stats["error"] = str(e)
            return stats

        finally:
            self._is_running = False

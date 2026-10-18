"""
AI Tech Consultant - Knowledge Brain
Sitemap parser and polite web crawler with rate limiting, retries, and checkpointing.
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import time
import xml.etree.ElementTree as ET
from typing import Optional
from urllib.parse import urlparse

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import get_settings
from app.database import Database
from app.models import PageStatus, SitemapEntry

logger = logging.getLogger(__name__)
settings = get_settings()


class SitemapParser:
    """Parse XML sitemaps to discover help-center URLs."""

    SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    async def fetch_and_parse(self, sitemap_url: str) -> list[SitemapEntry]:
        """Download and parse a sitemap XML file."""
        logger.info(f"Fetching sitemap: {sitemap_url}")
        async with httpx.AsyncClient(
            timeout=30,
            headers={"User-Agent": settings.crawl_user_agent},
            follow_redirects=True,
        ) as client:
            response = await client.get(sitemap_url)
            response.raise_for_status()

        entries = self._parse_xml(response.text)
        logger.info(f"Found {len(entries)} URLs in sitemap")
        return entries

    def _parse_xml(self, xml_content: str) -> list[SitemapEntry]:
        """Parse sitemap XML and extract URL entries."""
        root = ET.fromstring(xml_content)
        entries = []

        # Handle both sitemap index and urlset
        for url_elem in root.findall(".//sm:url", self.SITEMAP_NS):
            loc = url_elem.find("sm:loc", self.SITEMAP_NS)
            if loc is None or not loc.text:
                continue

            lastmod_elem = url_elem.find("sm:lastmod", self.SITEMAP_NS)
            changefreq_elem = url_elem.find("sm:changefreq", self.SITEMAP_NS)
            priority_elem = url_elem.find("sm:priority", self.SITEMAP_NS)

            entry = SitemapEntry(
                url=loc.text.strip(),
                lastmod=lastmod_elem.text.strip() if lastmod_elem is not None and lastmod_elem.text else None,
                changefreq=changefreq_elem.text.strip() if changefreq_elem is not None and changefreq_elem.text else None,
                priority=float(priority_elem.text) if priority_elem is not None and priority_elem.text else None,
            )
            entries.append(entry)

        # Also try without namespace (some sitemaps don't use namespace)
        if not entries:
            for url_elem in root.iter("url"):
                loc = url_elem.find("loc")
                if loc is None or not loc.text:
                    continue
                lastmod = url_elem.find("lastmod")
                entry = SitemapEntry(
                    url=loc.text.strip(),
                    lastmod=lastmod.text.strip() if lastmod is not None and lastmod.text else None,
                )
                entries.append(entry)

        return entries

    def filter_article_urls(self, entries: list[SitemapEntry]) -> list[SitemapEntry]:
        """Filter to only help-center article URLs."""
        filtered = []
        seen = set()
        for entry in entries:
            url = entry.url.rstrip("/")
            if url in seen:
                continue
            seen.add(url)

            parsed = urlparse(url)
            # Keep support/solutions articles, skip generic pages
            if "/support/solutions/articles/" in parsed.path or "/support/solutions/folders/" in parsed.path:
                filtered.append(entry)
            elif "/support/solutions/" in parsed.path:
                filtered.append(entry)

        logger.info(f"Filtered to {len(filtered)} article URLs")
        return filtered


class WebCrawler:
    """Polite, resumable web crawler with rate limiting and retry logic."""

    def __init__(self, db: Database):
        self.db = db
        self._semaphore = asyncio.Semaphore(settings.crawl_concurrency)
        self._last_request_time = 0.0
        self._request_lock = asyncio.Lock()
        self._stats = {"fetched": 0, "failed": 0, "skipped": 0}

    async def _rate_limit(self) -> None:
        """Enforce minimum delay between requests."""
        async with self._request_lock:
            now = time.monotonic()
            elapsed = now - self._last_request_time
            if elapsed < settings.crawl_delay_seconds:
                await asyncio.sleep(settings.crawl_delay_seconds - elapsed)
            self._last_request_time = time.monotonic()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout)),
    )
    async def _fetch_page(self, url: str) -> str:
        """Fetch a single page with retries."""
        await self._rate_limit()
        async with httpx.AsyncClient(
            timeout=30,
            headers={
                "User-Agent": settings.crawl_user_agent,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
            },
            follow_redirects=True,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    async def crawl_page(self, url: str) -> Optional[str]:
        """Crawl a single page with concurrency control and error handling."""
        async with self._semaphore:
            try:
                html = await self._fetch_page(url)
                content_hash = hashlib.md5(html.encode()).hexdigest()

                # Check if content changed
                existing = await self.db.get_page(url)
                if existing and existing.content_hash == content_hash and existing.status == PageStatus.INDEXED:
                    self._stats["skipped"] += 1
                    logger.debug(f"Skipping unchanged: {url}")
                    return None

                await self.db.update_page_status(url, PageStatus.CRAWLED, content_hash=content_hash)
                self._stats["fetched"] += 1
                logger.info(f"Crawled ({self._stats['fetched']}): {url}")
                return html

            except Exception as e:
                self._stats["failed"] += 1
                logger.error(f"Failed to crawl {url}: {e}")
                await self.db.update_page_status(
                    url, PageStatus.FAILED,
                    error_message=str(e)[:500]
                )
                return None

    async def crawl_batch(self, urls: list[str]) -> dict[str, Optional[str]]:
        """Crawl a batch of URLs with rate limiting."""
        results = {}
        tasks = [self.crawl_page(url) for url in urls]
        htmls = await asyncio.gather(*tasks, return_exceptions=True)

        for url, html in zip(urls, htmls):
            if isinstance(html, Exception):
                results[url] = None
                logger.error(f"Batch crawl error for {url}: {html}")
            else:
                results[url] = html

        return results

    async def crawl_all(
        self, entries: list[SitemapEntry], max_pages: Optional[int] = None
    ) -> dict[str, Optional[str]]:
        """Crawl all sitemap entries in batches, with checkpoint-resume."""
        all_results: dict[str, Optional[str]] = {}

        # Register all pages
        for entry in entries:
            await self.db.upsert_page(entry.url, entry.lastmod)

        # Filter to pages that need processing
        urls_to_crawl = []
        for entry in entries:
            page = await self.db.get_page(entry.url)
            if page and page.status in (PageStatus.INDEXED,) and page.content_hash:
                # Already indexed and unchanged
                continue
            urls_to_crawl.append(entry.url)

        if max_pages:
            urls_to_crawl = urls_to_crawl[:max_pages]

        total = len(urls_to_crawl)
        logger.info(f"Crawling {total} pages ({len(entries) - total} already indexed)")

        # Process in batches
        batch_size = settings.crawl_batch_size
        for i in range(0, total, batch_size):
            batch = urls_to_crawl[i : i + batch_size]
            logger.info(f"Batch {i // batch_size + 1}: {len(batch)} pages")
            batch_results = await self.crawl_batch(batch)
            all_results.update(batch_results)

        logger.info(
            f"Crawl complete: {self._stats['fetched']} fetched, "
            f"{self._stats['skipped']} skipped, {self._stats['failed']} failed"
        )
        return all_results

    def get_stats(self) -> dict:
        return dict(self._stats)


async def fetch_image(url: str) -> Optional[bytes]:
    """Download an image with rate limiting."""
    try:
        async with httpx.AsyncClient(
            timeout=20,
            headers={"User-Agent": settings.crawl_user_agent},
            follow_redirects=True,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            if "image" in content_type or url.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                return response.content
            return None
    except Exception as e:
        logger.warning(f"Failed to fetch image {url}: {e}")
        return None

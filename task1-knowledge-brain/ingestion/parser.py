"""
AI Tech Consultant - Knowledge Brain
HTML article parser: extracts title, headings, structured text, and image references.
"""
from __future__ import annotations

import hashlib
import logging
import re
from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, NavigableString, Tag

from app.models import ArticleContent, ArticleImage

logger = logging.getLogger(__name__)


class ArticleParser:
    """Extract structured content from help-center HTML pages."""

    # Elements to remove from parsing
    REMOVE_SELECTORS = [
        "nav", "header", "footer", ".header", ".footer", ".navigation",
        ".sidebar", ".breadcrumb", ".breadcrumbs", "script", "style",
        ".cookie-banner", ".modal", ".popup", ".advertisement",
        ".social-share", ".related-articles", ".comments",
        "#header", "#footer", "#sidebar", "#navigation",
    ]

    # Image extensions to consider
    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}

    def parse(self, html: str, url: str) -> Optional[ArticleContent]:
        """Parse an HTML page into structured article content."""
        try:
            soup = BeautifulSoup(html, "lxml")

            # Extract metadata and hierarchy before decomposing navigation/breadcrumbs
            title = self._extract_title(soup)
            category, folder = self._extract_hierarchy(soup, url)

            # Remove non-content elements
            for selector in self.REMOVE_SELECTORS:
                for element in soup.select(selector):
                    element.decompose()
            content_text = self._extract_text(soup)
            headings = self._extract_headings(soup)
            images = self._extract_images(soup, url)

            if not content_text or len(content_text.strip()) < 50:
                logger.warning(f"Insufficient content for {url}")
                return None

            content_hash = hashlib.md5(content_text.encode()).hexdigest()

            article = ArticleContent(
                url=url,
                title=title or "Untitled",
                category=category,
                folder=folder,
                content_text=content_text,
                headings=headings,
                images=images,
                content_hash=content_hash,
                word_count=len(content_text.split()),
            )
            logger.debug(f"Parsed article: {title} ({len(content_text)} chars, {len(images)} images)")
            return article

        except Exception as e:
            logger.error(f"Failed to parse {url}: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract the article title."""
        # Try article-specific title selectors
        for selector in [
            "h1.article-title", ".article-title", "h1.heading",
            ".solution-title", "h1",
        ]:
            elem = soup.select_one(selector)
            if elem and elem.get_text(strip=True):
                return elem.get_text(strip=True)

        # Fallback to page title
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            return title_tag.string.strip().split("|")[0].strip()

        return None

    def _extract_hierarchy(self, soup: BeautifulSoup, url: str) -> tuple[Optional[str], Optional[str]]:
        """Extract category and folder from breadcrumbs or URL structure."""
        # Try breadcrumbs
        breadcrumb = soup.select_one(".breadcrumb, .breadcrumbs, nav[aria-label='breadcrumb']")
        if breadcrumb:
            items = breadcrumb.find_all(["a", "li", "span"])
            texts = [i.get_text(strip=True) for i in items if i.get_text(strip=True)]
            texts = [t for t in texts if t not in ("Home", "Support", ">", "»", "/")]
            if len(texts) >= 2:
                return texts[0], texts[1]
            elif len(texts) == 1:
                return texts[0], None

        # Fallback: parse URL path
        parsed = urlparse(url)
        parts = [p for p in parsed.path.split("/") if p and p not in ("support", "solutions", "articles", "folders")]
        if len(parts) >= 2:
            return parts[0].replace("-", " ").title(), parts[1].replace("-", " ").title()

        return None, None

    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract clean article text preserving structure."""
        # Find the main content area
        content_area = None
        for selector in [
            ".article-body", ".article-content", ".solution-body",
            ".content-body", "article", ".article", "main",
            "#article-body", ".fr-view",
        ]:
            content_area = soup.select_one(selector)
            if content_area:
                break

        if not content_area:
            content_area = soup.find("body") or soup

        # Extract text with structure
        lines = []
        for element in content_area.descendants:
            if isinstance(element, NavigableString):
                text = str(element).strip()
                if text and element.parent.name not in ("script", "style"):
                    lines.append(text)
            elif isinstance(element, Tag):
                if element.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                    text = element.get_text(strip=True)
                    if text:
                        level = int(element.name[1])
                        prefix = "#" * level
                        lines.append(f"\n{prefix} {text}\n")
                elif element.name == "li":
                    text = element.get_text(strip=True)
                    if text:
                        lines.append(f"• {text}")
                elif element.name == "br":
                    lines.append("")
                elif element.name == "p":
                    text = element.get_text(strip=True)
                    if text:
                        lines.append(f"\n{text}\n")
                elif element.name in ("tr",):
                    cells = [td.get_text(strip=True) for td in element.find_all(["td", "th"])]
                    if cells:
                        lines.append(" | ".join(cells))

        # Clean up
        text = "\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def _extract_headings(self, soup: BeautifulSoup) -> list[str]:
        """Extract all headings for section structure."""
        headings = []
        for h in soup.find_all(["h1", "h2", "h3", "h4"]):
            text = h.get_text(strip=True)
            if text and len(text) > 2:
                headings.append(text)
        return headings

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> list[ArticleImage]:
        """Extract relevant images with their surrounding context."""
        images = []
        seen_urls = set()

        content_area = None
        for selector in [".article-body", ".article-content", ".solution-body", ".fr-view", "article", "main"]:
            content_area = soup.select_one(selector)
            if content_area:
                break
        if not content_area:
            content_area = soup

        for i, img in enumerate(content_area.find_all("img")):
            src = img.get("src", "") or img.get("data-src", "")
            if not src:
                continue

            # Make absolute URL
            img_url = urljoin(base_url, src)

            # Skip tiny icons, tracking pixels, etc.
            if any(skip in img_url.lower() for skip in [
                "pixel", "tracking", "spacer", "logo", "favicon",
                "icon", "badge", "avatar", "emoji",
            ]):
                continue

            # Check for valid image extension or known image CDN
            parsed = urlparse(img_url)
            has_ext = any(parsed.path.lower().endswith(ext) for ext in self.IMAGE_EXTENSIONS)
            is_cdn = any(cdn in img_url for cdn in ["amazonaws.com", "cloudfront", "cdn", "attachments"])

            if not has_ext and not is_cdn:
                continue

            if img_url in seen_urls:
                continue
            seen_urls.add(img_url)

            # Get surrounding text context
            context = self._get_image_context(img)
            alt_text = img.get("alt", "")

            images.append(ArticleImage(
                article_url=base_url,
                image_url=img_url,
                alt_text=alt_text if alt_text else None,
                context_text=context if context else None,
                position_index=i,
            ))

        return images

    def _get_image_context(self, img: Tag) -> Optional[str]:
        """Get text surrounding an image for context."""
        context_parts = []

        # Check figure caption
        figure = img.find_parent("figure")
        if figure:
            caption = figure.find("figcaption")
            if caption:
                context_parts.append(caption.get_text(strip=True))

        # Get previous sibling text
        prev = img.find_previous_sibling(["p", "h1", "h2", "h3", "h4", "li"])
        if prev:
            text = prev.get_text(strip=True)
            if text and len(text) > 10:
                context_parts.append(text[:200])

        # Get next sibling text
        nxt = img.find_next_sibling(["p", "h1", "h2", "h3", "h4", "li"])
        if nxt:
            text = nxt.get_text(strip=True)
            if text and len(text) > 10:
                context_parts.append(text[:200])

        # Parent paragraph
        parent_p = img.find_parent("p")
        if parent_p:
            text = parent_p.get_text(strip=True)
            if text and len(text) > 10:
                context_parts.append(text[:200])

        return " | ".join(context_parts[:3]) if context_parts else None

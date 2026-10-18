"""
Tests for Knowledge Brain: Sitemap Parser
"""
import pytest
from ingestion.crawler import SitemapParser

SAMPLE_SITEMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://support.brilliantdirectories.com/</loc>
        <lastmod>2026-01-01</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://support.brilliantdirectories.com/support/solutions/articles/10001-how-to-setup-domains</loc>
        <lastmod>2026-02-15</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://support.brilliantdirectories.com/support/solutions/folders/5001-domains-and-ssl</loc>
        <lastmod>2026-02-10</lastmod>
        <priority>0.5</priority>
    </url>
    <url>
        <loc>https://support.brilliantdirectories.com/contact-us</loc>
        <lastmod>2025-12-01</lastmod>
    </url>
</urlset>
"""


def test_parse_sitemap_xml():
    parser = SitemapParser()
    entries = parser._parse_xml(SAMPLE_SITEMAP_XML)
    assert len(entries) == 4
    assert entries[0].url == "https://support.brilliantdirectories.com/"
    assert entries[1].url == "https://support.brilliantdirectories.com/support/solutions/articles/10001-how-to-setup-domains"
    assert entries[1].priority == 0.8


def test_filter_article_urls():
    parser = SitemapParser()
    entries = parser._parse_xml(SAMPLE_SITEMAP_XML)
    filtered = parser.filter_article_urls(entries)
    urls = [e.url for e in filtered]
    assert "https://support.brilliantdirectories.com/support/solutions/articles/10001-how-to-setup-domains" in urls
    assert "https://support.brilliantdirectories.com/support/solutions/folders/5001-domains-and-ssl" in urls
    assert "https://support.brilliantdirectories.com/contact-us" not in urls
    assert "https://support.brilliantdirectories.com/" not in urls

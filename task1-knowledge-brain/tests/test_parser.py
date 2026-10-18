"""
Tests for Knowledge Brain: HTML Article Parser
"""
import pytest
from ingestion.parser import ArticleParser

SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>How to Configure Payment Gateways | Brilliant Directories</title>
</head>
<body>
    <header><nav><a href="/">Home</a></nav></header>
    <div class="breadcrumbs">
        <a href="/support">Support</a> &gt;
        <a href="/support/solutions/categories/finance">Finance &amp; Billing</a> &gt;
        <a href="/support/solutions/folders/gateways">Payment Gateways</a>
    </div>
    <main class="article-body">
        <h1 class="article-title">How to Configure Payment Gateways</h1>
        <p>This guide explains how to set up Stripe and PayPal on your directory website.</p>
        
        <h2>Prerequisites</h2>
        <p>Before beginning, ensure you have an active merchant account.</p>
        
        <h2>Step 1: Navigate to Finance Settings</h2>
        <p>Go to Settings &gt; Finance in your admin dashboard.</p>
        <img src="https://cdn.brilliantdirectories.com/attachments/step1_finance.png" alt="Finance settings screenshot" />
        
        <h2>Step 2: Enter API Keys</h2>
        <p>Paste your Publishable Key and Secret Key into the corresponding fields.</p>
        <ul>
            <li>Live Secret Key</li>
            <li>Live Publishable Key</li>
            <li>Webhook Secret</li>
        </ul>
        
        <h2>Frequently Asked Questions</h2>
        <p>Can I use multiple gateways? Yes, BD supports both Stripe and PayPal simultaneously.</p>
    </main>
    <footer>Copyright 2026 Brilliant Directories</footer>
</body>
</html>
"""


def test_article_parser_extracts_title():
    parser = ArticleParser()
    article = parser.parse(SAMPLE_HTML, "https://support.brilliantdirectories.com/support/solutions/articles/123-payment-gateways")
    assert article is not None
    assert article.title == "How to Configure Payment Gateways"


def test_article_parser_extracts_hierarchy():
    parser = ArticleParser()
    article = parser.parse(SAMPLE_HTML, "https://support.brilliantdirectories.com/support/solutions/articles/123-payment-gateways")
    assert article is not None
    assert article.category == "Finance & Billing"
    assert article.folder == "Payment Gateways"


def test_article_parser_extracts_headings():
    parser = ArticleParser()
    article = parser.parse(SAMPLE_HTML, "https://support.brilliantdirectories.com/support/solutions/articles/123-payment-gateways")
    assert article is not None
    assert "Prerequisites" in article.headings
    assert "Step 1: Navigate to Finance Settings" in article.headings
    assert "Step 2: Enter API Keys" in article.headings


def test_article_parser_extracts_images():
    parser = ArticleParser()
    article = parser.parse(SAMPLE_HTML, "https://support.brilliantdirectories.com/support/solutions/articles/123-payment-gateways")
    assert article is not None
    assert len(article.images) == 1
    assert "step1_finance.png" in article.images[0].image_url
    assert article.images[0].alt_text == "Finance settings screenshot"


def test_article_parser_insufficient_content_returns_none():
    parser = ArticleParser()
    empty_html = "<html><body><p>Too short</p></body></html>"
    article = parser.parse(empty_html, "https://support.brilliantdirectories.com/test")
    assert article is None

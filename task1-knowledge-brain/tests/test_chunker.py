"""
Tests for Knowledge Brain: Semantic Text Chunker
"""
import pytest
from app.models import ArticleContent, ArticleImage
from ingestion.chunker import ArticleChunker, count_tokens


def test_count_tokens():
    text = "Hello world, this is a test of the tiktoken tokenizer."
    tokens = count_tokens(text)
    assert tokens > 0
    assert isinstance(tokens, int)


def test_chunk_article_with_headings():
    content = """
# Introduction
This is an overview of the Brilliant Directories member management system.
You can manage members, plans, and subscriptions.

## Managing Member Accounts
To manage a member account, go to My Members in the dashboard.
Click on the member's name to view their full profile, transaction history, and activity logs.

## Changing Member Plans
To upgrade or downgrade a member, select the Action menu and choose Change Membership Plan.
Make sure to confirm billing adjustments before saving changes.
"""
    article = ArticleContent(
        url="https://support.brilliantdirectories.com/support/solutions/articles/member-management",
        title="Member Management Guide",
        category="Members",
        folder="Management",
        content_text=content.strip(),
        headings=["Introduction", "Managing Member Accounts", "Changing Member Plans"],
        images=[
            ArticleImage(
                article_url="https://support.brilliantdirectories.com/support/solutions/articles/member-management",
                image_url="https://cdn.brilliantdirectories.com/members.png",
                alt_text="My Members dashboard screenshot",
                context_text="To manage a member account, go to My Members in the dashboard.",
            )
        ],
        content_hash="abc123hash",
        word_count=len(content.split()),
    )

    chunker = ArticleChunker(chunk_size=200, chunk_overlap=30)
    chunks = chunker.chunk_article(article)

    assert len(chunks) >= 2
    for chunk in chunks:
        assert chunk.article_url == article.url
        assert chunk.article_title == article.title
        assert chunk.token_count > 0
        assert chunk.id is not None

    # Check that image reference was attached to the relevant chunk
    chunk_with_image = [c for c in chunks if c.image_refs]
    assert len(chunk_with_image) >= 1
    assert "members.png" in chunk_with_image[0].image_refs[0]


def test_chunk_article_without_headings():
    content = "This is a plain article with continuous text explaining general concepts. " * 10
    article = ArticleContent(
        url="https://support.brilliantdirectories.com/test-article",
        title="Plain Article",
        content_text=content.strip(),
        headings=[],
        images=[],
        content_hash="plainhash",
        word_count=len(content.split()),
    )

    chunker = ArticleChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk_article(article)

    assert len(chunks) >= 1
    assert chunks[0].section_heading == "General"

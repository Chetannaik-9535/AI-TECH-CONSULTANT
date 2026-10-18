"""
Tests for Knowledge Brain: SQLite Database Manager
"""
import pytest
from pathlib import Path
from app.database import Database
from app.models import PageStatus, ArticleImage, EscalationCreate, EscalationResolve


@pytest.fixture
async def temp_db(tmp_path: Path):
    db_file = tmp_path / "test_kb.db"
    db = Database(db_path=db_file)
    await db.connect()
    yield db
    await db.close()


@pytest.mark.asyncio
async def test_page_lifecycle(temp_db: Database):
    url = "https://support.brilliantdirectories.com/article/1"
    page = await temp_db.upsert_page(url, last_modified="2026-01-01T00:00:00")
    assert page.url == url
    assert page.status == PageStatus.PENDING

    await temp_db.update_page_status(
        url,
        PageStatus.INDEXED,
        content_hash="hash123",
        title="Test Article Title",
    )
    updated = await temp_db.get_page(url)
    assert updated.status == PageStatus.INDEXED
    assert updated.content_hash == "hash123"
    assert updated.title == "Test Article Title"

    counts = await temp_db.get_page_counts()
    assert counts.get("indexed") == 1


@pytest.mark.asyncio
async def test_escalation_lifecycle(temp_db: Database):
    esc_id = "esc_test_123"
    esc_data = EscalationCreate(
        question="How do I connect custom webhook endpoints?",
        context="Retrieved 3 articles, none mentioned custom webhooks.",
        retrieved_sources=["https://support.brilliantdirectories.com/api-docs"],
        reason="insufficient_evidence",
    )
    rec = await temp_db.create_escalation(esc_id, esc_data)
    assert rec.id == esc_id
    assert rec.status.value == "open"

    open_list = await temp_db.get_open_escalations()
    assert len(open_list) == 1

    # Resolve escalation
    resolve_data = EscalationResolve(
        answer="Navigate to Developer Hub > Webhooks > Add Webhook.",
        expert_name="DevLead",
        supporting_urls=["https://support.brilliantdirectories.com/webhooks-guide"],
        add_to_knowledge=True,
    )
    resolved = await temp_db.resolve_escalation(esc_id, resolve_data)
    assert resolved.status.value == "resolved"
    assert resolved.expert_name == "DevLead"

    # Verify expert knowledge was captured
    expert_rows = await temp_db.get_expert_answers()
    assert len(expert_rows) == 1
    assert expert_rows[0]["escalation_id"] == esc_id


@pytest.mark.asyncio
async def test_prompt_versioning(temp_db: Database):
    v1 = await temp_db.save_prompt_version("qa_prompt", "Version 1 prompt content", "Initial")
    assert v1 == 1

    active1 = await temp_db.get_active_prompt("qa_prompt")
    assert active1 == "Version 1 prompt content"

    v2 = await temp_db.save_prompt_version("qa_prompt", "Version 2 prompt content", "Improved citations")
    assert v2 == 2

    active2 = await temp_db.get_active_prompt("qa_prompt")
    assert active2 == "Version 2 prompt content"

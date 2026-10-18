"""
Tests for Knowledge Brain: FastAPI Endpoints
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from pathlib import Path

from app.main import app, db, vector_store
import app.main as main_module
from app.database import Database
from app.models import QueryResponse, AnswerStatus, SourceReference


@pytest.fixture
async def test_client(tmp_path: Path):
    test_db_file = tmp_path / "api_test.db"
    test_db = Database(db_path=test_db_file)
    await test_db.connect()

    mock_rag = MagicMock()
    mock_rag.query = AsyncMock(return_value=QueryResponse(
        answer="To set up custom domains, go to Settings > Domain Manager.",
        status=AnswerStatus.ANSWERED,
        sources=[SourceReference(
            title="Custom Domains Setup",
            url="https://support.brilliantdirectories.com/domain-setup",
            section="Overview",
            relevance_score=0.95,
            snippet="Domain setup steps...",
        )],
        images=[],
        confidence_note="High confidence",
        request_id="req123",
        model_used="claude-sonnet-4-20250514",
        latency_ms=120.0,
    ))

    # Temporarily override globals
    main_module.db = test_db
    main_module.rag_engine = mock_rag

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    await test_db.close()


@pytest.mark.asyncio
async def test_health_endpoint(test_client: AsyncClient):
    response = await test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "knowledge-brain"


@pytest.mark.asyncio
async def test_stats_endpoint(test_client: AsyncClient):
    response = await test_client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "pages" in data
    assert "vector_store" in data


@pytest.mark.asyncio
async def test_query_endpoint(test_client: AsyncClient):
    payload = {
        "question": "How do I configure my custom domain name?",
        "max_sources": 3,
        "include_images": True,
    }
    response = await test_client.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "answered"
    assert len(data["sources"]) == 1
    assert "Custom Domains Setup" in data["sources"][0]["title"]


@pytest.mark.asyncio
async def test_escalations_endpoints(test_client: AsyncClient):
    # Empty list initially
    response = await test_client.get("/escalations")
    assert response.status_code == 200
    assert response.json() == []

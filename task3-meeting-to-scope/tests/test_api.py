"""
FastAPI integration tests for Task 3 Meeting to Scope
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    res = await client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "meeting-to-scope"
    assert data["meetings_count"] >= 3


@pytest.mark.asyncio
async def test_list_meetings(client: AsyncClient):
    res = await client.get("/api/meetings")
    assert res.status_code == 200
    meetings = res.json()
    assert len(meetings) >= 3
    assert any(m["id"] == "MEET-2001" for m in meetings)


@pytest.mark.asyncio
async def test_get_meeting_detail(client: AsyncClient):
    res = await client.get("/api/meetings/MEET-2001")
    assert res.status_code == 200
    data = res.json()
    assert data["metadata"]["id"] == "MEET-2001"
    assert "transcript" in data
    assert "Dr. Julian Vance" in data["transcript"]


@pytest.mark.asyncio
async def test_analyze_meeting(client: AsyncClient):
    res = await client.post("/api/meetings/MEET-2001/analyze")
    assert res.status_code == 200
    data = res.json()
    assert data["meeting_id"] == "MEET-2001"
    assert "requirements" in data
    assert len(data["requirements"]) > 0


@pytest.mark.asyncio
async def test_generate_sow_and_download(client: AsyncClient):
    res = await client.post("/api/meetings/MEET-2001/generate-sow?hourly_rate=150")
    assert res.status_code == 200
    sow = res.json()
    assert "sow_id" in sow
    assert sow["total_cost"] > 0
    assert len(sow["phases"]) == 4

    # Download markdown
    sow_id = sow["sow_id"]
    res_md = await client.get(f"/api/sow/{sow_id}/markdown")
    assert res_md.status_code == 200
    assert "Scope of Work" in res_md.text

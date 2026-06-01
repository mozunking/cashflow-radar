"""Tests for CAD API"""

import pytest
from httpx import AsyncClient, ASGITransport
from cad_service.main import app


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


@pytest.mark.asyncio
async def test_batch_detect():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/detect/batch", json={"data_date": "2026-05-17"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["total_count"] == 100

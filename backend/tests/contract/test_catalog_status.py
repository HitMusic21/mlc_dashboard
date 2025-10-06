"""Contract test for GET /api/v1/catalog/{id}/status endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_status_returns_progress(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that GET /catalog/{id}/status returns progress info."""
    upload_id = 1
    response = await client.get(
        f"/api/v1/catalog/{upload_id}/status", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "progress_percentage" in data
    assert "estimated_time_remaining_seconds" in data
    assert isinstance(data["progress_percentage"], (int, float))


@pytest.mark.asyncio
async def test_get_status_nonexistent_returns_404(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that non-existent upload returns 404."""
    response = await client.get("/api/v1/catalog/999999/status", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_status_without_auth_returns_401(client: AsyncClient):
    """Test that status without auth returns 401."""
    response = await client.get("/api/v1/catalog/1/status")
    assert response.status_code == 401

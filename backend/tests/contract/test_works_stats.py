"""Contract test for GET /api/v1/works/statistics endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_statistics_returns_dashboard_stats(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that GET /works/statistics returns dashboard statistics."""
    # Act
    response = await client.get("/api/v1/works/statistics", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Validate DashboardStatistics schema
    assert "total_works" in data
    assert "works_with_iswc" in data
    assert "disputed_works" in data
    assert "monthly_trend" in data

    assert isinstance(data["total_works"], int)
    assert isinstance(data["works_with_iswc"], int)
    assert isinstance(data["disputed_works"], int)
    assert isinstance(data["monthly_trend"], list)


@pytest.mark.asyncio
async def test_statistics_without_auth_returns_401(client: AsyncClient):
    """Test that statistics without auth returns 401."""
    response = await client.get("/api/v1/works/statistics")
    assert response.status_code == 401

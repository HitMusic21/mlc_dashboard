"""Contract test for GET /api/v1/catalog/{id}/results endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_results_returns_match_groups(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that GET /catalog/{id}/results returns match result groups."""
    upload_id = 1
    response = await client.get(
        f"/api/v1/catalog/{upload_id}/results", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_get_results_match_group_schema(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that match groups have correct schema."""
    upload_id = 1
    response = await client.get(
        f"/api/v1/catalog/{upload_id}/results", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    if len(data["data"]) > 0:
        group = data["data"][0]
        assert "uploaded_track" in group
        assert "matches" in group
        assert isinstance(group["matches"], list)

        if len(group["matches"]) > 0:
            match = group["matches"][0]
            assert "work_id" in match
            assert "confidence_score" in match
            assert "rank" in match
            assert isinstance(match["rank"], int)
            assert match["rank"] >= 1


@pytest.mark.asyncio
async def test_get_results_sorted_by_score(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that matches are sorted by score (highest first)."""
    upload_id = 1
    response = await client.get(
        f"/api/v1/catalog/{upload_id}/results", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    if len(data["data"]) > 0:
        group = data["data"][0]
        if len(group["matches"]) > 1:
            scores = [m["confidence_score"] for m in group["matches"]]
            assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_get_results_with_confidence_filter(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that confidence filter works."""
    upload_id = 1
    response = await client.get(
        f"/api/v1/catalog/{upload_id}/results?confidence=high", headers=auth_headers
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_results_without_auth_returns_401(client: AsyncClient):
    """Test that results without auth returns 401."""
    response = await client.get("/api/v1/catalog/1/results")
    assert response.status_code == 401

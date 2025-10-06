"""Integration test for Scenario 2: Browse and search works."""

import time

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_browse_works_with_pagination(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test browsing works with pagination."""
    # Get first page
    response = await client.get(
        "/api/v1/works?page=1&limit=50", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) <= 50


@pytest.mark.asyncio
async def test_full_text_search_performance(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test full-text search with performance requirement."""
    start = time.time()
    response = await client.post(
        "/api/v1/works/search",
        json={"query": "yesterday", "page": 1, "limit": 50},
        headers=auth_headers,
    )
    elapsed_ms = (time.time() - start) * 1000

    assert response.status_code == 200
    assert elapsed_ms < 500


@pytest.mark.asyncio
async def test_filter_works_by_iswc_and_disputes(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test filtering works by ISWC and disputed rights."""
    response = await client.get(
        "/api/v1/works?has_iswc=true&has_disputed_rights=false", headers=auth_headers
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_work_details_with_resources(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test retrieving work details including resources."""
    # First get a work ID
    list_response = await client.get("/api/v1/works?limit=1", headers=auth_headers)
    assert list_response.status_code == 200

    works = list_response.json()["data"]
    if len(works) > 0:
        work_id = works[0]["id"]

        # Get detailed work
        detail_response = await client.get(
            f"/api/v1/works/{work_id}", headers=auth_headers
        )
        assert detail_response.status_code == 200
        work = detail_response.json()
        assert "resources" in work

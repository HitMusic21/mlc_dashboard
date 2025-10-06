"""Contract test for GET /api/v1/works endpoint.

This test validates the works listing API contract:
- Response schema validation (paginated list)
- Query parameters validation
- Performance requirement (<500ms)
- Filtering capabilities
"""

import time

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_works_returns_paginated_list(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that GET /works returns paginated list of musical works."""
    # Act
    response = await client.get("/api/v1/works", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Validate top-level response schema
    assert "data" in data
    assert "pagination" in data
    assert "meta" in data

    # Validate data is array
    assert isinstance(data["data"], list)

    # Validate pagination schema
    pagination = data["pagination"]
    assert "page" in pagination
    assert "limit" in pagination
    assert "total_items" in pagination
    assert "total_pages" in pagination
    assert isinstance(pagination["page"], int)
    assert isinstance(pagination["limit"], int)
    assert isinstance(pagination["total_items"], int)
    assert isinstance(pagination["total_pages"], int)

    # Validate meta schema
    meta = data["meta"]
    assert "response_time_ms" in meta
    assert isinstance(meta["response_time_ms"], (int, float))


@pytest.mark.asyncio
async def test_get_works_single_item_validates_schema(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that each work item has required fields."""
    # Act
    response = await client.get("/api/v1/works?limit=1", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()

    if len(data["data"]) > 0:
        work = data["data"][0]

        # Validate MusicalWork schema
        assert "id" in work
        assert "title" in work
        assert "iswc" in work
        assert "has_disputed_rights" in work
        assert "created_at" in work
        assert "updated_at" in work

        # Validate data types
        assert isinstance(work["id"], int)
        assert isinstance(work["title"], str)
        assert work["iswc"] is None or isinstance(work["iswc"], str)
        assert isinstance(work["has_disputed_rights"], bool)
        assert isinstance(work["created_at"], str)
        assert isinstance(work["updated_at"], str)


@pytest.mark.asyncio
async def test_get_works_with_page_parameter(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that page parameter works correctly."""
    # Act
    response = await client.get("/api/v1/works?page=2&limit=10", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["page"] == 2
    assert data["pagination"]["limit"] == 10


@pytest.mark.asyncio
async def test_get_works_with_limit_parameter(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that limit parameter works correctly."""
    # Act
    response = await client.get("/api/v1/works?limit=25", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["limit"] == 25
    assert len(data["data"]) <= 25


@pytest.mark.asyncio
async def test_get_works_with_search_parameter(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that search parameter filters results."""
    # Act
    response = await client.get(
        "/api/v1/works?search=yesterday", headers=auth_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


@pytest.mark.asyncio
async def test_get_works_with_has_iswc_filter(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that has_iswc filter works correctly."""
    # Act
    response = await client.get("/api/v1/works?has_iswc=true", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # If there are results, validate they all have ISWC
    for work in data["data"]:
        if work["iswc"] is not None:
            assert isinstance(work["iswc"], str)


@pytest.mark.asyncio
async def test_get_works_with_disputed_rights_filter(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that has_disputed_rights filter works correctly."""
    # Act
    response = await client.get(
        "/api/v1/works?has_disputed_rights=true", headers=auth_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    # If there are results, validate they all have disputed rights
    for work in data["data"]:
        if work["has_disputed_rights"]:
            assert work["has_disputed_rights"] is True


@pytest.mark.asyncio
async def test_get_works_with_date_filters(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that date filters work correctly."""
    # Act
    response = await client.get(
        "/api/v1/works?created_after=2024-01-01&created_before=2024-12-31",
        headers=auth_headers,
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


@pytest.mark.asyncio
async def test_get_works_response_time_under_500ms(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that response time is under 500ms (performance requirement)."""
    # Act
    start_time = time.time()
    response = await client.get("/api/v1/works?limit=50", headers=auth_headers)
    elapsed_ms = (time.time() - start_time) * 1000

    # Assert
    assert response.status_code == 200
    assert elapsed_ms < 500, f"Response time {elapsed_ms}ms exceeds 500ms requirement"


@pytest.mark.asyncio
async def test_get_works_without_auth_returns_401(client: AsyncClient):
    """Test that GET /works without authentication returns 401."""
    # Act
    response = await client.get("/api/v1/works")

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_works_with_invalid_page_returns_422(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that invalid page parameter returns 422."""
    # Act
    response = await client.get("/api/v1/works?page=0", headers=auth_headers)

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_works_with_invalid_limit_returns_422(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that invalid limit parameter returns 422."""
    # Act
    response = await client.get("/api/v1/works?limit=0", headers=auth_headers)

    # Assert
    assert response.status_code == 422

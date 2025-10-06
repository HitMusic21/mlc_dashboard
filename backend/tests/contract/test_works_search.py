"""Contract test for POST /api/v1/works/search endpoint.

This test validates the Elasticsearch-powered search API contract:
- Request schema validation
- Response schema with search scores
- Search performance metrics
- Full-text search capabilities
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_works_returns_scored_results(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that POST /works/search returns results with search scores."""
    # Arrange
    request_payload = {"query": "yesterday", "page": 1, "limit": 10}

    # Act
    response = await client.post(
        "/api/v1/works/search", json=request_payload, headers=auth_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Validate response schema
    assert "data" in data
    assert "pagination" in data
    assert "meta" in data
    assert isinstance(data["data"], list)

    # Validate meta includes search-specific fields
    meta = data["meta"]
    assert "search_time_ms" in meta
    assert isinstance(meta["search_time_ms"], (int, float))


@pytest.mark.asyncio
async def test_search_works_result_includes_score(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that search results include search_score field."""
    # Arrange
    request_payload = {"query": "test", "page": 1, "limit": 1}

    # Act
    response = await client.post(
        "/api/v1/works/search", json=request_payload, headers=auth_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    if len(data["data"]) > 0:
        result = data["data"][0]
        assert "search_score" in result
        assert isinstance(result["search_score"], (int, float))
        assert result["search_score"] > 0


@pytest.mark.asyncio
async def test_search_works_with_filters(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that search works with additional filters."""
    # Arrange
    request_payload = {
        "query": "test",
        "filters": {"has_iswc": True, "has_disputed_rights": False},
        "page": 1,
        "limit": 10,
    }

    # Act
    response = await client.post(
        "/api/v1/works/search", json=request_payload, headers=auth_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "data" in data


@pytest.mark.asyncio
async def test_search_works_empty_query_returns_422(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that empty query string returns 422."""
    # Arrange
    request_payload = {"query": "", "page": 1, "limit": 10}

    # Act
    response = await client.post(
        "/api/v1/works/search", json=request_payload, headers=auth_headers
    )

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_search_works_missing_query_returns_422(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that missing query field returns 422."""
    # Arrange
    request_payload = {"page": 1, "limit": 10}

    # Act
    response = await client.post(
        "/api/v1/works/search", json=request_payload, headers=auth_headers
    )

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_search_works_without_auth_returns_401(client: AsyncClient):
    """Test that search without authentication returns 401."""
    # Arrange
    request_payload = {"query": "test", "page": 1, "limit": 10}

    # Act
    response = await client.post("/api/v1/works/search", json=request_payload)

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_search_works_pagination_works(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that pagination parameters work correctly."""
    # Arrange
    request_payload = {"query": "test", "page": 2, "limit": 5}

    # Act
    response = await client.post(
        "/api/v1/works/search", json=request_payload, headers=auth_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["pagination"]["page"] == 2
    assert data["pagination"]["limit"] == 5


@pytest.mark.asyncio
async def test_search_works_results_sorted_by_relevance(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that results are sorted by search score (highest first)."""
    # Arrange
    request_payload = {"query": "test", "page": 1, "limit": 10}

    # Act
    response = await client.post(
        "/api/v1/works/search", json=request_payload, headers=auth_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    if len(data["data"]) > 1:
        scores = [item["search_score"] for item in data["data"]]
        # Verify descending order
        assert scores == sorted(scores, reverse=True)

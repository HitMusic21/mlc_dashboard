"""Contract test for POST /api/v1/preferences/searches endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_save_search_valid_data_returns_200(
    client: AsyncClient, auth_headers: dict
):
    """Test saving a new search with valid data."""
    request_payload = {
        "name": "Recent Uploads",
        "filters": {
            "date_range": "last_7_days",
            "status": "completed",
            "sort_by": "created_at",
            "sort_order": "desc",
        },
    }

    response = await client.post(
        "/api/v1/preferences/searches", json=request_payload, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "saved_searches" in data
    assert isinstance(data["saved_searches"], list)

    # Verify the new search was added
    search_names = [s["name"] for s in data["saved_searches"]]
    assert "Recent Uploads" in search_names


@pytest.mark.asyncio
async def test_save_search_missing_name_returns_422(
    client: AsyncClient, auth_headers: dict
):
    """Test saving search without required name field."""
    request_payload = {
        "filters": {"date_range": "last_7_days"}  # Missing 'name' field
    }

    response = await client.post(
        "/api/v1/preferences/searches", json=request_payload, headers=auth_headers
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_save_search_empty_name_returns_422(client: AsyncClient, auth_headers: dict):
    """Test saving search with empty name."""
    request_payload = {"name": "", "filters": {}}

    response = await client.post(
        "/api/v1/preferences/searches", json=request_payload, headers=auth_headers
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_save_search_duplicate_name_returns_400(
    client: AsyncClient, auth_headers: dict
):
    """Test saving search with duplicate name."""
    request_payload = {"name": "My Search", "filters": {"status": "active"}}

    # First save should succeed
    response1 = await client.post(
        "/api/v1/preferences/searches", json=request_payload, headers=auth_headers
    )
    assert response1.status_code == 200

    # Second save with same name should fail
    response2 = await client.post(
        "/api/v1/preferences/searches", json=request_payload, headers=auth_headers
    )
    assert response2.status_code == 400

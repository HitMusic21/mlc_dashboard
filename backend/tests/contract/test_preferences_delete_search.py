"""Contract test for DELETE /api/v1/preferences/searches/{id} endpoint."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_delete_saved_search_returns_200(client: AsyncClient, auth_headers: dict):
    """Test deleting an existing saved search."""
    # First, create a search to delete
    create_payload = {"name": "Temporary Search", "filters": {"status": "active"}}
    create_response = await client.post(
        "/api/v1/preferences/searches", json=create_payload, headers=auth_headers
    )
    assert create_response.status_code == 200

    saved_searches = create_response.json()["saved_searches"]
    search_id = next(s["id"] for s in saved_searches if s["name"] == "Temporary Search")

    # Delete the search
    response = await client.delete(
        f"/api/v1/preferences/searches/{search_id}", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "saved_searches" in data

    # Verify the search was removed
    search_ids = [s["id"] for s in data["saved_searches"]]
    assert search_id not in search_ids


@pytest.mark.asyncio
async def test_delete_nonexistent_search_returns_404(
    client: AsyncClient, auth_headers: dict
):
    """Test deleting a search that doesn't exist."""
    nonexistent_id = str(uuid4())

    response = await client.delete(
        f"/api/v1/preferences/searches/{nonexistent_id}", headers=auth_headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_search_invalid_uuid_returns_422(
    client: AsyncClient, auth_headers: dict
):
    """Test deleting search with invalid UUID format."""
    response = await client.delete(
        "/api/v1/preferences/searches/not-a-uuid", headers=auth_headers
    )

    assert response.status_code == 422

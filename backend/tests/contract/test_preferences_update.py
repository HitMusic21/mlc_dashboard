"""Contract test for PUT /api/v1/preferences endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_update_preferences_valid_data_returns_200(
    client: AsyncClient, auth_headers: dict
):
    """Test preferences update with valid data."""
    request_payload = {"theme": "dark", "items_per_page": 100, "notification_email": False}

    response = await client.put("/api/v1/preferences", json=request_payload, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["theme"] == "dark"
    assert data["items_per_page"] == 100
    assert data["notification_email"] is False


@pytest.mark.asyncio
async def test_update_preferences_invalid_theme_returns_422(
    client: AsyncClient, auth_headers: dict
):
    """Test update with invalid theme value."""
    request_payload = {"theme": "invalid_theme"}

    response = await client.put("/api/v1/preferences", json=request_payload, headers=auth_headers)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_preferences_items_per_page_out_of_range_returns_422(
    client: AsyncClient, auth_headers: dict
):
    """Test update with items_per_page out of valid range."""
    request_payload = {"items_per_page": 5}  # Below minimum 10

    response = await client.put("/api/v1/preferences", json=request_payload, headers=auth_headers)

    assert response.status_code == 422

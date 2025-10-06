"""Contract test for GET /api/v1/preferences endpoint.

This test validates the user preferences GET API contract:
- Response schema validation
- Authentication requirement
- Default preferences when none exist
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_preferences_with_auth_returns_200(
    client: AsyncClient, auth_headers: dict
):
    """Test that authenticated user can get their preferences."""
    # Act
    response = await client.get("/api/v1/preferences", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Validate response schema
    assert "id" in data
    assert "user_id" in data
    assert "dashboard_layout" in data
    assert "saved_searches" in data
    assert "theme" in data
    assert "items_per_page" in data
    assert "notification_email" in data
    assert "notification_push" in data
    assert "language" in data
    assert "timezone" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Validate data types
    assert isinstance(data["id"], str)
    assert isinstance(data["user_id"], str)
    assert data["dashboard_layout"] is None or isinstance(data["dashboard_layout"], dict)
    assert data["saved_searches"] is None or isinstance(data["saved_searches"], list)
    assert isinstance(data["theme"], str)
    assert data["theme"] in ["light", "dark", "auto"]
    assert isinstance(data["items_per_page"], int)
    assert 10 <= data["items_per_page"] <= 200
    assert isinstance(data["notification_email"], bool)
    assert isinstance(data["notification_push"], bool)
    assert isinstance(data["language"], str)
    assert isinstance(data["timezone"], str)


@pytest.mark.asyncio
async def test_get_preferences_without_auth_returns_401(client: AsyncClient):
    """Test that unauthenticated request returns 401."""
    # Act
    response = await client.get("/api/v1/preferences")

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_preferences_returns_defaults_when_none_exist(
    client: AsyncClient, auth_headers: dict
):
    """Test that default preferences are returned when user has no preferences yet."""
    # Act
    response = await client.get("/api/v1/preferences", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Should have default values
    assert data["theme"] == "light"  # Default theme
    assert data["items_per_page"] == 50  # Default pagination
    assert data["notification_email"] is True  # Default notification settings
    assert data["notification_push"] is True
    assert data["language"] == "en"  # Default language
    assert data["timezone"] == "UTC"  # Default timezone

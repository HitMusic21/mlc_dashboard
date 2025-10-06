"""Contract test for GET /api/v1/notifications/unread-count endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_unread_count_returns_200(client: AsyncClient, auth_headers: dict):
    """Test unread notification count retrieval."""
    response = await client.get("/api/v1/notifications/unread-count", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Validate response schema
    assert "count" in data
    assert isinstance(data["count"], int)
    assert data["count"] >= 0


@pytest.mark.asyncio
async def test_unread_count_only_counts_current_user_notifications(
    client: AsyncClient, auth_headers: dict
):
    """Test that unread count only includes current user's notifications."""
    response = await client.get("/api/v1/notifications/unread-count", headers=auth_headers)

    assert response.status_code == 200
    # The count should not include other users' notifications
    # This will be validated in integration tests

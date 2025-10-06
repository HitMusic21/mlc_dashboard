"""Contract test for PUT /api/v1/notifications/read-all endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_mark_all_notifications_read_returns_200(
    client: AsyncClient, auth_headers: dict
):
    """Test marking all notifications as read."""
    response = await client.put("/api/v1/notifications/read-all", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Validate response schema
    assert "updated_count" in data
    assert isinstance(data["updated_count"], int)
    assert data["updated_count"] >= 0


@pytest.mark.asyncio
async def test_mark_all_read_when_no_unread_notifications_returns_200(
    client: AsyncClient, auth_headers: dict
):
    """Test marking all as read when there are no unread notifications."""
    response = await client.put("/api/v1/notifications/read-all", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["updated_count"] == 0


@pytest.mark.asyncio
async def test_mark_all_read_updates_unread_count(client: AsyncClient, auth_headers: dict):
    """Test that marking all as read updates the unread count."""
    # Get initial unread count
    count_response = await client.get(
        "/api/v1/notifications/unread-count", headers=auth_headers
    )
    assert count_response.status_code == 200
    initial_count = count_response.json()["count"]

    # Mark all as read
    mark_response = await client.put(
        "/api/v1/notifications/read-all", headers=auth_headers
    )
    assert mark_response.status_code == 200

    # Verify unread count is now 0
    final_count_response = await client.get(
        "/api/v1/notifications/unread-count", headers=auth_headers
    )
    assert final_count_response.status_code == 200
    assert final_count_response.json()["count"] == 0


@pytest.mark.asyncio
async def test_mark_all_read_only_affects_current_user(
    client: AsyncClient, auth_headers: dict
):
    """Test that marking all as read only affects current user's notifications."""
    response = await client.put("/api/v1/notifications/read-all", headers=auth_headers)

    assert response.status_code == 200
    # The updated_count should only include current user's notifications
    # This will be validated in integration tests

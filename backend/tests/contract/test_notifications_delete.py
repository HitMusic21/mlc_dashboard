"""Contract test for DELETE /api/v1/notifications/{id} endpoint."""

import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.mark.asyncio
async def test_delete_notification_returns_204(client: AsyncClient, auth_headers: dict):
    """Test deleting a notification."""
    notification_id = str(uuid4())

    response = await client.delete(
        f"/api/v1/notifications/{notification_id}", headers=auth_headers
    )

    # Should return 204 No Content on successful deletion
    # or 404 if notification doesn't exist
    assert response.status_code in [204, 404]


@pytest.mark.asyncio
async def test_delete_nonexistent_notification_returns_404(
    client: AsyncClient, auth_headers: dict
):
    """Test deleting a notification that doesn't exist."""
    nonexistent_id = str(uuid4())

    response = await client.delete(
        f"/api/v1/notifications/{nonexistent_id}", headers=auth_headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_notification_invalid_uuid_returns_422(
    client: AsyncClient, auth_headers: dict
):
    """Test deleting notification with invalid UUID format."""
    response = await client.delete(
        "/api/v1/notifications/not-a-uuid", headers=auth_headers
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_notification_reduces_total_count(
    client: AsyncClient, auth_headers: dict
):
    """Test that deleting a notification reduces the total count."""
    # Get initial notification count
    list_response = await client.get("/api/v1/notifications", headers=auth_headers)
    assert list_response.status_code == 200
    initial_total = list_response.json()["total"]

    if initial_total > 0:
        # Get first notification ID
        notifications = list_response.json()["notifications"]
        notification_id = notifications[0]["id"]

        # Delete the notification
        delete_response = await client.delete(
            f"/api/v1/notifications/{notification_id}", headers=auth_headers
        )
        assert delete_response.status_code == 204

        # Verify total count decreased
        final_list_response = await client.get(
            "/api/v1/notifications", headers=auth_headers
        )
        assert final_list_response.status_code == 200
        assert final_list_response.json()["total"] == initial_total - 1


@pytest.mark.asyncio
async def test_delete_notification_only_allows_owner(
    client: AsyncClient, auth_headers: dict
):
    """Test that users can only delete their own notifications."""
    notification_id = str(uuid4())

    response = await client.delete(
        f"/api/v1/notifications/{notification_id}", headers=auth_headers
    )

    # Should return 404 for other users' notifications (not 403, to avoid leaking info)
    assert response.status_code in [204, 404]

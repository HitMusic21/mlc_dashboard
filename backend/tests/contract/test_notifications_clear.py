"""Contract test for DELETE /api/v1/notifications/clear-read endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_clear_read_notifications_returns_200(
    client: AsyncClient, auth_headers: dict
):
    """Test clearing all read notifications."""
    response = await client.delete("/api/v1/notifications/clear-read", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Validate response schema
    assert "deleted_count" in data
    assert isinstance(data["deleted_count"], int)
    assert data["deleted_count"] >= 0


@pytest.mark.asyncio
async def test_clear_read_when_no_read_notifications_returns_200(
    client: AsyncClient, auth_headers: dict
):
    """Test clearing read notifications when there are none."""
    response = await client.delete("/api/v1/notifications/clear-read", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["deleted_count"] == 0


@pytest.mark.asyncio
async def test_clear_read_does_not_delete_unread_notifications(
    client: AsyncClient, auth_headers: dict
):
    """Test that clear-read only deletes read notifications, not unread ones."""
    # Get initial unread count
    count_response = await client.get(
        "/api/v1/notifications/unread-count", headers=auth_headers
    )
    assert count_response.status_code == 200
    initial_unread = count_response.json()["count"]

    # Clear read notifications
    clear_response = await client.delete(
        "/api/v1/notifications/clear-read", headers=auth_headers
    )
    assert clear_response.status_code == 200

    # Verify unread count is unchanged
    final_count_response = await client.get(
        "/api/v1/notifications/unread-count", headers=auth_headers
    )
    assert final_count_response.status_code == 200
    assert final_count_response.json()["count"] == initial_unread


@pytest.mark.asyncio
async def test_clear_read_reduces_total_count(client: AsyncClient, auth_headers: dict):
    """Test that clearing read notifications reduces total count."""
    # Get initial total count
    list_response = await client.get("/api/v1/notifications", headers=auth_headers)
    assert list_response.status_code == 200
    initial_total = list_response.json()["total"]

    # Mark all as read
    await client.put("/api/v1/notifications/read-all", headers=auth_headers)

    # Clear read notifications
    clear_response = await client.delete(
        "/api/v1/notifications/clear-read", headers=auth_headers
    )
    assert clear_response.status_code == 200
    deleted_count = clear_response.json()["deleted_count"]

    # Verify total count decreased by deleted_count
    final_list_response = await client.get("/api/v1/notifications", headers=auth_headers)
    assert final_list_response.status_code == 200
    final_total = final_list_response.json()["total"]
    assert final_total == initial_total - deleted_count


@pytest.mark.asyncio
async def test_clear_read_only_affects_current_user(
    client: AsyncClient, auth_headers: dict
):
    """Test that clear-read only deletes current user's read notifications."""
    response = await client.delete("/api/v1/notifications/clear-read", headers=auth_headers)

    assert response.status_code == 200
    # The deleted_count should only include current user's read notifications
    # This will be validated in integration tests

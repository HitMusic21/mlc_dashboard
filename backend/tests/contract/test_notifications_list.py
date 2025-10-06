"""Contract test for GET /api/v1/notifications endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_notifications_returns_200_with_pagination(
    client: AsyncClient, auth_headers: dict
):
    """Test notifications list with pagination."""
    response = await client.get(
        "/api/v1/notifications?page=1&limit=20", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Validate response schema
    assert "notifications" in data
    assert "total" in data
    assert "page" in data
    assert "limit" in data
    assert "has_more" in data

    assert isinstance(data["notifications"], list)
    assert isinstance(data["total"], int)
    assert isinstance(data["page"], int)
    assert isinstance(data["limit"], int)
    assert isinstance(data["has_more"], bool)


@pytest.mark.asyncio
async def test_get_notifications_filter_by_is_read_returns_200(
    client: AsyncClient, auth_headers: dict
):
    """Test filtering notifications by read status."""
    response = await client.get(
        "/api/v1/notifications?is_read=false", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # All returned notifications should be unread
    for notification in data["notifications"]:
        assert notification["is_read"] is False


@pytest.mark.asyncio
async def test_get_notifications_ordered_by_created_at_desc(
    client: AsyncClient, auth_headers: dict
):
    """Test notifications are ordered by created_at descending (newest first)."""
    response = await client.get("/api/v1/notifications", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    notifications = data["notifications"]
    if len(notifications) > 1:
        # Verify descending order
        for i in range(len(notifications) - 1):
            assert notifications[i]["created_at"] >= notifications[i + 1]["created_at"]

"""Contract test for GET /api/v1/catalog/uploads endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_uploads_returns_paginated_list(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that GET /catalog/uploads returns paginated list."""
    response = await client.get("/api/v1/catalog/uploads", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_get_uploads_with_status_filter(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that status filter works."""
    response = await client.get(
        "/api/v1/catalog/uploads?status=completed", headers=auth_headers
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_uploads_without_auth_returns_401(client: AsyncClient):
    """Test that uploads without auth returns 401."""
    response = await client.get("/api/v1/catalog/uploads")
    assert response.status_code == 401

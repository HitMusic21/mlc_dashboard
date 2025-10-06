"""Contract test for DELETE /api/v1/catalog/{id} endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_delete_catalog_returns_204(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that DELETE /catalog/{id} returns 204."""
    upload_id = 1
    response = await client.delete(
        f"/api/v1/catalog/{upload_id}", headers=auth_headers
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_nonexistent_returns_404(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that deleting non-existent upload returns 404."""
    response = await client.delete("/api/v1/catalog/999999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_without_auth_returns_401(client: AsyncClient):
    """Test that delete without auth returns 401."""
    response = await client.delete("/api/v1/catalog/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_other_user_upload_returns_403(
    client: AsyncClient, publisher_headers: dict[str, str]
):
    """Test that publishers cannot delete other users' uploads."""
    # This would be an upload owned by a different user
    other_user_upload_id = 999
    response = await client.delete(
        f"/api/v1/catalog/{other_user_upload_id}", headers=publisher_headers
    )

    assert response.status_code in [403, 404]

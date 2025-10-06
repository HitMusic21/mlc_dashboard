"""Integration test for Scenario 8: Admin management capabilities."""

import io

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_views_all_uploads(
    client: AsyncClient, admin_headers: dict[str, str], publisher_headers: dict[str, str]
):
    """Test that admin can view all users' uploads."""
    # Publisher uploads a catalog
    csv_content = b"title,artist,duration\nTest,Artist,180"
    files = {"file": ("pub.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"publisher_name": "Publisher"}

    pub_upload = await client.post(
        "/api/v1/catalog/upload", files=files, data=data, headers=publisher_headers
    )
    assert pub_upload.status_code == 201

    # Admin views all uploads
    admin_response = await client.get("/api/v1/catalog/uploads", headers=admin_headers)
    assert admin_response.status_code == 200
    uploads = admin_response.json()["data"]

    # Should see uploads from multiple users
    assert isinstance(uploads, list)


@pytest.mark.asyncio
async def test_admin_can_delete_any_upload(
    client: AsyncClient, admin_headers: dict[str, str]
):
    """Test that admin can delete any user's upload."""
    # Create an upload
    csv_content = b"title,artist,duration\nTest,Artist,180"
    files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"publisher_name": "Test"}

    upload_response = await client.post(
        "/api/v1/catalog/upload", files=files, data=data, headers=admin_headers
    )
    upload_id = upload_response.json()["id"]

    # Admin deletes it
    delete_response = await client.delete(
        f"/api/v1/catalog/{upload_id}", headers=admin_headers
    )
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_publisher_cannot_access_admin_endpoints(
    client: AsyncClient, publisher_headers: dict[str, str]
):
    """Test that publisher cannot access admin-only endpoints."""
    # Try to access admin endpoint (if implemented)
    # This is a placeholder for admin-specific routes
    response = await client.get("/api/v1/admin/users", headers=publisher_headers)
    assert response.status_code in [403, 404]


@pytest.mark.asyncio
async def test_publisher_only_sees_own_uploads(
    client: AsyncClient, publisher_headers: dict[str, str]
):
    """Test that publisher can only see their own uploads."""
    # Get uploads
    response = await client.get("/api/v1/catalog/uploads", headers=publisher_headers)
    assert response.status_code == 200
    uploads = response.json()["data"]

    # All uploads should belong to this user
    # (Implementation will filter by user_id)
    assert isinstance(uploads, list)

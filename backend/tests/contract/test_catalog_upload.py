"""Contract test for POST /api/v1/catalog/upload endpoint."""

import io

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_catalog_csv_returns_201(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that catalog upload with CSV file returns 201."""
    # Arrange
    csv_content = b"title,artist,duration\nTest Song,Test Artist,180"
    files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"publisher_name": "Test Publisher"}

    # Act
    response = await client.post(
        "/api/v1/catalog/upload", files=files, data=data, headers=auth_headers
    )

    # Assert
    assert response.status_code == 201
    result = response.json()

    # Validate CatalogUpload schema
    assert "id" in result
    assert "filename" in result
    assert "publisher_name" in result
    assert "status" in result
    assert "created_at" in result
    assert result["status"] == "pending"


@pytest.mark.asyncio
async def test_upload_invalid_file_format_returns_400(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that invalid file format returns 400."""
    # Arrange
    files = {"file": ("test.txt", io.BytesIO(b"invalid"), "text/plain")}
    data = {"publisher_name": "Test Publisher"}

    # Act
    response = await client.post(
        "/api/v1/catalog/upload", files=files, data=data, headers=auth_headers
    )

    # Assert
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_without_auth_returns_401(client: AsyncClient):
    """Test that upload without auth returns 401."""
    files = {"file": ("test.csv", io.BytesIO(b"data"), "text/csv")}
    response = await client.post("/api/v1/catalog/upload", files=files)
    assert response.status_code == 401

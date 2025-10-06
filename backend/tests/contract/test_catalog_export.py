"""Contract test for GET /api/v1/catalog/{id}/export endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_export_csv_returns_file(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that CSV export returns file."""
    upload_id = 1
    response = await client.get(
        f"/api/v1/catalog/{upload_id}/export?format=csv", headers=auth_headers
    )

    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_export_excel_returns_file(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that Excel export returns file."""
    upload_id = 1
    response = await client.get(
        f"/api/v1/catalog/{upload_id}/export?format=excel", headers=auth_headers
    )

    assert response.status_code == 200
    assert "spreadsheet" in response.headers.get("content-type", "").lower()


@pytest.mark.asyncio
async def test_export_with_confidence_filter(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that confidence filter works in export."""
    upload_id = 1
    response = await client.get(
        f"/api/v1/catalog/{upload_id}/export?format=csv&confidence=high",
        headers=auth_headers,
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_export_without_auth_returns_401(client: AsyncClient):
    """Test that export without auth returns 401."""
    response = await client.get("/api/v1/catalog/1/export?format=csv")
    assert response.status_code == 401

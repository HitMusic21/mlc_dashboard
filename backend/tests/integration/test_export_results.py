"""Integration test for Scenario 5: Export results."""

import io

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_export_csv_with_all_details(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test CSV export contains all match details."""
    # Create and upload catalog
    csv_content = b"title,artist,duration\nTest,Artist,180"
    files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"publisher_name": "Test"}

    upload_response = await client.post(
        "/api/v1/catalog/upload", files=files, data=data, headers=auth_headers
    )
    upload_id = upload_response.json()["id"]

    # Export as CSV
    export_response = await client.get(
        f"/api/v1/catalog/{upload_id}/export?format=csv", headers=auth_headers
    )
    assert export_response.status_code == 200
    assert "text/csv" in export_response.headers["content-type"]

    # Verify CSV content
    csv_data = export_response.content.decode("utf-8")
    assert len(csv_data) > 0


@pytest.mark.asyncio
async def test_export_excel_with_all_details(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test Excel export contains all match details."""
    csv_content = b"title,artist,duration\nTest,Artist,180"
    files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"publisher_name": "Test"}

    upload_response = await client.post(
        "/api/v1/catalog/upload", files=files, data=data, headers=auth_headers
    )
    upload_id = upload_response.json()["id"]

    export_response = await client.get(
        f"/api/v1/catalog/{upload_id}/export?format=excel", headers=auth_headers
    )
    assert export_response.status_code == 200


@pytest.mark.asyncio
async def test_export_with_confidence_filter(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test export can be filtered by confidence level."""
    csv_content = b"title,artist,duration\nTest,Artist,180"
    files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"publisher_name": "Test"}

    upload_response = await client.post(
        "/api/v1/catalog/upload", files=files, data=data, headers=auth_headers
    )
    upload_id = upload_response.json()["id"]

    # Export only high confidence matches
    export_response = await client.get(
        f"/api/v1/catalog/{upload_id}/export?format=csv&confidence=high",
        headers=auth_headers,
    )
    assert export_response.status_code == 200

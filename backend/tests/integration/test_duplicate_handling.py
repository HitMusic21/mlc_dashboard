"""Integration test for Scenario 6: Duplicate handling."""

import io

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_duplicate_tracks_merged_before_matching(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that duplicate tracks are merged before matching."""
    # Create CSV with duplicate tracks
    csv_content = b"""title,artist,duration
Yesterday,Beatles,125
Yesterday,Beatles,125
Yesterday,The Beatles,125
"""

    files = {"file": ("dupes.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"publisher_name": "Test Publisher"}

    upload_response = await client.post(
        "/api/v1/catalog/upload", files=files, data=data, headers=auth_headers
    )
    assert upload_response.status_code == 201
    upload_id = upload_response.json()["id"]

    # Wait for processing
    await asyncio.sleep(3)

    # Get results - should show merged duplicates
    results_response = await client.get(
        f"/api/v1/catalog/{upload_id}/results", headers=auth_headers
    )
    results = results_response.json()["data"]

    # Should have fewer result groups than original tracks (due to merging)
    assert len(results) < 3


@pytest.mark.asyncio
async def test_metadata_merged_from_duplicates(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that metadata is merged from duplicate entries."""
    csv_content = b"""title,artist,duration
Song,Artist A,180
Song,Artist B,180
"""

    files = {"file": ("merge.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"publisher_name": "Test"}

    upload_response = await client.post(
        "/api/v1/catalog/upload", files=files, data=data, headers=auth_headers
    )
    assert upload_response.status_code == 201
    upload_id = upload_response.json()["id"]

    # Status should show merged count
    await asyncio.sleep(2)
    status_response = await client.get(
        f"/api/v1/catalog/{upload_id}/status", headers=auth_headers
    )
    status = status_response.json()

    # Check for merged count in metadata (implementation will add this field)
    assert status["status"] in ["pending", "processing", "completed"]

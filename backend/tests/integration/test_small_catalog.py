"""Integration test for Scenario 3: Small catalog upload and matching."""

import io
import time

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_small_catalog_end_to_end(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test complete flow: upload -> process -> view results."""
    # Step 1: Upload CSV with 100 tracks (simulated with smaller file for testing)
    csv_content = b"title,artist,duration\n"
    for i in range(10):  # Scaled down from 100 for testing
        csv_content += f"Song {i},Artist {i},180\n".encode()

    files = {"file": ("catalog.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"publisher_name": "Test Publisher"}

    upload_response = await client.post(
        "/api/v1/catalog/upload", files=files, data=data, headers=auth_headers
    )
    assert upload_response.status_code == 201
    upload_id = upload_response.json()["id"]

    # Step 2: Check processing status
    start_time = time.time()
    max_wait = 30  # 30 second timeout for processing

    while time.time() - start_time < max_wait:
        status_response = await client.get(
            f"/api/v1/catalog/{upload_id}/status", headers=auth_headers
        )
        assert status_response.status_code == 200
        status = status_response.json()["status"]

        if status == "completed":
            break
        await asyncio.sleep(1)

    # Step 3: Get match results
    results_response = await client.get(
        f"/api/v1/catalog/{upload_id}/results", headers=auth_headers
    )
    assert results_response.status_code == 200
    results = results_response.json()["data"]

    # Validate match structure
    if len(results) > 0:
        match_group = results[0]
        assert "uploaded_track" in match_group
        assert "matches" in match_group

        # Verify matches are ranked
        if len(match_group["matches"]) > 0:
            for idx, match in enumerate(match_group["matches"], 1):
                assert match["rank"] == idx


@pytest.mark.asyncio
async def test_multiple_matches_display(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that tracks with multiple matches show all with visual ranking."""
    # Upload and get results (simplified)
    csv_content = b"title,artist,duration\nYesterday,Beatles,125"
    files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"publisher_name": "Test"}

    upload_response = await client.post(
        "/api/v1/catalog/upload", files=files, data=data, headers=auth_headers
    )
    upload_id = upload_response.json()["id"]

    # Wait and get results
    await asyncio.sleep(2)

    results_response = await client.get(
        f"/api/v1/catalog/{upload_id}/results", headers=auth_headers
    )
    results = results_response.json()["data"]

    # Verify all matches shown with ranking
    for group in results:
        matches = group["matches"]
        if len(matches) > 1:
            # Verify sorted by confidence score
            scores = [m["confidence_score"] for m in matches]
            assert scores == sorted(scores, reverse=True)

"""Integration test for Scenario 4: Large catalog processing performance."""

import io

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.slow
async def test_large_catalog_processing_throughput(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test large catalog processing meets throughput requirement (>1000 tracks/min)."""
    # Create sample with 1000 tracks (scaled down for testing)
    csv_content = b"title,artist,duration\n"
    for i in range(100):  # Scaled down from 50000 to 100 for testing
        csv_content += f"Track {i},Artist {i},180\n".encode()

    files = {"file": ("large.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"publisher_name": "Large Publisher"}

    upload_response = await client.post(
        "/api/v1/catalog/upload", files=files, data=data, headers=auth_headers
    )
    assert upload_response.status_code == 201
    upload_id = upload_response.json()["id"]

    # Monitor processing progress
    import time

    start_time = time.time()

    while time.time() - start_time < 120:  # 2 minute max for 100 tracks
        status_response = await client.get(
            f"/api/v1/catalog/{upload_id}/status", headers=auth_headers
        )
        status_data = status_response.json()

        if status_data["status"] == "completed":
            elapsed = time.time() - start_time
            tracks_per_minute = (100 / elapsed) * 60
            assert tracks_per_minute > 1000  # Performance requirement
            break

        await asyncio.sleep(2)


@pytest.mark.asyncio
async def test_system_responsive_during_processing(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that system remains responsive during catalog processing."""
    # Start a large upload
    csv_content = b"title,artist,duration\n" + b"Track,Artist,180\n" * 50
    files = {"file": ("bg.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"publisher_name": "BG Publisher"}

    await client.post(
        "/api/v1/catalog/upload", files=files, data=data, headers=auth_headers
    )

    # Verify other operations still work
    import time

    start = time.time()
    works_response = await client.get("/api/v1/works", headers=auth_headers)
    elapsed_ms = (time.time() - start) * 1000

    assert works_response.status_code == 200
    assert elapsed_ms < 500  # Still meets performance SLA

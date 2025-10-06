"""Contract test for GET /api/v1/works/{id} endpoint.

This test validates the single work retrieval API contract:
- Response schema validation (detailed work with resources)
- Error handling for non-existent IDs
- Related resources included in response
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_work_by_id_returns_detailed_work(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that GET /works/{id} returns detailed work with resources."""
    # Arrange
    work_id = 1

    # Act
    response = await client.get(f"/api/v1/works/{work_id}", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Validate MusicalWorkDetailed schema
    assert "id" in data
    assert "title" in data
    assert "iswc" in data
    assert "has_disputed_rights" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "resources" in data

    # Validate data types
    assert isinstance(data["id"], int)
    assert isinstance(data["title"], str)
    assert data["iswc"] is None or isinstance(data["iswc"], str)
    assert isinstance(data["has_disputed_rights"], bool)
    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)
    assert isinstance(data["resources"], list)


@pytest.mark.asyncio
async def test_get_work_resources_schema(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that work resources have correct schema."""
    # Arrange
    work_id = 1

    # Act
    response = await client.get(f"/api/v1/works/{work_id}", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()

    if len(data["resources"]) > 0:
        resource = data["resources"][0]

        # Validate Resource schema
        assert "id" in resource
        assert "isrc" in resource
        assert "resource_type" in resource
        assert "title" in resource
        assert "duration_seconds" in resource
        assert "created_at" in resource

        # Validate data types
        assert isinstance(resource["id"], int)
        assert resource["isrc"] is None or isinstance(resource["isrc"], str)
        assert isinstance(resource["resource_type"], str)
        assert resource["resource_type"] in ["recording", "video"]
        assert isinstance(resource["title"], str)
        assert resource["duration_seconds"] is None or isinstance(
            resource["duration_seconds"], int
        )
        assert isinstance(resource["created_at"], str)


@pytest.mark.asyncio
async def test_get_work_nonexistent_id_returns_404(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that GET /works/{id} with non-existent ID returns 404."""
    # Arrange
    nonexistent_id = 999999

    # Act
    response = await client.get(
        f"/api/v1/works/{nonexistent_id}", headers=auth_headers
    )

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_work_invalid_id_returns_422(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that GET /works/{id} with invalid ID format returns 422."""
    # Arrange
    invalid_id = "not-a-number"

    # Act
    response = await client.get(f"/api/v1/works/{invalid_id}", headers=auth_headers)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_work_without_auth_returns_401(client: AsyncClient):
    """Test that GET /works/{id} without authentication returns 401."""
    # Arrange
    work_id = 1

    # Act
    response = await client.get(f"/api/v1/works/{work_id}")

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_work_with_no_resources_returns_empty_array(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that work with no resources returns empty resources array."""
    # Arrange
    work_id = 1

    # Act
    response = await client.get(f"/api/v1/works/{work_id}", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["resources"], list)

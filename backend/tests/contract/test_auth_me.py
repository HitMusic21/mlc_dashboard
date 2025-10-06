"""Contract test for GET /api/v1/auth/me endpoint.

This test validates the "current user" API contract:
- Response schema validation (User object)
- Requires valid authentication token
- Error handling for missing/invalid token
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_me_with_valid_token_returns_user(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that GET /auth/me with valid token returns user object."""
    # Act
    response = await client.get("/api/v1/auth/me", headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Validate response schema
    assert "id" in data
    assert "email" in data
    assert "full_name" in data
    assert "role" in data
    assert "is_active" in data
    assert "created_at" in data

    # Validate data types
    assert isinstance(data["id"], int)
    assert isinstance(data["email"], str)
    assert isinstance(data["full_name"], str)
    assert isinstance(data["role"], str)
    assert isinstance(data["is_active"], bool)
    assert isinstance(data["created_at"], str)

    # Validate role enum
    assert data["role"] in ["publisher", "admin"]

    # Validate email format
    assert "@" in data["email"]


@pytest.mark.asyncio
async def test_get_me_without_token_returns_401(client: AsyncClient):
    """Test that GET /auth/me without token returns 401 Unauthorized."""
    # Act
    response = await client.get("/api/v1/auth/me")

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_me_with_invalid_token_returns_401(client: AsyncClient):
    """Test that GET /auth/me with invalid token returns 401 Unauthorized."""
    # Arrange
    invalid_headers = {"Authorization": "Bearer invalid-token"}

    # Act
    response = await client.get("/api/v1/auth/me", headers=invalid_headers)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_me_with_expired_token_returns_401(client: AsyncClient):
    """Test that GET /auth/me with expired token returns 401 Unauthorized."""
    # Arrange
    expired_headers = {"Authorization": "Bearer expired-token"}

    # Act
    response = await client.get("/api/v1/auth/me", headers=expired_headers)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_get_me_publisher_role_returns_publisher_data(
    client: AsyncClient, publisher_headers: dict[str, str]
):
    """Test that GET /auth/me for publisher role returns correct role."""
    # Act
    response = await client.get("/api/v1/auth/me", headers=publisher_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "publisher"


@pytest.mark.asyncio
async def test_get_me_admin_role_returns_admin_data(
    client: AsyncClient, admin_headers: dict[str, str]
):
    """Test that GET /auth/me for admin role returns correct role."""
    # Act
    response = await client.get("/api/v1/auth/me", headers=admin_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"

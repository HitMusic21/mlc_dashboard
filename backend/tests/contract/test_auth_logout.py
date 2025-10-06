"""Contract test for POST /api/v1/auth/logout endpoint.

This test validates the logout API contract:
- Successful logout returns 204 No Content
- Requires valid authentication token
- Error handling for invalid/missing token
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_logout_with_valid_token_returns_204(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that logout with valid token returns 204 No Content."""
    # Act
    response = await client.post("/api/v1/auth/logout", headers=auth_headers)

    # Assert
    assert response.status_code == 204
    assert response.content == b""


@pytest.mark.asyncio
async def test_logout_without_token_returns_401(client: AsyncClient):
    """Test that logout without authentication token returns 401 Unauthorized."""
    # Act
    response = await client.post("/api/v1/auth/logout")

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_logout_with_invalid_token_returns_401(client: AsyncClient):
    """Test that logout with invalid token returns 401 Unauthorized."""
    # Arrange
    invalid_headers = {"Authorization": "Bearer invalid-token"}

    # Act
    response = await client.post("/api/v1/auth/logout", headers=invalid_headers)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_logout_with_expired_token_returns_401(client: AsyncClient):
    """Test that logout with expired token returns 401 Unauthorized."""
    # Arrange
    expired_headers = {"Authorization": "Bearer expired-token"}

    # Act
    response = await client.post("/api/v1/auth/logout", headers=expired_headers)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_logout_with_malformed_header_returns_401(client: AsyncClient):
    """Test that logout with malformed authorization header returns 401."""
    # Arrange
    malformed_headers = {"Authorization": "InvalidFormat token"}

    # Act
    response = await client.post("/api/v1/auth/logout", headers=malformed_headers)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data

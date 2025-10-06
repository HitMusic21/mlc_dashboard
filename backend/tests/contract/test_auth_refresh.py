"""Contract test for POST /api/v1/auth/refresh endpoint.

This test validates the token refresh API contract:
- Request schema validation (refresh_token)
- Response schema validation (new access and refresh tokens)
- Error handling for invalid/expired tokens
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_refresh_valid_token_returns_new_tokens(client: AsyncClient):
    """Test that refresh with valid token returns new access and refresh tokens."""
    # Arrange
    request_payload = {"refresh_token": "valid-refresh-token-placeholder"}

    # Act
    response = await client.post("/api/v1/auth/refresh", json=request_payload)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Validate response schema (same as login)
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert "expires_in" in data

    # Validate data types
    assert isinstance(data["access_token"], str)
    assert isinstance(data["refresh_token"], str)
    assert data["token_type"] == "Bearer"
    assert isinstance(data["expires_in"], int)
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_refresh_invalid_token_returns_401(client: AsyncClient):
    """Test that refresh with invalid token returns 401 Unauthorized."""
    # Arrange
    request_payload = {"refresh_token": "invalid-token"}

    # Act
    response = await client.post("/api/v1/auth/refresh", json=request_payload)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_refresh_expired_token_returns_401(client: AsyncClient):
    """Test that refresh with expired token returns 401 Unauthorized."""
    # Arrange
    # This would be a token that was valid but has expired
    request_payload = {"refresh_token": "expired-refresh-token"}

    # Act
    response = await client.post("/api/v1/auth/refresh", json=request_payload)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_refresh_missing_token_returns_422(client: AsyncClient):
    """Test that refresh without token returns 422 Unprocessable Entity."""
    # Arrange
    request_payload = {}

    # Act
    response = await client.post("/api/v1/auth/refresh", json=request_payload)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_refresh_empty_token_returns_422(client: AsyncClient):
    """Test that refresh with empty token returns 422 Unprocessable Entity."""
    # Arrange
    request_payload = {"refresh_token": ""}

    # Act
    response = await client.post("/api/v1/auth/refresh", json=request_payload)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_refresh_malformed_token_returns_401(client: AsyncClient):
    """Test that refresh with malformed token returns 401 Unauthorized."""
    # Arrange
    request_payload = {"refresh_token": "not.a.valid.jwt"}

    # Act
    response = await client.post("/api/v1/auth/refresh", json=request_payload)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data

"""Contract test for POST /api/v1/auth/login endpoint.

This test validates the authentication login API contract:
- Request schema validation
- Response schema validation
- Error handling for invalid credentials
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_valid_credentials_returns_tokens(client: AsyncClient):
    """Test that login with valid credentials returns access and refresh tokens."""
    # Arrange
    request_payload = {"email": "test@example.com", "password": "SecurePassword123!"}

    # Act
    response = await client.post("/api/v1/auth/login", json=request_payload)

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Validate response schema
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
async def test_login_invalid_email_returns_401(client: AsyncClient):
    """Test that login with non-existent email returns 401 Unauthorized."""
    # Arrange
    request_payload = {
        "email": "nonexistent@example.com",
        "password": "SomePassword123!",
    }

    # Act
    response = await client.post("/api/v1/auth/login", json=request_payload)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_login_invalid_password_returns_401(client: AsyncClient):
    """Test that login with incorrect password returns 401 Unauthorized."""
    # Arrange
    request_payload = {"email": "test@example.com", "password": "WrongPassword123!"}

    # Act
    response = await client.post("/api/v1/auth/login", json=request_payload)

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_login_missing_email_returns_422(client: AsyncClient):
    """Test that login without email returns 422 Unprocessable Entity."""
    # Arrange
    request_payload = {"password": "SecurePassword123!"}

    # Act
    response = await client.post("/api/v1/auth/login", json=request_payload)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_login_missing_password_returns_422(client: AsyncClient):
    """Test that login without password returns 422 Unprocessable Entity."""
    # Arrange
    request_payload = {"email": "test@example.com"}

    # Act
    response = await client.post("/api/v1/auth/login", json=request_payload)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_login_invalid_email_format_returns_422(client: AsyncClient):
    """Test that login with invalid email format returns 422 Unprocessable Entity."""
    # Arrange
    request_payload = {"email": "not-an-email", "password": "SecurePassword123!"}

    # Act
    response = await client.post("/api/v1/auth/login", json=request_payload)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_login_empty_credentials_returns_422(client: AsyncClient):
    """Test that login with empty credentials returns 422 Unprocessable Entity."""
    # Arrange
    request_payload = {"email": "", "password": ""}

    # Act
    response = await client.post("/api/v1/auth/login", json=request_payload)

    # Assert
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

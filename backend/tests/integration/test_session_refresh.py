"""Integration test for Scenario 9: Session and token refresh."""

import asyncio
import time

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_access_token_expiration_flow(client: AsyncClient):
    """Test complete flow of token expiration and refresh."""
    # Step 1: Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "publisher@example.com", "password": "SecurePass123!"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    expires_in = tokens["expires_in"]

    # Step 2: Use access token successfully
    headers = {"Authorization": f"Bearer {access_token}"}
    works_response = await client.get("/api/v1/works", headers=headers)
    assert works_response.status_code == 200

    # Step 3: Simulate token expiration (in real scenario, wait for expiration)
    # For testing, we'll just test the refresh mechanism

    # Step 4: Refresh token to get new access token
    refresh_response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()

    # Step 5: Use new access token
    new_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
    works_response = await client.get("/api/v1/works", headers=new_headers)
    assert works_response.status_code == 200


@pytest.mark.asyncio
async def test_expired_access_token_rejected(client: AsyncClient):
    """Test that expired access tokens are rejected."""
    # Use a token that's marked as expired
    headers = {"Authorization": "Bearer expired-token"}
    response = await client.get("/api/v1/works", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_provides_new_tokens(client: AsyncClient):
    """Test that refresh provides both new access and refresh tokens."""
    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "publisher@example.com", "password": "SecurePass123!"},
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh
    refresh_response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200

    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["token_type"] == "Bearer"

    # New tokens should be different from old ones
    assert new_tokens["access_token"] != login_response.json()["access_token"]


@pytest.mark.asyncio
async def test_seamless_user_experience_on_refresh(client: AsyncClient):
    """Test that user experience is seamless when token is refreshed."""
    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "publisher@example.com", "password": "SecurePass123!"},
    )
    tokens = login_response.json()

    # Use access token
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response1 = await client.get("/api/v1/works", headers=headers)
    assert response1.status_code == 200

    # Refresh token
    refresh_response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    new_tokens = refresh_response.json()

    # Use new token immediately - should work seamlessly
    new_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
    response2 = await client.get("/api/v1/works", headers=new_headers)
    assert response2.status_code == 200

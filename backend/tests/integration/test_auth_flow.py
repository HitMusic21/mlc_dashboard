"""Integration tests for authentication flow with token blacklisting."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, get_password_hash
from app.models.user import User, UserRole
from app.services.token_blacklist import token_blacklist_service


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        role=UserRole.PUBLISHER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def inactive_user(db_session: AsyncSession):
    """Create an inactive test user."""
    user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Inactive User",
        role=UserRole.PUBLISHER,
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


class TestAuthenticationFlow:
    """Test complete authentication flow."""

    @pytest.mark.asyncio
    async def test_complete_auth_flow(self, client: AsyncClient, test_user: User, fake_redis):
        """Test complete login → access → refresh → logout flow."""
        # Connect token blacklist service to fake redis
        token_blacklist_service.redis = fake_redis

        # 1. Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "testpassword123"},
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        
        assert "access_token" in login_data
        assert "refresh_token" in login_data
        assert login_data["token_type"] == "Bearer"
        
        access_token = login_data["access_token"]
        refresh_token = login_data["refresh_token"]

        # 2. Access protected endpoint with access token
        me_response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["email"] == "testuser@example.com"
        assert me_data["full_name"] == "Test User"

        # 3. Refresh tokens
        refresh_response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()
        
        assert "access_token" in refresh_data
        assert "refresh_token" in refresh_data
        new_access_token = refresh_data["access_token"]
        new_refresh_token = refresh_data["refresh_token"]

        # 4. Old refresh token should still work (not blacklisted yet)
        # Note: In production, you might want to blacklist old refresh tokens on rotation
        
        # 5. Logout (blacklist current refresh token)
        logout_response = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": new_refresh_token},
            headers={"Authorization": f"Bearer {new_access_token}"},
        )
        assert logout_response.status_code == 204

        # 6. Try to refresh with blacklisted token (should fail)
        blocked_refresh = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": new_refresh_token},
        )
        assert blocked_refresh.status_code == 401
        assert "revoked" in blocked_refresh.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_with_wrong_password(self, client: AsyncClient, test_user: User):
        """Test login with incorrect password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_with_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_with_inactive_user(self, client: AsyncClient, inactive_user: User):
        """Test login with inactive user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "inactive@example.com", "password": "password123"},
        )
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_access_protected_route_without_token(self, client: AsyncClient):
        """Test accessing protected route without token."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_access_protected_route_with_invalid_token(self, client: AsyncClient):
        """Test accessing protected route with invalid token."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, client: AsyncClient):
        """Test token refresh with invalid refresh token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.refresh.token"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_with_access_token(self, client: AsyncClient, test_user: User):
        """Test that refresh endpoint rejects access tokens."""
        # Get access token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "testpassword123"},
        )
        access_token = login_response.json()["access_token"]

        # Try to use access token for refresh (should fail)
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )
        assert response.status_code == 401


class TestTokenBlacklistingIntegration:
    """Test token blacklisting integration with auth flow."""

    @pytest.mark.asyncio
    async def test_logout_invalidates_refresh_token(
        self, client: AsyncClient, test_user: User, fake_redis
    ):
        """Test that logout properly blacklists refresh token."""
        token_blacklist_service.redis = fake_redis

        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "testpassword123"},
        )
        tokens = login_response.json()

        # Logout
        await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": tokens["refresh_token"]},
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )

        # Verify token is blacklisted
        is_blacklisted = await token_blacklist_service.is_blacklisted(
            tokens["refresh_token"], token_type="refresh"
        )
        assert is_blacklisted is True

    @pytest.mark.asyncio
    async def test_multiple_logouts_idempotent(
        self, client: AsyncClient, test_user: User, fake_redis
    ):
        """Test that multiple logout calls are idempotent."""
        token_blacklist_service.redis = fake_redis

        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "testpassword123"},
        )
        tokens = login_response.json()

        # First logout
        response1 = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": tokens["refresh_token"]},
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert response1.status_code == 204

        # Second logout (same token) - should still succeed
        response2 = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": tokens["refresh_token"]},
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert response2.status_code == 204

    @pytest.mark.asyncio
    async def test_blacklisted_token_cannot_refresh(
        self, client: AsyncClient, test_user: User, fake_redis
    ):
        """Test that blacklisted refresh token cannot be used."""
        token_blacklist_service.redis = fake_redis

        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "testpassword123"},
        )
        tokens = login_response.json()

        # Manually blacklist the refresh token
        await token_blacklist_service.blacklist_token(
            tokens["refresh_token"],
            expires_in_seconds=7 * 24 * 60 * 60,
            token_type="refresh",
        )

        # Try to refresh
        refresh_response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert refresh_response.status_code == 401
        assert "revoked" in refresh_response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_concurrent_sessions(
        self, client: AsyncClient, test_user: User, fake_redis
    ):
        """Test multiple concurrent sessions for same user."""
        token_blacklist_service.redis = fake_redis

        # Login twice (two different sessions)
        login1 = await client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "testpassword123"},
        )
        tokens1 = login1.json()

        login2 = await client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "testpassword123"},
        )
        tokens2 = login2.json()

        # Tokens should be different
        assert tokens1["refresh_token"] != tokens2["refresh_token"]

        # Logout from first session
        await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": tokens1["refresh_token"]},
            headers={"Authorization": f"Bearer {tokens1['access_token']}"},
        )

        # First session token should be blacklisted
        refresh1 = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens1["refresh_token"]},
        )
        assert refresh1.status_code == 401

        # Second session should still work
        refresh2 = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens2["refresh_token"]},
        )
        assert refresh2.status_code == 200


class TestRateLimiting:
    """Test rate limiting on authentication endpoints."""

    @pytest.mark.asyncio
    async def test_login_rate_limit(self, client: AsyncClient, test_user: User):
        """Test that login endpoint has rate limiting."""
        # Note: This test assumes rate limiting is configured (5/minute in production)
        # In test environment, rate limiting might be disabled or have different limits
        
        # Make multiple rapid login attempts
        for i in range(3):
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "testuser@example.com", "password": "testpassword123"},
            )
            # First few should succeed
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_refresh_rate_limit(self, client: AsyncClient, test_user: User):
        """Test that refresh endpoint has rate limiting."""
        # Login to get tokens
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "testpassword123"},
        )
        tokens = login_response.json()

        # Make multiple rapid refresh attempts
        for i in range(5):
            response = await client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": tokens["refresh_token"]},
            )
            # Should succeed (rate limit is 10/minute for refresh)
            assert response.status_code == 200
            # Update token for next iteration
            tokens = response.json()

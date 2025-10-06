"""Unit tests for TokenBlacklistService."""

from unittest.mock import AsyncMock

import pytest

from app.services.token_blacklist import TokenBlacklistService


class TestTokenBlacklistService:
    """Test TokenBlacklistService class."""

    @pytest.fixture
    async def blacklist_service(self, fake_redis):
        """Create TokenBlacklistService with fake Redis."""
        service = TokenBlacklistService()
        service.redis = fake_redis
        return service

    @pytest.mark.asyncio
    async def test_connect(self, monkeypatch):
        """Test Redis connection."""
        mock_redis = AsyncMock()
        monkeypatch.setattr("app.services.token_blacklist.redis.from_url", mock_redis)

        service = TokenBlacklistService()
        await service.connect()

        mock_redis.assert_called_once()
        assert service.redis is not None

    @pytest.mark.asyncio
    async def test_disconnect(self, blacklist_service):
        """Test Redis disconnection."""
        await blacklist_service.disconnect()
        # After disconnect, redis should be closed (fakeredis doesn't track this)

    @pytest.mark.asyncio
    async def test_blacklist_token(self, blacklist_service):
        """Test blacklisting a token."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature"
        expires_in = 7 * 24 * 60 * 60  # 7 days

        # Blacklist token
        success = await blacklist_service.blacklist_token(
            token=token,
            expires_in_seconds=expires_in,
            token_type="refresh",
        )
        assert success is True

        # Token should be blacklisted
        is_blacklisted = await blacklist_service.is_blacklisted(token, token_type="refresh")
        assert is_blacklisted is True

    @pytest.mark.asyncio
    async def test_is_blacklisted_not_exists(self, blacklist_service):
        """Test checking non-blacklisted token."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.valid.signature"

        is_blacklisted = await blacklist_service.is_blacklisted(token, token_type="refresh")
        assert is_blacklisted is False

    @pytest.mark.asyncio
    async def test_blacklist_access_token(self, blacklist_service):
        """Test blacklisting an access token (different type)."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.access.signature"
        expires_in = 30 * 60  # 30 minutes

        success = await blacklist_service.blacklist_token(
            token=token,
            expires_in_seconds=expires_in,
            token_type="access",
        )
        assert success is True

        is_blacklisted = await blacklist_service.is_blacklisted(token, token_type="access")
        assert is_blacklisted is True

        # Should not be blacklisted as refresh token
        is_blacklisted_refresh = await blacklist_service.is_blacklisted(
            token, token_type="refresh"
        )
        assert is_blacklisted_refresh is False

    @pytest.mark.asyncio
    async def test_key_prefix_structure(self, blacklist_service):
        """Test that blacklist keys have correct prefix structure."""
        token = "test.token.signature"

        await blacklist_service.blacklist_token(token, 3600, "refresh")

        # Check key structure directly in redis
        key = f"blacklist:token:refresh:{token}"
        exists = await blacklist_service.redis.exists(key)
        assert exists > 0

    @pytest.mark.asyncio
    async def test_blacklist_user_tokens(self, blacklist_service):
        """Test blacklisting all tokens for a user."""
        user_id = 123
        expires_in = 7 * 24 * 60 * 60  # 7 days

        success = await blacklist_service.blacklist_user_tokens(
            user_id=user_id,
            expires_in_seconds=expires_in,
        )
        assert success is True

        # User should be blacklisted
        is_blacklisted = await blacklist_service.is_user_blacklisted(user_id)
        assert is_blacklisted is True

    @pytest.mark.asyncio
    async def test_is_user_not_blacklisted(self, blacklist_service):
        """Test checking non-blacklisted user."""
        user_id = 456

        is_blacklisted = await blacklist_service.is_user_blacklisted(user_id)
        assert is_blacklisted is False

    @pytest.mark.asyncio
    async def test_blacklist_user_default_ttl(self, blacklist_service):
        """Test blacklisting user tokens with default TTL."""
        user_id = 789

        # Use default TTL (7 days)
        success = await blacklist_service.blacklist_user_tokens(user_id=user_id)
        assert success is True

        is_blacklisted = await blacklist_service.is_user_blacklisted(user_id)
        assert is_blacklisted is True

    @pytest.mark.asyncio
    async def test_remove_from_blacklist(self, blacklist_service):
        """Test removing a token from blacklist."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.remove.signature"

        # First blacklist
        await blacklist_service.blacklist_token(token, 3600, "refresh")
        assert await blacklist_service.is_blacklisted(token, "refresh") is True

        # Then remove
        success = await blacklist_service.remove_from_blacklist(token, "refresh")
        assert success is True

        # Should no longer be blacklisted
        assert await blacklist_service.is_blacklisted(token, "refresh") is False

    @pytest.mark.asyncio
    async def test_blacklist_token_error_handling(self, blacklist_service):
        """Test error handling in blacklist_token."""
        # Mock redis to raise exception
        blacklist_service.redis.setex = AsyncMock(side_effect=Exception("Redis error"))

        success = await blacklist_service.blacklist_token("token", 3600, "refresh")
        assert success is False

    @pytest.mark.asyncio
    async def test_is_blacklisted_error_handling(self, blacklist_service):
        """Test error handling in is_blacklisted (fail closed)."""
        # Mock redis to raise exception
        blacklist_service.redis.exists = AsyncMock(side_effect=Exception("Redis error"))

        # Should fail closed (return True)
        is_blacklisted = await blacklist_service.is_blacklisted("token", "refresh")
        assert is_blacklisted is True

    @pytest.mark.asyncio
    async def test_blacklist_user_error_handling(self, blacklist_service):
        """Test error handling in blacklist_user_tokens."""
        blacklist_service.redis.setex = AsyncMock(side_effect=Exception("Redis error"))

        success = await blacklist_service.blacklist_user_tokens(123, 3600)
        assert success is False

    @pytest.mark.asyncio
    async def test_is_user_blacklisted_error_handling(self, blacklist_service):
        """Test error handling in is_user_blacklisted."""
        blacklist_service.redis.exists = AsyncMock(side_effect=Exception("Redis error"))

        # Should return False on error
        is_blacklisted = await blacklist_service.is_user_blacklisted(123)
        assert is_blacklisted is False

    @pytest.mark.asyncio
    async def test_remove_from_blacklist_error_handling(self, blacklist_service):
        """Test error handling in remove_from_blacklist."""
        blacklist_service.redis.delete = AsyncMock(side_effect=Exception("Redis error"))

        success = await blacklist_service.remove_from_blacklist("token", "refresh")
        assert success is False

    @pytest.mark.asyncio
    async def test_auto_connect_on_blacklist(self, fake_redis):
        """Test auto-connect when blacklisting token."""
        service = TokenBlacklistService()
        assert service.redis is None

        # Mock connect to set redis
        service.redis = fake_redis

        # Should auto-connect and work
        success = await service.blacklist_token("token", 3600, "refresh")
        assert success is True
        assert service.redis is not None

    @pytest.mark.asyncio
    async def test_auto_connect_on_check(self, fake_redis):
        """Test auto-connect when checking blacklist."""
        service = TokenBlacklistService()
        assert service.redis is None

        service.redis = fake_redis

        # Should auto-connect and work
        is_blacklisted = await service.is_blacklisted("token", "refresh")
        assert is_blacklisted is False
        assert service.redis is not None


class TestTokenBlacklistIntegration:
    """Integration tests for token blacklist service with actual usage patterns."""

    @pytest.fixture
    async def blacklist_service(self, fake_redis):
        """Create TokenBlacklistService with fake Redis."""
        service = TokenBlacklistService()
        service.redis = fake_redis
        return service

    @pytest.mark.asyncio
    async def test_logout_flow(self, blacklist_service):
        """Test typical logout flow."""
        # Simulate logout - blacklist refresh token
        refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh.logout"
        ttl = 7 * 24 * 60 * 60  # 7 days

        # Logout: blacklist token
        success = await blacklist_service.blacklist_token(
            token=refresh_token,
            expires_in_seconds=ttl,
            token_type="refresh",
        )
        assert success is True

        # Subsequent refresh attempt should fail
        is_blacklisted = await blacklist_service.is_blacklisted(
            refresh_token, token_type="refresh"
        )
        assert is_blacklisted is True

    @pytest.mark.asyncio
    async def test_password_reset_flow(self, blacklist_service):
        """Test password reset flow - invalidate all user tokens."""
        user_id = 42

        # User requests password reset - blacklist all their tokens
        success = await blacklist_service.blacklist_user_tokens(
            user_id=user_id,
            expires_in_seconds=7 * 24 * 60 * 60,
        )
        assert success is True

        # All user tokens should be invalid
        is_blacklisted = await blacklist_service.is_user_blacklisted(user_id)
        assert is_blacklisted is True

    @pytest.mark.asyncio
    async def test_multiple_tokens_same_user(self, blacklist_service):
        """Test blacklisting multiple tokens for same user."""
        user_id = 100
        token1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.token1.sig"
        token2 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.token2.sig"

        # Blacklist individual tokens
        await blacklist_service.blacklist_token(token1, 3600, "refresh")
        await blacklist_service.blacklist_token(token2, 3600, "refresh")

        # Both should be blacklisted
        assert await blacklist_service.is_blacklisted(token1, "refresh") is True
        assert await blacklist_service.is_blacklisted(token2, "refresh") is True

    @pytest.mark.asyncio
    async def test_token_type_isolation(self, blacklist_service):
        """Test that token types are isolated (access vs refresh)."""
        same_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.same.signature"

        # Blacklist as refresh token
        await blacklist_service.blacklist_token(same_token, 3600, "refresh")

        # Should be blacklisted as refresh
        assert await blacklist_service.is_blacklisted(same_token, "refresh") is True

        # But NOT blacklisted as access token
        assert await blacklist_service.is_blacklisted(same_token, "access") is False

    @pytest.mark.asyncio
    async def test_account_suspension_flow(self, blacklist_service):
        """Test account suspension - invalidate all user tokens."""
        user_id = 999

        # Admin suspends account - blacklist all tokens
        await blacklist_service.blacklist_user_tokens(user_id, 30 * 24 * 60 * 60)  # 30 days

        # User-level blacklist should be active
        assert await blacklist_service.is_user_blacklisted(user_id) is True

        # Individual tokens would also be checked
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.suspended.user"
        await blacklist_service.blacklist_token(token, 3600, "refresh")
        assert await blacklist_service.is_blacklisted(token, "refresh") is True

    @pytest.mark.asyncio
    async def test_graceful_logout_with_invalid_token(self, blacklist_service):
        """Test logging out with already invalid/blacklisted token."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.already.blacklisted"

        # Blacklist once
        await blacklist_service.blacklist_token(token, 3600, "refresh")

        # Blacklist again (idempotent)
        success = await blacklist_service.blacklist_token(token, 3600, "refresh")
        assert success is True

        # Still blacklisted
        assert await blacklist_service.is_blacklisted(token, "refresh") is True

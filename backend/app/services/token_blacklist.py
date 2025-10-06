"""Token blacklist service for managing invalidated tokens."""

from typing import Optional

import redis.asyncio as redis
from app.core.config import settings


class TokenBlacklistService:
    """Service for blacklisting invalidated JWT tokens."""

    def __init__(self):
        """Initialize Redis connection for token blacklist."""
        self.redis: Optional[redis.Redis] = None
        self.key_prefix = "blacklist:token:"

    async def connect(self):
        """Establish Redis connection."""
        if not self.redis:
            self.redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )

    async def disconnect(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()

    async def blacklist_token(
        self,
        token: str,
        expires_in_seconds: int,
        token_type: str = "refresh",
    ) -> bool:
        """Add a token to the blacklist.

        Args:
            token: The JWT token to blacklist
            expires_in_seconds: Time until token expires (used as TTL)
            token_type: Type of token (access/refresh)

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            await self.connect()

        try:
            key = f"{self.key_prefix}{token_type}:{token}"
            # Store token with TTL equal to its expiration time
            # After expiration, Redis will auto-delete it
            await self.redis.setex(
                key,
                expires_in_seconds,
                "blacklisted",
            )
            return True
        except Exception as e:
            print(f"Error blacklisting token: {e}")
            return False

    async def is_blacklisted(
        self,
        token: str,
        token_type: str = "refresh",
    ) -> bool:
        """Check if a token is blacklisted.

        Args:
            token: The JWT token to check
            token_type: Type of token (access/refresh)

        Returns:
            True if blacklisted, False otherwise
        """
        if not self.redis:
            await self.connect()

        try:
            key = f"{self.key_prefix}{token_type}:{token}"
            exists = await self.redis.exists(key)
            return exists > 0
        except Exception as e:
            print(f"Error checking blacklist: {e}")
            # Fail closed - if Redis is down, consider token blacklisted
            return True

    async def blacklist_user_tokens(
        self,
        user_id: int,
        expires_in_seconds: int = 604800,  # 7 days default
    ) -> bool:
        """Blacklist all tokens for a user (e.g., on password reset).

        Args:
            user_id: User ID
            expires_in_seconds: Time to keep blacklist entry

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            await self.connect()

        try:
            key = f"{self.key_prefix}user:{user_id}"
            await self.redis.setex(key, expires_in_seconds, "all_tokens_blacklisted")
            return True
        except Exception as e:
            print(f"Error blacklisting user tokens: {e}")
            return False

    async def is_user_blacklisted(self, user_id: int) -> bool:
        """Check if all tokens for a user are blacklisted.

        Args:
            user_id: User ID

        Returns:
            True if user tokens are blacklisted, False otherwise
        """
        if not self.redis:
            await self.connect()

        try:
            key = f"{self.key_prefix}user:{user_id}"
            exists = await self.redis.exists(key)
            return exists > 0
        except Exception as e:
            print(f"Error checking user blacklist: {e}")
            return False

    async def remove_from_blacklist(
        self,
        token: str,
        token_type: str = "refresh",
    ) -> bool:
        """Remove a token from blacklist (rarely needed).

        Args:
            token: The JWT token to remove
            token_type: Type of token (access/refresh)

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            await self.connect()

        try:
            key = f"{self.key_prefix}{token_type}:{token}"
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Error removing from blacklist: {e}")
            return False


# Global token blacklist service instance
token_blacklist_service = TokenBlacklistService()

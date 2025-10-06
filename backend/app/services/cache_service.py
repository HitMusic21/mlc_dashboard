"""Redis caching service for API responses."""

import json
from typing import Any, Optional

import redis.asyncio as redis
from app.core.config import settings


class CacheService:
    """Async Redis cache service for API responses."""

    def __init__(self):
        """Initialize Redis connection pool."""
        self.redis: Optional[redis.Redis] = None

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

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.redis:
            await self.connect()

        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            # Log error but don't fail - cache miss
            print(f"Cache get error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300,  # 5 minutes default
    ) -> bool:
        """Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            await self.connect()

        try:
            serialized = json.dumps(value)
            await self.redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            # Log error but don't fail
            print(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise
        """
        if not self.redis:
            await self.connect()

        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern.

        Args:
            pattern: Key pattern (e.g., "works:*")

        Returns:
            Number of keys deleted
        """
        if not self.redis:
            await self.connect()

        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error for {pattern}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if exists, False otherwise
        """
        if not self.redis:
            await self.connect()

        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            print(f"Cache exists error for key {key}: {e}")
            return False

    async def get_ttl(self, key: str) -> int:
        """Get remaining TTL for key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds, -1 if no expiry, -2 if key doesn't exist
        """
        if not self.redis:
            await self.connect()

        try:
            return await self.redis.ttl(key)
        except Exception as e:
            print(f"Cache TTL error for key {key}: {e}")
            return -2


# Global cache service instance
cache_service = CacheService()


# Cache key generators
def generate_cache_key(prefix: str, **kwargs) -> str:
    """Generate cache key from prefix and parameters.

    Args:
        prefix: Key prefix (e.g., "works", "dashboard")
        **kwargs: Key-value pairs to include in key

    Returns:
        Cache key string
    """
    parts = [prefix]
    for key, value in sorted(kwargs.items()):
        if value is not None:
            parts.append(f"{key}:{value}")
    return ":".join(parts)


# Common cache TTL values (in seconds)
class CacheTTL:
    """Standard cache TTL values."""

    VERY_SHORT = 30  # 30 seconds - frequently changing data
    SHORT = 300  # 5 minutes - moderately changing data
    MEDIUM = 600  # 10 minutes - relatively stable data
    LONG = 1800  # 30 minutes - stable data
    VERY_LONG = 3600  # 1 hour - rarely changing data

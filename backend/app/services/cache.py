"""Redis cache service for query results and session management."""

import json
import logging
from typing import Any, Optional

from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis cache service for application data."""

    def __init__(self):
        """Initialize cache service."""
        self.client: Optional[Redis] = None
        self.default_ttl = 300  # 5 minutes

    async def connect(self):
        """Connect to Redis server."""
        try:
            self.client = Redis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True
            )
            await self.client.ping()
            logger.info("Redis connection established")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    async def disconnect(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")

    def _make_key(self, namespace: str, key: str) -> str:
        """Generate cache key with namespace.

        Args:
            namespace: Cache namespace (e.g., 'works', 'catalog', 'session')
            key: Specific key within namespace

        Returns:
            Formatted cache key
        """
        return f"{settings.PROJECT_NAME}:{namespace}:{key}"

    async def get(self, namespace: str, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            namespace: Cache namespace
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.client:
            logger.warning("Redis not available, skipping cache read")
            return None

        try:
            cache_key = self._make_key(namespace, key)
            value = await self.client.get(cache_key)

            if value:
                logger.debug(f"Cache hit: {cache_key}")
                return json.loads(value)

            logger.debug(f"Cache miss: {cache_key}")
            return None

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode cached value for {cache_key}: {e}")
            # Delete corrupted cache entry
            await self.delete(namespace, key)
            return None
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None

    async def set(
        self, namespace: str, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache.

        Args:
            namespace: Cache namespace
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (default: 300)

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.warning("Redis not available, skipping cache write")
            return False

        try:
            cache_key = self._make_key(namespace, key)
            serialized = json.dumps(value, default=str)

            ttl_seconds = ttl if ttl is not None else self.default_ttl
            await self.client.setex(cache_key, ttl_seconds, serialized)

            logger.debug(f"Cache set: {cache_key} (TTL: {ttl_seconds}s)")
            return True

        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize value for {cache_key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Cache write error: {e}")
            return False

    async def delete(self, namespace: str, key: str) -> bool:
        """Delete value from cache.

        Args:
            namespace: Cache namespace
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False

        try:
            cache_key = self._make_key(namespace, key)
            await self.client.delete(cache_key)
            logger.debug(f"Cache deleted: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def delete_pattern(self, namespace: str, pattern: str) -> int:
        """Delete all keys matching a pattern.

        Args:
            namespace: Cache namespace
            pattern: Key pattern (e.g., 'user:*')

        Returns:
            Number of keys deleted
        """
        if not self.client:
            return 0

        try:
            cache_pattern = self._make_key(namespace, pattern)
            keys = []

            async for key in self.client.scan_iter(match=cache_pattern, count=100):
                keys.append(key)

            if keys:
                deleted = await self.client.delete(*keys)
                logger.info(
                    f"Deleted {deleted} keys matching pattern: {cache_pattern}"
                )
                return deleted

            return 0

        except Exception as e:
            logger.error(f"Pattern delete error: {e}")
            return 0

    async def exists(self, namespace: str, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            namespace: Cache namespace
            key: Cache key

        Returns:
            True if exists, False otherwise
        """
        if not self.client:
            return False

        try:
            cache_key = self._make_key(namespace, key)
            return await self.client.exists(cache_key) > 0

        except Exception as e:
            logger.error(f"Cache exists check error: {e}")
            return False

    async def increment(
        self, namespace: str, key: str, amount: int = 1, ttl: Optional[int] = None
    ) -> Optional[int]:
        """Increment a numeric value in cache.

        Args:
            namespace: Cache namespace
            key: Cache key
            amount: Amount to increment by (default: 1)
            ttl: Time to live in seconds

        Returns:
            New value after increment, or None on error
        """
        if not self.client:
            return None

        try:
            cache_key = self._make_key(namespace, key)
            new_value = await self.client.incrby(cache_key, amount)

            if ttl is not None:
                await self.client.expire(cache_key, ttl)

            return new_value

        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return None

    # Convenience methods for common cache namespaces

    async def cache_query_result(
        self, query_hash: str, result: Any, ttl: int = 300
    ) -> bool:
        """Cache a query result.

        Args:
            query_hash: Hash of query parameters
            result: Query result to cache
            ttl: Time to live in seconds (default: 5 minutes)

        Returns:
            True if successful
        """
        return await self.set("query", query_hash, result, ttl)

    async def get_query_result(self, query_hash: str) -> Optional[Any]:
        """Get cached query result.

        Args:
            query_hash: Hash of query parameters

        Returns:
            Cached result or None
        """
        return await self.get("query", query_hash)

    async def cache_session(self, session_id: str, data: Any, ttl: int = 1800) -> bool:
        """Cache session data.

        Args:
            session_id: Session identifier
            data: Session data
            ttl: Time to live in seconds (default: 30 minutes)

        Returns:
            True if successful
        """
        return await self.set("session", session_id, data, ttl)

    async def get_session(self, session_id: str) -> Optional[Any]:
        """Get cached session data.

        Args:
            session_id: Session identifier

        Returns:
            Session data or None
        """
        return await self.get("session", session_id)

    async def invalidate_user_cache(self, user_id: int) -> int:
        """Invalidate all cache entries for a user.

        Args:
            user_id: User ID

        Returns:
            Number of keys deleted
        """
        return await self.delete_pattern("query", f"*user:{user_id}:*")


# Global service instance
cache_service = CacheService()

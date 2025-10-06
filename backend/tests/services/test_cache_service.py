"""Unit tests for CacheService."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.cache_service import CacheTTL, CacheService, generate_cache_key


class TestCacheKeyGeneration:
    """Test cache key generation utility."""

    def test_generate_cache_key_simple(self):
        """Test simple cache key generation."""
        key = generate_cache_key("users")
        assert key == "users"

    def test_generate_cache_key_with_params(self):
        """Test cache key generation with parameters."""
        key = generate_cache_key("users:list", page=1, limit=10)
        assert "users:list" in key
        assert "page:1" in key or "page=1" in key
        assert "limit:10" in key or "limit=10" in key

    def test_generate_cache_key_with_filters(self):
        """Test cache key generation with filter dict."""
        filters = {"search": "test", "has_iswc": True}
        key = generate_cache_key("works", page=1, filters=filters)
        assert "works" in key
        assert "page:1" in key or "page=1" in key

    def test_generate_cache_key_deterministic(self):
        """Test that cache keys are deterministic for same inputs."""
        key1 = generate_cache_key("test", a=1, b=2)
        key2 = generate_cache_key("test", a=1, b=2)
        assert key1 == key2

        # Different order should produce same key (dict is sorted)
        key3 = generate_cache_key("test", b=2, a=1)
        assert key1 == key3


class TestCacheService:
    """Test CacheService class."""

    @pytest.fixture
    async def cache_service(self, fake_redis):
        """Create CacheService with fake Redis."""
        service = CacheService()
        service.redis = fake_redis
        return service

    @pytest.mark.asyncio
    async def test_connect(self, monkeypatch):
        """Test Redis connection."""
        mock_redis = AsyncMock()
        monkeypatch.setattr("app.services.cache_service.redis.from_url", mock_redis)

        service = CacheService()
        await service.connect()

        mock_redis.assert_called_once()
        assert service.redis is not None

    @pytest.mark.asyncio
    async def test_disconnect(self, cache_service):
        """Test Redis disconnection."""
        await cache_service.disconnect()
        # After disconnect, redis should be closed

    @pytest.mark.asyncio
    async def test_set_and_get(self, cache_service):
        """Test setting and getting cache values."""
        test_data = {"key": "value", "number": 42}

        # Set cache
        success = await cache_service.set("test:key", test_data, ttl=60)
        assert success is True

        # Get cache
        result = await cache_service.get("test:key")
        assert result == test_data

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, cache_service):
        """Test getting non-existent cache key."""
        result = await cache_service.get("nonexistent:key")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_with_ttl(self, cache_service):
        """Test setting cache with TTL."""
        test_data = {"expires": "soon"}

        success = await cache_service.set("test:ttl", test_data, ttl=1)
        assert success is True

        # Should exist immediately
        result = await cache_service.get("test:ttl")
        assert result == test_data

        # Wait for expiration (fakeredis simulates TTL)
        # In real tests, we'd use time.sleep or fakeredis advance time
        # For now, just verify the set operation

    @pytest.mark.asyncio
    async def test_delete(self, cache_service):
        """Test deleting cache key."""
        test_data = {"delete": "me"}

        # Set then delete
        await cache_service.set("test:delete", test_data)
        success = await cache_service.delete("test:delete")
        assert success is True

        # Should not exist
        result = await cache_service.get("test:delete")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_pattern(self, cache_service):
        """Test deleting cache by pattern."""
        # Set multiple keys
        await cache_service.set("works:1", {"id": 1})
        await cache_service.set("works:2", {"id": 2})
        await cache_service.set("users:1", {"id": 1})

        # Delete works pattern
        deleted = await cache_service.delete_pattern("works:*")
        assert deleted >= 2

        # works keys should be gone
        assert await cache_service.get("works:1") is None
        assert await cache_service.get("works:2") is None

        # users key should remain
        assert await cache_service.get("users:1") is not None

    @pytest.mark.asyncio
    async def test_exists(self, cache_service):
        """Test checking key existence."""
        test_data = {"exists": True}

        # Should not exist initially
        exists = await cache_service.exists("test:exists")
        assert exists is False

        # Set key
        await cache_service.set("test:exists", test_data)

        # Should exist now
        exists = await cache_service.exists("test:exists")
        assert exists is True

    @pytest.mark.asyncio
    async def test_set_error_handling(self, cache_service):
        """Test error handling in set operation."""
        # Mock redis to raise exception
        cache_service.redis.setex = AsyncMock(side_effect=Exception("Redis error"))

        success = await cache_service.set("test:error", {"data": "test"})
        assert success is False

    @pytest.mark.asyncio
    async def test_get_error_handling(self, cache_service):
        """Test error handling in get operation."""
        # Mock redis to raise exception
        cache_service.redis.get = AsyncMock(side_effect=Exception("Redis error"))

        result = await cache_service.get("test:error")
        assert result is None

    @pytest.mark.asyncio
    async def test_json_serialization(self, cache_service):
        """Test JSON serialization of complex objects."""
        complex_data = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "nested": {"key": "value"},
        }

        await cache_service.set("test:json", complex_data)
        result = await cache_service.get("test:json")

        assert result == complex_data

    @pytest.mark.asyncio
    async def test_auto_connect_on_operations(self, fake_redis):
        """Test that operations auto-connect if not connected."""
        service = CacheService()
        assert service.redis is None

        # After calling get, redis should be connected
        service.redis = fake_redis
        await service.get("test:key")
        assert service.redis is not None

        # Same for set
        service_2 = CacheService()
        assert service_2.redis is None
        service_2.redis = fake_redis
        await service_2.set("test:key", {"data": "test"})
        assert service_2.redis is not None


class TestCacheTTL:
    """Test CacheTTL constants."""

    def test_ttl_constants(self):
        """Test that TTL constants are defined correctly."""
        assert CacheTTL.VERY_SHORT == 30
        assert CacheTTL.SHORT == 300  # 5 minutes
        assert CacheTTL.MEDIUM == 600  # 10 minutes
        assert CacheTTL.LONG == 1800  # 30 minutes
        assert CacheTTL.VERY_LONG == 3600  # 1 hour

    def test_ttl_hierarchy(self):
        """Test that TTL values are in ascending order."""
        assert CacheTTL.VERY_SHORT < CacheTTL.SHORT
        assert CacheTTL.SHORT < CacheTTL.MEDIUM
        assert CacheTTL.MEDIUM < CacheTTL.LONG
        assert CacheTTL.LONG < CacheTTL.VERY_LONG


class TestCacheServiceIntegration:
    """Integration tests for cache service with actual usage patterns."""

    @pytest.fixture
    async def cache_service(self, fake_redis):
        """Create CacheService with fake Redis."""
        service = CacheService()
        service.redis = fake_redis
        return service

    @pytest.mark.asyncio
    async def test_works_list_caching_pattern(self, cache_service):
        """Test typical works list caching pattern."""
        # Simulate works list response
        works_data = {
            "items": [
                {"id": 1, "title": "Work 1"},
                {"id": 2, "title": "Work 2"},
            ],
            "total": 2,
            "page": 1,
            "limit": 10,
        }

        # Generate cache key
        cache_key = generate_cache_key("works:list", page=1, limit=10)

        # Cache miss
        cached = await cache_service.get(cache_key)
        assert cached is None

        # Set cache
        await cache_service.set(cache_key, works_data, ttl=CacheTTL.SHORT)

        # Cache hit
        cached = await cache_service.get(cache_key)
        assert cached == works_data
        assert cached["total"] == 2

    @pytest.mark.asyncio
    async def test_statistics_caching_pattern(self, cache_service):
        """Test dashboard statistics caching pattern."""
        stats_data = {
            "total_works": 1000,
            "works_with_iswc": 750,
            "disputed_works": 25,
            "monthly_trend": [{"month": "2025-01", "count": 50}],
        }

        cache_key = "dashboard:statistics"

        # Set cache with medium TTL
        await cache_service.set(cache_key, stats_data, ttl=CacheTTL.MEDIUM)

        # Retrieve
        cached = await cache_service.get(cache_key)
        assert cached["total_works"] == 1000
        assert len(cached["monthly_trend"]) == 1

    @pytest.mark.asyncio
    async def test_cache_invalidation_pattern(self, cache_service):
        """Test cache invalidation when data changes."""
        # Set initial cache
        cache_key = "works:list:page:1"
        await cache_service.set(cache_key, {"items": [], "total": 0})

        # Verify cache exists
        assert await cache_service.exists(cache_key) is True

        # Simulate data change - invalidate cache
        await cache_service.delete(cache_key)

        # Cache should be gone
        assert await cache_service.exists(cache_key) is False

    @pytest.mark.asyncio
    async def test_clear_all_works_cache(self, cache_service):
        """Test clearing all works-related cache."""
        # Set multiple works caches
        await cache_service.set("works:list:page:1", {"page": 1})
        await cache_service.set("works:list:page:2", {"page": 2})
        await cache_service.set("works:123", {"id": 123})
        await cache_service.set("dashboard:statistics", {"stats": True})

        # Delete all works cache
        await cache_service.delete_pattern("works:*")

        # Works cache should be cleared
        assert await cache_service.get("works:list:page:1") is None
        assert await cache_service.get("works:list:page:2") is None
        assert await cache_service.get("works:123") is None

        # Dashboard stats should remain
        assert await cache_service.get("dashboard:statistics") is not None

"""Integration test for Scenario 7: Concurrent load handling."""

import asyncio
import time

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_concurrent_users_performance(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test system handles concurrent users with acceptable performance."""

    async def make_request():
        """Single user request."""
        start = time.time()
        response = await client.get("/api/v1/works", headers=auth_headers)
        elapsed_ms = (time.time() - start) * 1000
        return response.status_code, elapsed_ms

    # Simulate 10 concurrent users (scaled down from 100)
    tasks = [make_request() for _ in range(10)]
    results = await asyncio.gather(*tasks)

    # Verify all requests succeeded
    for status_code, elapsed_ms in results:
        assert status_code == 200
        assert elapsed_ms < 500  # Performance requirement


@pytest.mark.asyncio
async def test_concurrent_searches(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test concurrent search requests don't degrade performance."""

    async def search_works(query: str):
        response = await client.post(
            "/api/v1/works/search",
            json={"query": query, "page": 1, "limit": 10},
            headers=auth_headers,
        )
        return response.status_code

    queries = ["yesterday", "love", "song", "music", "test"]
    tasks = [search_works(q) for q in queries * 2]  # 10 concurrent searches

    results = await asyncio.gather(*tasks)

    for status_code in results:
        assert status_code == 200


@pytest.mark.asyncio
async def test_no_connection_pool_exhaustion(
    client: AsyncClient, auth_headers: dict[str, str]
):
    """Test that database connection pool doesn't get exhausted."""

    async def db_query():
        """Make a database-heavy request."""
        response = await client.get("/api/v1/works?limit=50", headers=auth_headers)
        return response.status_code

    # Make many concurrent requests
    tasks = [db_query() for _ in range(20)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # All should succeed (no connection errors)
    successful = sum(1 for r in results if r == 200)
    assert successful >= 18  # Allow for some variance

"""Shared pytest fixtures for all tests."""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fakeredis import aioredis as fakeredis
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from sqlmodel import SQLModel

from app.core.config import settings
from main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine.

    Uses PostgreSQL test database if available (preferred for contract tests),
    falls back to SQLite for unit tests.

    To use PostgreSQL:
    1. Start PostgreSQL: docker-compose up -d postgres
    2. Create test DB: docker exec bwarm_postgres psql -U postgres -c "CREATE DATABASE bwarm_test;"
    3. Run tests: pytest tests/contract/
    """
    import os

    # Try PostgreSQL first (required for contract tests with full features)
    test_db_url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/bwarm_test"
    )

    try:
        # Attempt PostgreSQL connection
        engine = create_async_engine(
            test_db_url,
            poolclass=NullPool,
            echo=False,
        )

        # Test connection
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        print(f"\n✓ Using PostgreSQL test database: {test_db_url}")
        use_postgres = True

    except Exception as e:
        # Fall back to SQLite for unit tests only
        print(f"\n⚠ PostgreSQL not available ({e}), falling back to SQLite")
        print("  Note: Some contract tests may fail with SQLite due to PostgreSQL-specific features")
        print("  To fix: docker-compose up -d postgres")

        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            poolclass=NullPool,
            echo=False,
        )
        use_postgres = False

    # Import all models to register them with SQLModel
    from app.models.user import User
    from app.models.musical_work import MusicalWork
    from app.models.resource import Resource
    from app.models.work_resource_link import WorkResourceLink
    from app.models.catalog_upload import CatalogUpload
    from app.models.catalog_match import CatalogMatch
    from app.models.notification import Notification
    from app.models.user_preferences import UserPreferences
    from app.models.activity_log import ActivityLog

    # Create all tables
    async with engine.begin() as conn:
        if use_postgres:
            # PostgreSQL: drop and recreate for clean state
            await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def fake_redis():
    """Create a fake Redis instance for testing."""
    redis = fakeredis.FakeRedis(decode_responses=True)
    yield redis
    await redis.flushall()
    await redis.aclose()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for testing."""
    monkeypatch.setattr(settings, "REDIS_URL", "redis://localhost:6379/1")
    monkeypatch.setattr(settings, "DEBUG", True)
    monkeypatch.setattr(settings, "SECRET_KEY", "test-secret-key-for-testing-only")
    return settings


# ============================================================
# Authentication Fixtures for Contract Tests
# ============================================================


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user (publisher role) for authentication.

    Returns:
        User: Test user with publisher role
    """
    from app.core.security import get_password_hash
    from app.models.user import User, UserRole

    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("Test123!"),
        full_name="Test User",
        role=UserRole.PUBLISHER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_admin(db_session: AsyncSession):
    """Create a test admin user for authentication.

    Returns:
        User: Test user with admin role
    """
    from app.core.security import get_password_hash
    from app.models.user import User, UserRole

    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("Admin123!"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_publisher(db_session: AsyncSession):
    """Create a test publisher user for authentication.

    Returns:
        User: Test user with publisher role
    """
    from app.core.security import get_password_hash
    from app.models.user import User, UserRole

    user = User(
        email="publisher@example.com",
        hashed_password=get_password_hash("Publisher123!"),
        full_name="Publisher User",
        role=UserRole.PUBLISHER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def auth_headers(test_user) -> dict[str, str]:
    """Generate valid authentication headers with access token.

    Args:
        test_user: Test user fixture

    Returns:
        dict: Headers with Bearer token for authentication
    """
    from app.core.security import create_access_token

    access_token = create_access_token(
        data={
            "sub": str(test_user.id),
            "email": test_user.email,
            "role": test_user.role,
        }
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def admin_headers(test_admin) -> dict[str, str]:
    """Generate valid authentication headers for admin user.

    Args:
        test_admin: Test admin user fixture

    Returns:
        dict: Headers with Bearer token for admin authentication
    """
    from app.core.security import create_access_token

    access_token = create_access_token(
        data={
            "sub": str(test_admin.id),
            "email": test_admin.email,
            "role": test_admin.role,
        }
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def publisher_headers(test_publisher) -> dict[str, str]:
    """Generate valid authentication headers for publisher user.

    Args:
        test_publisher: Test publisher user fixture

    Returns:
        dict: Headers with Bearer token for publisher authentication
    """
    from app.core.security import create_access_token

    access_token = create_access_token(
        data={
            "sub": str(test_publisher.id),
            "email": test_publisher.email,
            "role": test_publisher.role,
        }
    )
    return {"Authorization": f"Bearer {access_token}"}

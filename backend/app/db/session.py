"""Database session management for BWARM Dashboard."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from app.core.config import settings

# Create async engine with connection pooling
# SQLite uses different parameters than PostgreSQL
is_sqlite = "sqlite" in settings.DATABASE_URL

engine_kwargs = {
    "url": settings.DATABASE_URL,
    "echo": settings.DEBUG,
    "future": True,
}

# Add PostgreSQL-specific pooling parameters
if not is_sqlite:
    engine_kwargs["pool_pre_ping"] = True  # Verify connections before using them
    engine_kwargs["pool_size"] = 10  # Number of connections to maintain
    engine_kwargs["max_overflow"] = 20  # Additional connections to create if pool is exhausted
else:
    engine_kwargs["poolclass"] = NullPool  # SQLite doesn't support connection pooling

engine = create_async_engine(**engine_kwargs)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session.

    Yields:
        AsyncSession: Database session

    Example:
        ```python
        @app.get("/users")
        async def get_users(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(User))
            return result.scalars().all()
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database by creating all tables.

    Note: In production, use Alembic migrations instead.
    This is primarily for development and testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """Close database connection pool."""
    await engine.dispose()

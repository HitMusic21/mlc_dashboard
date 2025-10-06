"""Database initialization and seeding for BWARM Dashboard."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


async def create_initial_admin(session: AsyncSession) -> None:
    """Create initial admin user if it doesn't exist.

    Args:
        session: Database session
    """
    # Check if admin exists
    result = await session.execute(
        select(User).where(User.email == "admin@example.com", User.role == UserRole.ADMIN)
    )
    admin_user = result.scalar_one_or_none()

    if admin_user is None:
        # Create admin user
        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),  # Change in production!
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        logger.info("Created initial admin user: admin@example.com")
    else:
        logger.info("Admin user already exists")


async def create_test_publisher(session: AsyncSession) -> None:
    """Create test publisher user if it doesn't exist (development only).

    Args:
        session: Database session
    """
    # Check if publisher exists
    result = await session.execute(
        select(User).where(
            User.email == "publisher@example.com", User.role == UserRole.PUBLISHER
        )
    )
    publisher_user = result.scalar_one_or_none()

    if publisher_user is None:
        # Create publisher user
        publisher = User(
            email="publisher@example.com",
            hashed_password=get_password_hash("SecurePass123!"),
            full_name="Test Publisher",
            role=UserRole.PUBLISHER,
            is_active=True,
        )
        session.add(publisher)
        await session.commit()
        logger.info("Created test publisher user: publisher@example.com")
    else:
        logger.info("Publisher user already exists")


async def init_db_data(session: AsyncSession) -> None:
    """Initialize database with seed data.

    Args:
        session: Database session
    """
    logger.info("Initializing database with seed data...")

    # Create initial admin
    await create_initial_admin(session)

    # Create test publisher (development only)
    from app.core.config import settings

    if settings.DEBUG:
        await create_test_publisher(session)

    logger.info("Database initialization complete")


async def check_db_connection(session: AsyncSession) -> bool:
    """Check database connectivity.

    Args:
        session: Database session

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        # Simple query to test connection
        await session.execute(select(1))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False

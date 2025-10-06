"""CRUD operations for User entities."""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User, UserRole


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """Get user by email address.

    Args:
        session: Database session
        email: User email

    Returns:
        User object or None if not found
    """
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        User object or None if not found
    """
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, user_data: Dict) -> User:
    """Create a new user.

    Args:
        session: Database session
        user_data: User data (email, password, full_name, role)

    Returns:
        Created User object
    """
    # Hash password before storing
    hashed_password = get_password_hash(user_data["password"])

    user = User(
        email=user_data["email"],
        hashed_password=hashed_password,
        full_name=user_data["full_name"],
        role=user_data.get("role", UserRole.PUBLISHER),
        is_active=user_data.get("is_active", True),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


async def update_last_login(session: AsyncSession, user_id: int) -> Optional[User]:
    """Update user's last login timestamp.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        Updated User object or None if not found
    """
    user = await get_user_by_id(session, user_id)
    if not user:
        return None

    user.last_login_at = datetime.utcnow()
    await session.commit()
    await session.refresh(user)

    return user


async def update_user(
    session: AsyncSession, user_id: int, update_data: Dict
) -> Optional[User]:
    """Update user information.

    Args:
        session: Database session
        user_id: User ID
        update_data: Fields to update

    Returns:
        Updated User object or None if not found
    """
    user = await get_user_by_id(session, user_id)
    if not user:
        return None

    # Update allowed fields
    for key, value in update_data.items():
        if key == "password":
            user.hashed_password = get_password_hash(value)
        elif hasattr(user, key) and key not in ["id", "hashed_password"]:
            setattr(user, key, value)

    await session.commit()
    await session.refresh(user)

    return user


async def deactivate_user(session: AsyncSession, user_id: int) -> Optional[User]:
    """Deactivate a user (soft delete).

    Args:
        session: Database session
        user_id: User ID

    Returns:
        Updated User object or None if not found
    """
    user = await get_user_by_id(session, user_id)
    if not user:
        return None

    user.is_active = False
    await session.commit()
    await session.refresh(user)

    return user


async def get_all_users(
    session: AsyncSession,
    filters: Optional[Dict] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[User]:
    """Get all users with optional filtering.

    Args:
        session: Database session
        filters: Optional filters (role, is_active)
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of User objects
    """
    query = select(User)

    # Apply filters
    if filters:
        if "role" in filters:
            query = query.where(User.role == filters["role"])
        if "is_active" in filters:
            query = query.where(User.is_active == filters["is_active"])

    # Apply pagination
    query = query.order_by(User.created_at.desc())
    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_users_count(
    session: AsyncSession, filters: Optional[Dict] = None
) -> int:
    """Get count of users with optional filtering.

    Args:
        session: Database session
        filters: Optional filters (role, is_active)

    Returns:
        Count of users
    """
    from sqlalchemy import func

    query = select(func.count()).select_from(User)

    # Apply filters
    if filters:
        if "role" in filters:
            query = query.where(User.role == filters["role"])
        if "is_active" in filters:
            query = query.where(User.is_active == filters["is_active"])

    result = await session.execute(query)
    return result.scalar() or 0

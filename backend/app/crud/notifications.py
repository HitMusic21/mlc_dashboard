"""CRUD operations for Notification entities."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationSeverity, NotificationType


async def create_notification(
    session: AsyncSession, notification_data: dict
) -> Notification:
    """Create a new notification.

    Args:
        session: Database session
        notification_data: Notification data (user_id, type, severity, title, message, etc.)

    Returns:
        Created Notification object
    """
    notification = Notification(**notification_data)
    session.add(notification)
    await session.commit()
    await session.refresh(notification)

    return notification


async def get_notification_by_id(
    session: AsyncSession, notification_id: UUID, user_id: int
) -> Optional[Notification]:
    """Get a notification by ID for a specific user.

    Args:
        session: Database session
        notification_id: Notification ID
        user_id: User ID (for authorization)

    Returns:
        Notification object or None if not found or doesn't belong to user
    """
    query = select(Notification).where(
        Notification.id == notification_id, Notification.user_id == user_id
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_notifications(
    session: AsyncSession,
    user_id: int,
    is_read: Optional[bool] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[Notification]:
    """Get notifications for a user with optional filtering and pagination.

    Args:
        session: Database session
        user_id: User ID
        is_read: Optional filter by read status
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of Notification objects
    """
    query = select(Notification).where(Notification.user_id == user_id)

    # Apply read status filter
    if is_read is not None:
        query = query.where(Notification.is_read == is_read)

    # Order by created_at descending (newest first)
    query = query.order_by(Notification.created_at.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_notifications_count(
    session: AsyncSession, user_id: int, is_read: Optional[bool] = None
) -> int:
    """Get count of notifications for a user with optional filtering.

    Args:
        session: Database session
        user_id: User ID
        is_read: Optional filter by read status

    Returns:
        Count of notifications
    """
    query = select(func.count()).select_from(Notification).where(Notification.user_id == user_id)

    if is_read is not None:
        query = query.where(Notification.is_read == is_read)

    result = await session.execute(query)
    return result.scalar() or 0


async def get_unread_count(session: AsyncSession, user_id: int) -> int:
    """Get count of unread notifications for a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        Count of unread notifications
    """
    return await get_notifications_count(session, user_id, is_read=False)


async def mark_notification_as_read(
    session: AsyncSession, notification_id: UUID, user_id: int
) -> Optional[Notification]:
    """Mark a notification as read.

    Args:
        session: Database session
        notification_id: Notification ID
        user_id: User ID (for authorization)

    Returns:
        Updated Notification object or None if not found
    """
    notification = await get_notification_by_id(session, notification_id, user_id)

    if not notification:
        return None

    notification.mark_as_read()

    await session.commit()
    await session.refresh(notification)

    return notification


async def mark_all_notifications_as_read(session: AsyncSession, user_id: int) -> int:
    """Mark all unread notifications as read for a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        Number of notifications updated
    """
    stmt = (
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)
        .values(is_read=True, read_at=datetime.utcnow())
    )

    result = await session.execute(stmt)
    await session.commit()

    return result.rowcount or 0


async def delete_notification(
    session: AsyncSession, notification_id: UUID, user_id: int
) -> bool:
    """Delete a notification.

    Args:
        session: Database session
        notification_id: Notification ID
        user_id: User ID (for authorization)

    Returns:
        True if deleted, False if not found
    """
    stmt = delete(Notification).where(
        Notification.id == notification_id, Notification.user_id == user_id
    )

    result = await session.execute(stmt)
    await session.commit()

    return (result.rowcount or 0) > 0


async def clear_read_notifications(session: AsyncSession, user_id: int) -> int:
    """Delete all read notifications for a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        Number of notifications deleted
    """
    stmt = delete(Notification).where(
        Notification.user_id == user_id, Notification.is_read == True
    )

    result = await session.execute(stmt)
    await session.commit()

    return result.rowcount or 0

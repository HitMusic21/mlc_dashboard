"""User notifications API routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.crud import notifications as notifications_crud
from app.db.session import get_session
from app.models.user import User
from app.schemas.notifications import (
    ClearReadResponse,
    MarkAllReadResponse,
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Get paginated list of user's notifications.

    Optionally filter by read status and supports pagination.

    Args:
        is_read: Optional filter by read status
        page: Page number (1-indexed)
        limit: Items per page (max 100)
        current_user: Authenticated user
        session: Database session

    Returns:
        NotificationListResponse with notifications and pagination metadata
    """
    skip = (page - 1) * limit

    # Get notifications
    notifications = await notifications_crud.get_notifications(
        session, current_user.id, is_read=is_read, skip=skip, limit=limit
    )

    # Get total count
    total = await notifications_crud.get_notifications_count(
        session, current_user.id, is_read=is_read
    )

    has_more = (skip + len(notifications)) < total

    return NotificationListResponse(
        notifications=notifications,
        total=total,
        page=page,
        limit=limit,
        has_more=has_more,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Get count of unread notifications for current user.

    Args:
        current_user: Authenticated user
        session: Database session

    Returns:
        UnreadCountResponse with count
    """
    count = await notifications_crud.get_unread_count(session, current_user.id)
    return UnreadCountResponse(count=count)


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Mark a specific notification as read.

    Args:
        notification_id: Notification ID
        current_user: Authenticated user
        session: Database session

    Returns:
        Updated NotificationResponse

    Raises:
        HTTPException: 404 if notification not found or doesn't belong to user
    """
    notification = await notifications_crud.mark_notification_as_read(
        session, notification_id, current_user.id
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return notification


@router.put("/read-all", response_model=MarkAllReadResponse)
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Mark all unread notifications as read for current user.

    Args:
        current_user: Authenticated user
        session: Database session

    Returns:
        MarkAllReadResponse with count of updated notifications
    """
    updated_count = await notifications_crud.mark_all_notifications_as_read(
        session, current_user.id
    )

    return MarkAllReadResponse(updated_count=updated_count)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Delete a specific notification.

    Args:
        notification_id: Notification ID
        current_user: Authenticated user
        session: Database session

    Raises:
        HTTPException: 404 if notification not found or doesn't belong to user
    """
    deleted = await notifications_crud.delete_notification(
        session, notification_id, current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )


@router.delete("/clear-read", response_model=ClearReadResponse)
async def clear_read_notifications(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Delete all read notifications for current user.

    Args:
        current_user: Authenticated user
        session: Database session

    Returns:
        ClearReadResponse with count of deleted notifications
    """
    deleted_count = await notifications_crud.clear_read_notifications(
        session, current_user.id
    )

    return ClearReadResponse(deleted_count=deleted_count)

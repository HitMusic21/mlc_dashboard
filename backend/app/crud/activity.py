"""CRUD operations for ActivityLog entities."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityLog, ActivityStatus


async def log_activity(session: AsyncSession, activity_data: dict) -> ActivityLog:
    """Log a new activity.

    Args:
        session: Database session
        activity_data: Activity data (user_id, action, entity_type, entity_id, description, etc.)

    Returns:
        Created ActivityLog object
    """
    # Validate action format if provided
    if "action" in activity_data:
        action = activity_data["action"]
        if "." not in action or len(action.split(".")) != 2:
            raise ValueError("Action must follow format: {entity}.{verb}")

    activity = ActivityLog(**activity_data)
    session.add(activity)
    await session.commit()
    await session.refresh(activity)

    return activity


async def get_recent_activity(
    session: AsyncSession,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    days: int = 7,
    skip: int = 0,
    limit: int = 50,
) -> List[ActivityLog]:
    """Get recent activity logs with optional filtering.

    Args:
        session: Database session
        user_id: Optional filter by user
        entity_type: Optional filter by entity type
        entity_id: Optional filter by entity ID
        days: Number of days to look back (default 7)
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of ActivityLog objects
    """
    query = select(ActivityLog)

    # Time filter
    since = datetime.utcnow() - timedelta(days=days)
    query = query.where(ActivityLog.created_at >= since)

    # Apply optional filters
    if user_id is not None:
        query = query.where(ActivityLog.user_id == user_id)

    if entity_type is not None:
        query = query.where(ActivityLog.entity_type == entity_type)

    if entity_id is not None:
        query = query.where(ActivityLog.entity_id == entity_id)

    # Order by created_at descending (newest first)
    query = query.order_by(ActivityLog.created_at.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_activity_by_entity(
    session: AsyncSession,
    entity_type: str,
    entity_id: UUID,
    skip: int = 0,
    limit: int = 20,
) -> List[ActivityLog]:
    """Get activity logs for a specific entity (audit trail).

    Args:
        session: Database session
        entity_type: Entity type (e.g., 'catalog', 'work')
        entity_id: Entity ID
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of ActivityLog objects ordered by time descending
    """
    query = (
        select(ActivityLog)
        .where(ActivityLog.entity_type == entity_type, ActivityLog.entity_id == entity_id)
        .order_by(ActivityLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_activity_stats(
    session: AsyncSession, user_id: Optional[int] = None, days: int = 30
) -> Dict:
    """Get activity statistics for analytics dashboard.

    Args:
        session: Database session
        user_id: Optional filter by user
        days: Number of days to analyze (default 30)

    Returns:
        Dictionary with statistics:
        - total_actions: Total number of activities
        - by_action: Count grouped by action type
        - by_status: Count grouped by status
        - by_entity: Count grouped by entity type
    """
    since = datetime.utcnow() - timedelta(days=days)

    # Base query for time range
    base_query = select(ActivityLog).where(ActivityLog.created_at >= since)

    if user_id is not None:
        base_query = base_query.where(ActivityLog.user_id == user_id)

    # Total actions count
    total_query = select(func.count()).select_from(ActivityLog).where(ActivityLog.created_at >= since)
    if user_id is not None:
        total_query = total_query.where(ActivityLog.user_id == user_id)

    total_result = await session.execute(total_query)
    total_actions = total_result.scalar() or 0

    # Group by action
    action_query = (
        select(ActivityLog.action, func.count().label("count"))
        .where(ActivityLog.created_at >= since)
        .group_by(ActivityLog.action)
        .order_by(func.count().desc())
    )
    if user_id is not None:
        action_query = action_query.where(ActivityLog.user_id == user_id)

    action_result = await session.execute(action_query)
    by_action = {row.action: row.count for row in action_result.all()}

    # Group by status
    status_query = (
        select(ActivityLog.status, func.count().label("count"))
        .where(ActivityLog.created_at >= since)
        .group_by(ActivityLog.status)
    )
    if user_id is not None:
        status_query = status_query.where(ActivityLog.user_id == user_id)

    status_result = await session.execute(status_query)
    by_status = {row.status.value: row.count for row in status_result.all()}

    # Group by entity type (filter out None values)
    entity_query = (
        select(ActivityLog.entity_type, func.count().label("count"))
        .where(ActivityLog.created_at >= since, ActivityLog.entity_type.isnot(None))
        .group_by(ActivityLog.entity_type)
        .order_by(func.count().desc())
    )
    if user_id is not None:
        entity_query = entity_query.where(ActivityLog.user_id == user_id)

    entity_result = await session.execute(entity_query)
    by_entity = {row.entity_type: row.count for row in entity_result.all()}

    return {
        "total_actions": total_actions,
        "by_action": by_action,
        "by_status": by_status,
        "by_entity": by_entity,
        "period_days": days,
    }

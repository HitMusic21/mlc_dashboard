"""Unit tests for activity log CRUD operations."""

import pytest
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.activity import (
    log_activity,
    get_recent_activity,
    get_activity_by_entity,
    get_activity_stats,
)
from app.models.activity_log import ActivityLog, ActivityStatus


@pytest.fixture
def mock_session():
    """Create a mock AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_activity():
    """Create a sample ActivityLog."""
    activity = MagicMock(spec=ActivityLog)
    activity.id = uuid4()
    activity.user_id = 1
    activity.action = "work.create"
    activity.entity_type = "work"
    activity.entity_id = uuid4()
    activity.description = "Created musical work"
    activity.status = ActivityStatus.SUCCESS
    activity.ip_address = "192.168.1.1"
    activity.user_agent = "Mozilla/5.0"
    activity.created_at = datetime.utcnow()
    return activity


@pytest.fixture
def sample_activities():
    """Create a list of sample activities."""
    activities = []
    now = datetime.utcnow()

    # Activity 1 - Work creation (today)
    activity1 = MagicMock(spec=ActivityLog)
    activity1.id = uuid4()
    activity1.user_id = 1
    activity1.action = "work.create"
    activity1.entity_type = "work"
    activity1.entity_id = uuid4()
    activity1.status = ActivityStatus.SUCCESS
    activity1.created_at = now
    activities.append(activity1)

    # Activity 2 - Work update (yesterday)
    activity2 = MagicMock(spec=ActivityLog)
    activity2.id = uuid4()
    activity2.user_id = 1
    activity2.action = "work.update"
    activity2.entity_type = "work"
    activity2.entity_id = activity1.entity_id
    activity2.status = ActivityStatus.SUCCESS
    activity2.created_at = now - timedelta(days=1)
    activities.append(activity2)

    # Activity 3 - Catalog upload (2 days ago)
    activity3 = MagicMock(spec=ActivityLog)
    activity3.id = uuid4()
    activity3.user_id = 2
    activity3.action = "catalog.upload"
    activity3.entity_type = "catalog"
    activity3.entity_id = uuid4()
    activity3.status = ActivityStatus.SUCCESS
    activity3.created_at = now - timedelta(days=2)
    activities.append(activity3)

    # Activity 4 - Failed action (3 days ago)
    activity4 = MagicMock(spec=ActivityLog)
    activity4.id = uuid4()
    activity4.user_id = 1
    activity4.action = "work.delete"
    activity4.entity_type = "work"
    activity4.entity_id = uuid4()
    activity4.status = ActivityStatus.FAILURE
    activity4.created_at = now - timedelta(days=3)
    activities.append(activity4)

    return activities


@pytest.fixture
def activity_data():
    """Sample activity creation data."""
    return {
        "user_id": 1,
        "action": "work.create",
        "entity_type": "work",
        "entity_id": uuid4(),
        "description": "Created a new musical work",
        "status": ActivityStatus.SUCCESS,
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0",
    }


class TestLogActivity:
    """Test log_activity function."""

    @pytest.mark.asyncio
    async def test_log_activity_success(self, mock_session, activity_data):
        """Test logging activity successfully."""
        created_activity = MagicMock(spec=ActivityLog)
        for key, value in activity_data.items():
            setattr(created_activity, key, value)

        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("app.crud.activity.ActivityLog", return_value=created_activity):
            activity = await log_activity(mock_session, activity_data)

            assert activity.action == "work.create"
            assert activity.user_id == 1
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_log_activity_invalid_action_format(self, mock_session):
        """Test that invalid action format raises error."""
        invalid_data = {
            "user_id": 1,
            "action": "invalid_action",  # Missing dot separator
            "entity_type": "work",
        }

        with pytest.raises(ValueError, match="Action must follow format"):
            await log_activity(mock_session, invalid_data)

    @pytest.mark.asyncio
    async def test_log_activity_action_with_multiple_dots(self, mock_session):
        """Test that action with too many dots raises error."""
        invalid_data = {
            "user_id": 1,
            "action": "work.create.extra",  # Too many dots
            "entity_type": "work",
        }

        with pytest.raises(ValueError, match="Action must follow format"):
            await log_activity(mock_session, invalid_data)


class TestGetRecentActivity:
    """Test get_recent_activity function."""

    @pytest.mark.asyncio
    async def test_get_recent_activity_no_filters(self, mock_session, sample_activities):
        """Test getting recent activity without filters."""
        # Mock should return activities from last 7 days
        recent = [a for a in sample_activities if (datetime.utcnow() - a.created_at).days <= 7]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = recent
        mock_session.execute.return_value = mock_result

        activities = await get_recent_activity(mock_session)

        assert len(activities) == 4
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_recent_activity_with_user_filter(self, mock_session, sample_activities):
        """Test filtering by user_id."""
        user_activities = [a for a in sample_activities if a.user_id == 1]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = user_activities
        mock_session.execute.return_value = mock_result

        activities = await get_recent_activity(mock_session, user_id=1)

        assert len(activities) == 3
        assert all(a.user_id == 1 for a in activities)

    @pytest.mark.asyncio
    async def test_get_recent_activity_with_entity_type_filter(self, mock_session, sample_activities):
        """Test filtering by entity_type."""
        work_activities = [a for a in sample_activities if a.entity_type == "work"]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = work_activities
        mock_session.execute.return_value = mock_result

        activities = await get_recent_activity(mock_session, entity_type="work")

        assert len(activities) == 3
        assert all(a.entity_type == "work" for a in activities)

    @pytest.mark.asyncio
    async def test_get_recent_activity_with_entity_id_filter(self, mock_session, sample_activities):
        """Test filtering by entity_id."""
        entity_id = sample_activities[0].entity_id
        entity_activities = [a for a in sample_activities if a.entity_id == entity_id]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = entity_activities
        mock_session.execute.return_value = mock_result

        activities = await get_recent_activity(mock_session, entity_id=entity_id)

        assert len(activities) == 2
        assert all(a.entity_id == entity_id for a in activities)

    @pytest.mark.asyncio
    async def test_get_recent_activity_with_days_filter(self, mock_session, sample_activities):
        """Test filtering by days parameter."""
        # Only get last 2 days
        recent = [a for a in sample_activities if (datetime.utcnow() - a.created_at).days <= 2]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = recent
        mock_session.execute.return_value = mock_result

        activities = await get_recent_activity(mock_session, days=2)

        assert len(activities) == 3

    @pytest.mark.asyncio
    async def test_get_recent_activity_with_pagination(self, mock_session, sample_activities):
        """Test pagination parameters."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_activities[1]]
        mock_session.execute.return_value = mock_result

        activities = await get_recent_activity(mock_session, skip=1, limit=1)

        assert len(activities) == 1
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_recent_activity_empty_result(self, mock_session):
        """Test when no activities match filters."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        activities = await get_recent_activity(mock_session, user_id=999)

        assert activities == []


class TestGetActivityByEntity:
    """Test get_activity_by_entity function."""

    @pytest.mark.asyncio
    async def test_get_activity_by_entity_success(self, mock_session, sample_activities):
        """Test getting activity logs for specific entity."""
        entity_id = sample_activities[0].entity_id
        entity_activities = [
            a for a in sample_activities
            if a.entity_id == entity_id and a.entity_type == "work"
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = entity_activities
        mock_session.execute.return_value = mock_result

        activities = await get_activity_by_entity(
            mock_session, entity_type="work", entity_id=entity_id
        )

        assert len(activities) == 2
        assert all(a.entity_id == entity_id for a in activities)
        assert all(a.entity_type == "work" for a in activities)

    @pytest.mark.asyncio
    async def test_get_activity_by_entity_with_pagination(self, mock_session, sample_activities):
        """Test pagination for entity audit trail."""
        entity_id = sample_activities[0].entity_id
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_activities[1]]
        mock_session.execute.return_value = mock_result

        activities = await get_activity_by_entity(
            mock_session, entity_type="work", entity_id=entity_id, skip=1, limit=1
        )

        assert len(activities) == 1

    @pytest.mark.asyncio
    async def test_get_activity_by_entity_empty(self, mock_session):
        """Test when entity has no activity."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        activities = await get_activity_by_entity(
            mock_session, entity_type="work", entity_id=uuid4()
        )

        assert activities == []


class TestGetActivityStats:
    """Test get_activity_stats function."""

    @pytest.mark.asyncio
    async def test_get_activity_stats_no_user_filter(self, mock_session):
        """Test getting stats without user filter."""
        # Mock total count
        total_result = MagicMock()
        total_result.scalar.return_value = 10

        # Mock action breakdown
        action_result = MagicMock()
        action_rows = [
            MagicMock(action="work.create", count=5),
            MagicMock(action="work.update", count=3),
            MagicMock(action="catalog.upload", count=2),
        ]
        action_result.all.return_value = action_rows

        # Mock status breakdown
        status_result = MagicMock()
        success_status = MagicMock()
        success_status.value = "SUCCESS"
        failure_status = MagicMock()
        failure_status.value = "FAILURE"
        status_rows = [
            MagicMock(status=success_status, count=8),
            MagicMock(status=failure_status, count=2),
        ]
        status_result.all.return_value = status_rows

        # Mock entity breakdown
        entity_result = MagicMock()
        entity_rows = [
            MagicMock(entity_type="work", count=8),
            MagicMock(entity_type="catalog", count=2),
        ]
        entity_result.all.return_value = entity_rows

        mock_session.execute.side_effect = [
            total_result,
            action_result,
            status_result,
            entity_result,
        ]

        stats = await get_activity_stats(mock_session)

        assert stats["total_actions"] == 10
        assert stats["by_action"]["work.create"] == 5
        assert stats["by_status"]["SUCCESS"] == 8
        assert stats["by_entity"]["work"] == 8
        assert stats["period_days"] == 30

    @pytest.mark.asyncio
    async def test_get_activity_stats_with_user_filter(self, mock_session):
        """Test getting stats for specific user."""
        # Mock total count
        total_result = MagicMock()
        total_result.scalar.return_value = 5

        # Mock action breakdown
        action_result = MagicMock()
        action_rows = [MagicMock(action="work.create", count=5)]
        action_result.all.return_value = action_rows

        # Mock status breakdown
        status_result = MagicMock()
        success_status = MagicMock()
        success_status.value = "SUCCESS"
        status_rows = [MagicMock(status=success_status, count=5)]
        status_result.all.return_value = status_rows

        # Mock entity breakdown
        entity_result = MagicMock()
        entity_rows = [MagicMock(entity_type="work", count=5)]
        entity_result.all.return_value = entity_rows

        mock_session.execute.side_effect = [
            total_result,
            action_result,
            status_result,
            entity_result,
        ]

        stats = await get_activity_stats(mock_session, user_id=1)

        assert stats["total_actions"] == 5
        assert len(stats["by_action"]) == 1

    @pytest.mark.asyncio
    async def test_get_activity_stats_custom_days(self, mock_session):
        """Test stats with custom days period."""
        # Mock total count
        total_result = MagicMock()
        total_result.scalar.return_value = 3

        # Mock empty breakdowns
        action_result = MagicMock()
        action_result.all.return_value = []

        status_result = MagicMock()
        status_result.all.return_value = []

        entity_result = MagicMock()
        entity_result.all.return_value = []

        mock_session.execute.side_effect = [
            total_result,
            action_result,
            status_result,
            entity_result,
        ]

        stats = await get_activity_stats(mock_session, days=7)

        assert stats["period_days"] == 7
        assert stats["total_actions"] == 3

    @pytest.mark.asyncio
    async def test_get_activity_stats_zero_activities(self, mock_session):
        """Test stats when no activities exist."""
        # Mock total count = 0
        total_result = MagicMock()
        total_result.scalar.return_value = None

        # Mock empty breakdowns
        action_result = MagicMock()
        action_result.all.return_value = []

        status_result = MagicMock()
        status_result.all.return_value = []

        entity_result = MagicMock()
        entity_result.all.return_value = []

        mock_session.execute.side_effect = [
            total_result,
            action_result,
            status_result,
            entity_result,
        ]

        stats = await get_activity_stats(mock_session)

        assert stats["total_actions"] == 0
        assert stats["by_action"] == {}
        assert stats["by_status"] == {}
        assert stats["by_entity"] == {}


class TestActivityIntegration:
    """Integration tests for activity log CRUD operations."""

    @pytest.mark.asyncio
    async def test_full_activity_workflow(self, mock_session, activity_data, sample_activity):
        """Test complete workflow: log → get recent → get by entity → stats."""
        # 1. Log activity
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch("app.crud.activity.ActivityLog", return_value=sample_activity):
            logged = await log_activity(mock_session, activity_data)
            assert logged.action == "work.create"

        # 2. Get recent activity
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_activity]
        mock_session.execute.return_value = mock_result

        recent = await get_recent_activity(mock_session, user_id=1)
        assert len(recent) == 1

        # 3. Get activity by entity
        mock_result2 = MagicMock()
        mock_result2.scalars.return_value.all.return_value = [sample_activity]
        mock_session.execute.return_value = mock_result2

        entity_logs = await get_activity_by_entity(
            mock_session,
            entity_type=sample_activity.entity_type,
            entity_id=sample_activity.entity_id
        )
        assert len(entity_logs) == 1

        # 4. Get stats
        total_result = MagicMock()
        total_result.scalar.return_value = 1

        action_result = MagicMock()
        action_result.all.return_value = [MagicMock(action="work.create", count=1)]

        status_result = MagicMock()
        success_status = MagicMock()
        success_status.value = "SUCCESS"
        status_result.all.return_value = [MagicMock(status=success_status, count=1)]

        entity_result = MagicMock()
        entity_result.all.return_value = [MagicMock(entity_type="work", count=1)]

        mock_session.execute.side_effect = [
            total_result,
            action_result,
            status_result,
            entity_result,
        ]

        stats = await get_activity_stats(mock_session, user_id=1)
        assert stats["total_actions"] == 1

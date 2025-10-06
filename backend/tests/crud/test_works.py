"""Unit tests for works CRUD operations."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.works import (
    get_works,
    get_work_by_id,
    search_works,
    get_works_count,
    get_statistics,
)
from app.models.musical_work import MusicalWork
from app.models.resource import Resource


@pytest.fixture
def mock_session():
    """Create a mock AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_work():
    """Create a sample MusicalWork for testing (with mock to allow resources attribute)."""
    work = MagicMock(spec=MusicalWork)
    work.id = 1
    work.title = "Test Symphony"
    work.contributors = "Test Composer"
    work.publisher = "Test Publisher"
    work.iswc = "T-123.456.789-0"
    work.territory = "US"
    work.has_disputed_rights = False
    work.created_at = datetime.utcnow()
    work.updated_at = datetime.utcnow()
    # Allow resources attribute to be set
    work.resources = []
    return work


@pytest.fixture
def sample_works():
    """Create a list of sample works."""
    return [
        MusicalWork(
            id=1,
            title="Symphony No. 1",
            contributors="Beethoven",
            publisher="Universal",
            iswc="T-123.456.789-0",
            has_disputed_rights=False,
            created_at=datetime.utcnow() - timedelta(days=10),
        ),
        MusicalWork(
            id=2,
            title="Piano Sonata",
            contributors="Mozart",
            publisher="Warner",
            iswc=None,
            has_disputed_rights=True,
            created_at=datetime.utcnow() - timedelta(days=5),
        ),
        MusicalWork(
            id=3,
            title="String Quartet",
            contributors="Haydn",
            publisher="Sony",
            iswc="T-987.654.321-0",
            has_disputed_rights=False,
            created_at=datetime.utcnow(),
        ),
    ]


class TestGetWorks:
    """Test get_works function."""

    @pytest.mark.asyncio
    async def test_get_works_no_filters(self, mock_session, sample_works):
        """Test getting works without filters."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_works
        mock_session.execute.return_value = mock_result

        works = await get_works(mock_session, skip=0, limit=50)

        assert len(works) == 3
        assert works[0].title == "Symphony No. 1"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_works_with_pagination(self, mock_session, sample_works):
        """Test pagination parameters."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_works[1:]
        mock_session.execute.return_value = mock_result

        works = await get_works(mock_session, skip=1, limit=2)

        assert len(works) == 2
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_works_with_search_filter(self, mock_session, sample_works):
        """Test search filter."""
        mock_result = MagicMock()
        filtered_works = [w for w in sample_works if "Symphony" in w.title]
        mock_result.scalars.return_value.all.return_value = filtered_works
        mock_session.execute.return_value = mock_result

        works = await get_works(
            mock_session,
            filters={"search": "Symphony"}
        )

        assert len(works) == 1
        assert "Symphony" in works[0].title

    @pytest.mark.asyncio
    async def test_get_works_with_iswc_filter_true(self, mock_session, sample_works):
        """Test filtering works with ISWC."""
        mock_result = MagicMock()
        filtered_works = [w for w in sample_works if w.iswc is not None]
        mock_result.scalars.return_value.all.return_value = filtered_works
        mock_session.execute.return_value = mock_result

        works = await get_works(
            mock_session,
            filters={"has_iswc": True}
        )

        assert len(works) == 2
        assert all(w.iswc is not None for w in works)

    @pytest.mark.asyncio
    async def test_get_works_with_iswc_filter_false(self, mock_session, sample_works):
        """Test filtering works without ISWC."""
        mock_result = MagicMock()
        filtered_works = [w for w in sample_works if w.iswc is None]
        mock_result.scalars.return_value.all.return_value = filtered_works
        mock_session.execute.return_value = mock_result

        works = await get_works(
            mock_session,
            filters={"has_iswc": False}
        )

        assert len(works) == 1
        assert works[0].iswc is None

    @pytest.mark.asyncio
    async def test_get_works_with_disputed_rights_filter(self, mock_session, sample_works):
        """Test filtering by disputed rights."""
        mock_result = MagicMock()
        filtered_works = [w for w in sample_works if w.has_disputed_rights]
        mock_result.scalars.return_value.all.return_value = filtered_works
        mock_session.execute.return_value = mock_result

        works = await get_works(
            mock_session,
            filters={"has_disputed_rights": True}
        )

        assert len(works) == 1
        assert works[0].has_disputed_rights is True

    @pytest.mark.asyncio
    async def test_get_works_with_date_filters(self, mock_session, sample_works):
        """Test filtering by date range."""
        mock_result = MagicMock()
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)

        filtered_works = [w for w in sample_works if w.created_at >= week_ago]
        mock_result.scalars.return_value.all.return_value = filtered_works
        mock_session.execute.return_value = mock_result

        works = await get_works(
            mock_session,
            filters={"created_after": week_ago}
        )

        assert len(works) == 2
        assert all(w.created_at >= week_ago for w in works)

    @pytest.mark.asyncio
    async def test_get_works_with_multiple_filters(self, mock_session, sample_works):
        """Test combining multiple filters."""
        mock_result = MagicMock()
        filtered_works = [w for w in sample_works if w.iswc is not None and not w.has_disputed_rights]
        mock_result.scalars.return_value.all.return_value = filtered_works
        mock_session.execute.return_value = mock_result

        works = await get_works(
            mock_session,
            filters={
                "has_iswc": True,
                "has_disputed_rights": False
            }
        )

        assert len(works) == 2
        assert all(w.iswc is not None and not w.has_disputed_rights for w in works)

    @pytest.mark.asyncio
    async def test_get_works_empty_result(self, mock_session):
        """Test when no works match."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        works = await get_works(mock_session)

        assert works == []


class TestGetWorkById:
    """Test get_work_by_id function."""

    @pytest.mark.asyncio
    async def test_get_work_by_id_found(self, mock_session, sample_work):
        """Test getting work by ID when found."""
        resource1 = Resource(id=1, resource_type="musicbrainz", resource_identifier="mb-123")
        resource2 = Resource(id=2, resource_type="spotify", resource_identifier="spotify-456")

        mock_result = MagicMock()
        mock_result.all.return_value = [
            (sample_work, resource1),
            (sample_work, resource2),
        ]
        mock_session.execute.return_value = mock_result

        work = await get_work_by_id(mock_session, work_id=1)

        assert work is not None
        assert work.id == 1
        assert work.title == "Test Symphony"
        assert len(work.resources) == 2
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_work_by_id_with_no_resources(self, mock_session, sample_work):
        """Test getting work with no resources."""
        mock_result = MagicMock()
        mock_result.all.return_value = [(sample_work, None)]
        mock_session.execute.return_value = mock_result

        work = await get_work_by_id(mock_session, work_id=1)

        assert work is not None
        assert work.id == 1
        assert work.resources == []

    @pytest.mark.asyncio
    async def test_get_work_by_id_not_found(self, mock_session):
        """Test getting work that doesn't exist."""
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute.return_value = mock_result

        work = await get_work_by_id(mock_session, work_id=999)

        assert work is None

    @pytest.mark.asyncio
    async def test_get_work_by_id_duplicate_resources(self, mock_session, sample_work):
        """Test that duplicate resources are removed."""
        resource = Resource(id=1, resource_type="musicbrainz", resource_identifier="mb-123")

        mock_result = MagicMock()
        # Same resource appears twice (could happen with complex joins)
        mock_result.all.return_value = [
            (sample_work, resource),
            (sample_work, resource),
        ]
        mock_session.execute.return_value = mock_result

        work = await get_work_by_id(mock_session, work_id=1)

        assert work is not None
        assert len(work.resources) == 1  # Duplicates removed


class TestSearchWorks:
    """Test search_works function."""

    @pytest.mark.asyncio
    async def test_search_works_basic(self, mock_session, sample_works):
        """Test basic search."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_works[0]]
        mock_session.execute.return_value = mock_result

        works = await search_works(mock_session, query="Symphony")

        assert len(works) == 1
        assert "Symphony" in works[0].title

    @pytest.mark.asyncio
    async def test_search_works_multiple_fields(self, mock_session, sample_works):
        """Test search across title, contributors, and publisher."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_works[0]]
        mock_session.execute.return_value = mock_result

        # Should search in all fields
        works = await search_works(mock_session, query="Beethoven")

        assert len(works) == 1
        assert "Beethoven" in works[0].contributors

    @pytest.mark.asyncio
    async def test_search_works_with_filters(self, mock_session, sample_works):
        """Test search with additional filters."""
        mock_result = MagicMock()
        filtered = [w for w in sample_works if w.iswc is not None]
        mock_result.scalars.return_value.all.return_value = filtered
        mock_session.execute.return_value = mock_result

        works = await search_works(
            mock_session,
            query="Symphony",
            filters={"has_iswc": True}
        )

        assert len(works) == 2
        assert all(w.iswc is not None for w in works)

    @pytest.mark.asyncio
    async def test_search_works_with_pagination(self, mock_session, sample_works):
        """Test search pagination."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_works[1:2]
        mock_session.execute.return_value = mock_result

        works = await search_works(
            mock_session,
            query="test",
            skip=1,
            limit=1
        )

        assert len(works) == 1

    @pytest.mark.asyncio
    async def test_search_works_no_results(self, mock_session):
        """Test search with no matching results."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        works = await search_works(mock_session, query="nonexistent")

        assert works == []


class TestGetWorksCount:
    """Test get_works_count function."""

    @pytest.mark.asyncio
    async def test_get_works_count_no_filters(self, mock_session):
        """Test count without filters."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 10
        mock_session.execute.return_value = mock_result

        count = await get_works_count(mock_session)

        assert count == 10
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_works_count_with_search_filter(self, mock_session):
        """Test count with search filter."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 3
        mock_session.execute.return_value = mock_result

        count = await get_works_count(
            mock_session,
            filters={"search": "Symphony"}
        )

        assert count == 3

    @pytest.mark.asyncio
    async def test_get_works_count_with_iswc_filter(self, mock_session):
        """Test count with ISWC filter."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 5
        mock_session.execute.return_value = mock_result

        count = await get_works_count(
            mock_session,
            filters={"has_iswc": True}
        )

        assert count == 5

    @pytest.mark.asyncio
    async def test_get_works_count_zero(self, mock_session):
        """Test count when no works match."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 0
        mock_session.execute.return_value = mock_result

        count = await get_works_count(
            mock_session,
            filters={"search": "nonexistent"}
        )

        assert count == 0


class TestGetStatistics:
    """Test get_statistics function."""

    @pytest.mark.asyncio
    async def test_get_statistics(self, mock_session):
        """Test getting dashboard statistics."""
        # Mock total works count
        total_result = MagicMock()
        total_result.scalar_one.return_value = 100

        # Mock ISWC count
        iswc_result = MagicMock()
        iswc_result.scalar_one.return_value = 75

        # Mock disputed count
        disputed_result = MagicMock()
        disputed_result.scalar_one.return_value = 5

        # Mock monthly trend
        trend_result = MagicMock()
        mock_row1 = MagicMock()
        mock_row1.month = datetime(2025, 9, 1)
        mock_row1.count = 30

        mock_row2 = MagicMock()
        mock_row2.month = datetime(2025, 10, 1)
        mock_row2.count = 40

        trend_result.all.return_value = [mock_row1, mock_row2]

        # Set up execute to return different results for each call
        mock_session.execute.side_effect = [
            total_result,
            iswc_result,
            disputed_result,
            trend_result,
        ]

        stats = await get_statistics(mock_session)

        assert stats["total_works"] == 100
        assert stats["works_with_iswc"] == 75
        assert stats["disputed_works"] == 5
        assert len(stats["monthly_trend"]) == 2
        assert stats["monthly_trend"][0]["month"] == "2025-09"
        assert stats["monthly_trend"][0]["count"] == 30
        assert stats["monthly_trend"][1]["month"] == "2025-10"
        assert stats["monthly_trend"][1]["count"] == 40

    @pytest.mark.asyncio
    async def test_get_statistics_zero_works(self, mock_session):
        """Test statistics when database is empty."""
        # All counts are zero
        zero_result = MagicMock()
        zero_result.scalar_one.return_value = 0

        # Empty trend
        trend_result = MagicMock()
        trend_result.all.return_value = []

        mock_session.execute.side_effect = [
            zero_result,
            zero_result,
            zero_result,
            trend_result,
        ]

        stats = await get_statistics(mock_session)

        assert stats["total_works"] == 0
        assert stats["works_with_iswc"] == 0
        assert stats["disputed_works"] == 0
        assert stats["monthly_trend"] == []

    @pytest.mark.asyncio
    async def test_get_statistics_trend_formatting(self, mock_session):
        """Test monthly trend date formatting."""
        total_result = MagicMock()
        total_result.scalar_one.return_value = 50

        iswc_result = MagicMock()
        iswc_result.scalar_one.return_value = 30

        disputed_result = MagicMock()
        disputed_result.scalar_one.return_value = 2

        trend_result = MagicMock()
        mock_row = MagicMock()
        mock_row.month = datetime(2025, 1, 1)
        mock_row.count = 10
        trend_result.all.return_value = [mock_row]

        mock_session.execute.side_effect = [
            total_result,
            iswc_result,
            disputed_result,
            trend_result,
        ]

        stats = await get_statistics(mock_session)

        # Verify date is formatted as YYYY-MM
        assert stats["monthly_trend"][0]["month"] == "2025-01"


class TestWorksIntegration:
    """Integration tests for works CRUD operations."""

    @pytest.mark.asyncio
    async def test_full_workflow(self, mock_session, sample_works):
        """Test a complete workflow: list → count → get detail."""
        # Setup mocks for list
        list_result = MagicMock()
        list_result.scalars.return_value.all.return_value = sample_works

        # Setup mocks for count
        count_result = MagicMock()
        count_result.scalar_one.return_value = len(sample_works)

        # Setup mocks for detail - use mock work to allow resources attribute
        mock_work = MagicMock(spec=MusicalWork)
        mock_work.id = 1
        mock_work.title = "Symphony No. 1"
        mock_work.resources = []

        detail_result = MagicMock()
        detail_result.all.return_value = [(mock_work, None)]

        mock_session.execute.side_effect = [list_result, count_result, detail_result]

        # 1. List works
        works = await get_works(mock_session, skip=0, limit=10)
        assert len(works) == 3

        # 2. Get count
        count = await get_works_count(mock_session)
        assert count == 3

        # 3. Get detail
        work = await get_work_by_id(mock_session, work_id=1)
        assert work is not None
        assert work.id == 1

    @pytest.mark.asyncio
    async def test_filter_consistency(self, mock_session):
        """Test that get_works and get_works_count use same filters."""
        filters = {
            "has_iswc": True,
            "has_disputed_rights": False,
            "search": "Symphony"
        }

        # Both should use the same filter logic
        list_result = MagicMock()
        list_result.scalars.return_value.all.return_value = []

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        mock_session.execute.side_effect = [list_result, count_result]

        works = await get_works(mock_session, filters=filters)
        count = await get_works_count(mock_session, filters=filters)

        # Both queries should be executed
        assert mock_session.execute.call_count == 2

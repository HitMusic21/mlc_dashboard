"""Unit tests for catalog matching CRUD operations."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.matches import (
    create_match,
    create_matches_bulk,
    get_matches_for_upload,
    get_matches_grouped,
    get_match_statistics,
)
from app.models.catalog_match import CatalogMatch, ConfidenceLevel
from app.models.musical_work import MusicalWork


@pytest.fixture
def mock_session():
    """Create a mock AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def match_data():
    """Sample match data dictionary."""
    return {
        "catalog_upload_id": 1,
        "musical_work_id": 1,
        "uploaded_track_title": "Yesterday",
        "uploaded_track_artist": "The Beatles",
        "uploaded_track_duration": 125,
        "match_score": 0.95,
        "confidence_level": ConfidenceLevel.HIGH,
        "title_similarity": 1.0,
        "artist_similarity": 0.9,
    }


@pytest.fixture
def sample_match():
    """Create a sample CatalogMatch."""
    match = MagicMock(spec=CatalogMatch)
    match.id = 1
    match.catalog_upload_id = 1
    match.musical_work_id = 1
    match.uploaded_track_title = "Yesterday"
    match.uploaded_track_artist = "The Beatles"
    match.uploaded_track_duration = 125
    match.match_score = 0.95
    match.confidence_level = ConfidenceLevel.HIGH
    match.title_similarity = 1.0
    match.artist_similarity = 0.9
    match.created_at = datetime.utcnow()
    return match


@pytest.fixture
def sample_matches():
    """Create a list of sample matches (using mocks to allow work attribute)."""
    matches = []

    # Match 1 - HIGH confidence
    match1 = MagicMock(spec=CatalogMatch)
    match1.id = 1
    match1.catalog_upload_id = 1
    match1.musical_work_id = 1
    match1.uploaded_track_title = "Yesterday"
    match1.uploaded_track_artist = "The Beatles"
    match1.uploaded_track_duration = 125
    match1.match_score = 0.95
    match1.confidence_level = ConfidenceLevel.HIGH
    match1.title_similarity = 1.0
    match1.artist_similarity = 0.9
    matches.append(match1)

    # Match 2 - MEDIUM confidence (same track)
    match2 = MagicMock(spec=CatalogMatch)
    match2.id = 2
    match2.catalog_upload_id = 1
    match2.musical_work_id = 2
    match2.uploaded_track_title = "Yesterday"
    match2.uploaded_track_artist = "The Beatles"
    match2.uploaded_track_duration = 125
    match2.match_score = 0.85
    match2.confidence_level = ConfidenceLevel.MEDIUM
    match2.title_similarity = 0.9
    match2.artist_similarity = 0.8
    matches.append(match2)

    # Match 3 - HIGH confidence (different track)
    match3 = MagicMock(spec=CatalogMatch)
    match3.id = 3
    match3.catalog_upload_id = 1
    match3.musical_work_id = 3
    match3.uploaded_track_title = "Hey Jude"
    match3.uploaded_track_artist = "The Beatles"
    match3.uploaded_track_duration = 431
    match3.match_score = 0.92
    match3.confidence_level = ConfidenceLevel.HIGH
    match3.title_similarity = 1.0
    match3.artist_similarity = 0.85
    matches.append(match3)

    # Match 4 - LOW confidence
    match4 = MagicMock(spec=CatalogMatch)
    match4.id = 4
    match4.catalog_upload_id = 1
    match4.musical_work_id = 4
    match4.uploaded_track_title = "Let It Be"
    match4.uploaded_track_artist = "The Beatles"
    match4.uploaded_track_duration = 243
    match4.match_score = 0.65
    match4.confidence_level = ConfidenceLevel.LOW
    match4.title_similarity = 0.7
    match4.artist_similarity = 0.6
    matches.append(match4)

    return matches


@pytest.fixture
def sample_work():
    """Create a sample MusicalWork."""
    work = MagicMock(spec=MusicalWork)
    work.id = 1
    work.title = "Yesterday"
    work.contributors = "Lennon/McCartney"
    work.publisher = "Sony/ATV"
    work.iswc = "T-070.127.829-8"
    return work


class TestCreateMatch:
    """Test create_match function."""

    @pytest.mark.asyncio
    async def test_create_match_success(self, mock_session, match_data):
        """Test creating a single match."""
        created_match = CatalogMatch(**match_data)

        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Mock the CatalogMatch creation
        with patch(
            "app.crud.matches.CatalogMatch", return_value=created_match
        ):
            match = await create_match(mock_session, match_data)

            assert match.uploaded_track_title == "Yesterday"
            assert match.match_score == 0.95
            assert match.confidence_level == ConfidenceLevel.HIGH
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_match_with_high_score(self, mock_session, match_data):
        """Test creating match with high match score."""
        match_data["match_score"] = 0.98

        created_match = MagicMock(spec=CatalogMatch)
        for key, value in match_data.items():
            setattr(created_match, key, value)

        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch(
            "app.crud.matches.CatalogMatch", return_value=created_match
        ):
            match = await create_match(mock_session, match_data)

            assert match.match_score == 0.98
            assert match.confidence_level == ConfidenceLevel.HIGH


class TestCreateMatchesBulk:
    """Test create_matches_bulk function."""

    @pytest.mark.asyncio
    async def test_create_matches_bulk_success(self, mock_session):
        """Test creating multiple matches in bulk."""
        matches_data = [
            {
                "catalog_upload_id": 1,
                "musical_work_id": i,
                "uploaded_track_title": f"Track {i}",
                "uploaded_track_artist": "Artist",
                "match_score": 0.8 + (i * 0.05),
                "confidence_level": ConfidenceLevel.MEDIUM,
            }
            for i in range(5)
        ]

        created_matches = [CatalogMatch(**data) for data in matches_data]

        mock_session.add_all = MagicMock()
        mock_session.commit = AsyncMock()

        with patch(
            "app.crud.matches.CatalogMatch",
            side_effect=created_matches
        ):
            matches = await create_matches_bulk(mock_session, matches_data)

            assert len(matches) == 5
            mock_session.add_all.assert_called_once()
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_matches_bulk_empty_list(self, mock_session):
        """Test creating bulk with empty list."""
        mock_session.add_all = MagicMock()
        mock_session.commit = AsyncMock()

        matches = await create_matches_bulk(mock_session, [])

        assert matches == []
        mock_session.add_all.assert_called_once_with([])
        mock_session.commit.assert_called_once()


class TestGetMatchesForUpload:
    """Test get_matches_for_upload function."""

    @pytest.mark.asyncio
    async def test_get_matches_no_filters(self, mock_session, sample_matches, sample_work):
        """Test getting matches without filters."""
        mock_result = MagicMock()
        # Simulate JOIN result (match, work) tuples
        rows = [(match, sample_work) for match in sample_matches]
        mock_result.all.return_value = rows
        mock_session.execute.return_value = mock_result

        matches = await get_matches_for_upload(mock_session, upload_id=1)

        assert len(matches) == 4
        # Verify work is attached to match
        assert all(hasattr(m, 'work') for m in matches)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_matches_with_confidence_filter(
        self, mock_session, sample_matches, sample_work
    ):
        """Test filtering matches by confidence level."""
        mock_result = MagicMock()
        high_confidence = [m for m in sample_matches if m.confidence_level == ConfidenceLevel.HIGH]
        rows = [(match, sample_work) for match in high_confidence]
        mock_result.all.return_value = rows
        mock_session.execute.return_value = mock_result

        matches = await get_matches_for_upload(
            mock_session,
            upload_id=1,
            filters={"confidence": "high"}
        )

        assert len(matches) == 2
        assert all(m.confidence_level == ConfidenceLevel.HIGH for m in matches)

    @pytest.mark.asyncio
    async def test_get_matches_with_min_score_filter(
        self, mock_session, sample_matches, sample_work
    ):
        """Test filtering matches by minimum score."""
        mock_result = MagicMock()
        high_scores = [m for m in sample_matches if m.match_score >= 0.9]
        rows = [(match, sample_work) for match in high_scores]
        mock_result.all.return_value = rows
        mock_session.execute.return_value = mock_result

        matches = await get_matches_for_upload(
            mock_session,
            upload_id=1,
            filters={"min_score": 0.9}
        )

        assert len(matches) == 2
        assert all(m.match_score >= 0.9 for m in matches)

    @pytest.mark.asyncio
    async def test_get_matches_with_combined_filters(
        self, mock_session, sample_matches, sample_work
    ):
        """Test combining confidence and score filters."""
        mock_result = MagicMock()
        filtered = [
            m for m in sample_matches
            if m.confidence_level == ConfidenceLevel.HIGH and m.match_score >= 0.9
        ]
        rows = [(match, sample_work) for match in filtered]
        mock_result.all.return_value = rows
        mock_session.execute.return_value = mock_result

        matches = await get_matches_for_upload(
            mock_session,
            upload_id=1,
            filters={"confidence": "high", "min_score": 0.9}
        )

        assert len(matches) == 2
        assert all(m.confidence_level == ConfidenceLevel.HIGH for m in matches)
        assert all(m.match_score >= 0.9 for m in matches)

    @pytest.mark.asyncio
    async def test_get_matches_with_pagination(
        self, mock_session, sample_matches, sample_work
    ):
        """Test pagination parameters."""
        mock_result = MagicMock()
        rows = [(sample_matches[1], sample_work)]
        mock_result.all.return_value = rows
        mock_session.execute.return_value = mock_result

        matches = await get_matches_for_upload(
            mock_session,
            upload_id=1,
            skip=1,
            limit=1
        )

        assert len(matches) == 1
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_matches_empty_result(self, mock_session):
        """Test when no matches exist."""
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute.return_value = mock_result

        matches = await get_matches_for_upload(mock_session, upload_id=999)

        assert matches == []


class TestGetMatchesGrouped:
    """Test get_matches_grouped function."""

    @pytest.mark.asyncio
    async def test_get_matches_grouped(self, mock_session, sample_matches, sample_work):
        """Test grouping matches by uploaded track."""
        # Mock get_matches_for_upload
        with patch(
            "app.crud.matches.get_matches_for_upload",
            return_value=sample_matches
        ):
            grouped = await get_matches_grouped(mock_session, upload_id=1)

            # Should have 3 unique tracks
            assert len(grouped) == 3

            # Verify structure
            assert all("uploaded_track" in group for group in grouped)
            assert all("matches" in group for group in grouped)

            # Find Yesterday group (should have 2 matches)
            yesterday_group = next(
                g for g in grouped
                if g["uploaded_track"]["title"] == "Yesterday"
            )
            assert len(yesterday_group["matches"]) == 2

    @pytest.mark.asyncio
    async def test_get_matches_grouped_with_filters(self, mock_session, sample_matches):
        """Test grouping with filters applied."""
        # Only high confidence matches
        high_confidence = [
            m for m in sample_matches
            if m.confidence_level == ConfidenceLevel.HIGH
        ]

        with patch(
            "app.crud.matches.get_matches_for_upload",
            return_value=high_confidence
        ):
            grouped = await get_matches_grouped(
                mock_session,
                upload_id=1,
                filters={"confidence": "high"}
            )

            # Should have 2 unique tracks
            assert len(grouped) == 2

    @pytest.mark.asyncio
    async def test_get_matches_grouped_empty(self, mock_session):
        """Test grouping with no matches."""
        with patch(
            "app.crud.matches.get_matches_for_upload",
            return_value=[]
        ):
            grouped = await get_matches_grouped(mock_session, upload_id=999)

            assert grouped == []

    @pytest.mark.asyncio
    async def test_get_matches_grouped_track_structure(
        self, mock_session, sample_matches
    ):
        """Test uploaded_track structure contains all fields."""
        with patch(
            "app.crud.matches.get_matches_for_upload",
            return_value=sample_matches[:1]
        ):
            grouped = await get_matches_grouped(mock_session, upload_id=1)

            track = grouped[0]["uploaded_track"]
            assert "title" in track
            assert "artist" in track
            assert "duration" in track
            assert track["title"] == "Yesterday"
            assert track["artist"] == "The Beatles"
            assert track["duration"] == 125


class TestGetMatchStatistics:
    """Test get_match_statistics function."""

    @pytest.mark.asyncio
    async def test_get_match_statistics(self, mock_session):
        """Test getting match statistics."""
        # Mock total matches
        total_result = MagicMock()
        total_result.scalar_one.return_value = 10

        # Mock confidence breakdown
        confidence_result = MagicMock()
        mock_rows = [
            (ConfidenceLevel.HIGH, 4),
            (ConfidenceLevel.MEDIUM, 3),
            (ConfidenceLevel.LOW, 3),
        ]
        confidence_result.all.return_value = mock_rows

        # Mock average score
        avg_result = MagicMock()
        avg_result.scalar_one.return_value = 0.85

        mock_session.execute.side_effect = [
            total_result,
            confidence_result,
            avg_result,
        ]

        stats = await get_match_statistics(mock_session, upload_id=1)

        assert stats["total_matches"] == 10
        assert stats["high_confidence"] == 4
        assert stats["medium_confidence"] == 3
        assert stats["low_confidence"] == 3
        assert stats["average_score"] == 0.85

    @pytest.mark.asyncio
    async def test_get_match_statistics_no_matches(self, mock_session):
        """Test statistics when no matches exist."""
        # Mock total matches
        total_result = MagicMock()
        total_result.scalar_one.return_value = 0

        # Mock empty confidence breakdown
        confidence_result = MagicMock()
        confidence_result.all.return_value = []

        # Mock average score (None when no matches)
        avg_result = MagicMock()
        avg_result.scalar_one.return_value = None

        mock_session.execute.side_effect = [
            total_result,
            confidence_result,
            avg_result,
        ]

        stats = await get_match_statistics(mock_session, upload_id=999)

        assert stats["total_matches"] == 0
        assert stats["high_confidence"] == 0
        assert stats["medium_confidence"] == 0
        assert stats["low_confidence"] == 0
        assert stats["average_score"] == 0.0

    @pytest.mark.asyncio
    async def test_get_match_statistics_only_high_confidence(self, mock_session):
        """Test statistics with only high confidence matches."""
        # Mock total matches
        total_result = MagicMock()
        total_result.scalar_one.return_value = 5

        # Mock confidence breakdown (only HIGH)
        confidence_result = MagicMock()
        confidence_result.all.return_value = [(ConfidenceLevel.HIGH, 5)]

        # Mock average score
        avg_result = MagicMock()
        avg_result.scalar_one.return_value = 0.95

        mock_session.execute.side_effect = [
            total_result,
            confidence_result,
            avg_result,
        ]

        stats = await get_match_statistics(mock_session, upload_id=1)

        assert stats["total_matches"] == 5
        assert stats["high_confidence"] == 5
        assert stats["medium_confidence"] == 0
        assert stats["low_confidence"] == 0
        assert stats["average_score"] == 0.95

    @pytest.mark.asyncio
    async def test_get_match_statistics_score_rounding(self, mock_session):
        """Test that average score is rounded to 4 decimals."""
        # Mock results
        total_result = MagicMock()
        total_result.scalar_one.return_value = 3

        confidence_result = MagicMock()
        confidence_result.all.return_value = [(ConfidenceLevel.MEDIUM, 3)]

        # Mock average with many decimals
        avg_result = MagicMock()
        avg_result.scalar_one.return_value = 0.8567891234

        mock_session.execute.side_effect = [
            total_result,
            confidence_result,
            avg_result,
        ]

        stats = await get_match_statistics(mock_session, upload_id=1)

        assert stats["average_score"] == 0.8568  # Rounded to 4 decimals


class TestMatchesIntegration:
    """Integration tests for matching CRUD operations."""

    @pytest.mark.asyncio
    async def test_full_matching_workflow(
        self, mock_session, match_data, sample_matches, sample_work
    ):
        """Test complete matching workflow: create → get → stats."""
        # 1. Create match
        created_match = CatalogMatch(**match_data)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch(
            "app.crud.matches.CatalogMatch", return_value=created_match
        ):
            match = await create_match(mock_session, match_data)
            assert match.match_score == 0.95

        # 2. Get matches for upload
        mock_result = MagicMock()
        rows = [(m, sample_work) for m in sample_matches]
        mock_result.all.return_value = rows
        mock_session.execute.return_value = mock_result

        matches = await get_matches_for_upload(mock_session, upload_id=1)
        assert len(matches) == 4

        # 3. Get statistics
        total_result = MagicMock()
        total_result.scalar_one.return_value = 4

        confidence_result = MagicMock()
        confidence_result.all.return_value = [
            (ConfidenceLevel.HIGH, 2),
            (ConfidenceLevel.MEDIUM, 1),
            (ConfidenceLevel.LOW, 1),
        ]

        avg_result = MagicMock()
        avg_result.scalar_one.return_value = 0.8425

        mock_session.execute.side_effect = [
            total_result,
            confidence_result,
            avg_result,
        ]

        stats = await get_match_statistics(mock_session, upload_id=1)
        assert stats["total_matches"] == 4
        assert stats["average_score"] == 0.8425

    @pytest.mark.asyncio
    async def test_bulk_create_and_query(self, mock_session, sample_work):
        """Test bulk creation and querying."""
        # 1. Bulk create
        matches_data = [
            {
                "catalog_upload_id": 1,
                "musical_work_id": i,
                "uploaded_track_title": f"Track {i}",
                "uploaded_track_artist": "Artist",
                "match_score": 0.8,
                "confidence_level": ConfidenceLevel.MEDIUM,
            }
            for i in range(10)
        ]

        # Create MagicMock matches to allow work attribute
        created_matches = []
        for data in matches_data:
            match = MagicMock(spec=CatalogMatch)
            for key, value in data.items():
                setattr(match, key, value)
            created_matches.append(match)

        mock_session.add_all = MagicMock()
        mock_session.commit = AsyncMock()

        with patch(
            "app.crud.matches.CatalogMatch",
            side_effect=created_matches
        ):
            matches = await create_matches_bulk(mock_session, matches_data)
            assert len(matches) == 10

        # 2. Query all matches
        mock_result = MagicMock()
        rows = [(m, sample_work) for m in created_matches]
        mock_result.all.return_value = rows
        mock_session.execute.return_value = mock_result

        all_matches = await get_matches_for_upload(
            mock_session,
            upload_id=1,
            limit=1000
        )
        assert len(all_matches) == 10

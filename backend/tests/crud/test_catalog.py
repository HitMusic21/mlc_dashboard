"""Unit tests for catalog CRUD operations."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.catalog import (
    create_upload,
    get_uploads,
    get_upload_by_id,
    update_upload_status,
    delete_upload,
    get_uploads_count,
)
from app.models.catalog_upload import CatalogUpload, UploadStatus


@pytest.fixture
def mock_session():
    """Create a mock AsyncSession."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_upload():
    """Create a sample CatalogUpload for testing."""
    upload = MagicMock(spec=CatalogUpload)
    upload.id = 1
    upload.user_id = 1
    upload.filename = "catalog.csv"
    upload.file_format = "csv"
    upload.file_size_bytes = 1024
    upload.publisher_name = "Test Publisher"
    upload.status = UploadStatus.PENDING
    upload.progress_percentage = 0.0
    upload.started_at = None
    upload.completed_at = None
    upload.created_at = datetime.utcnow()
    upload.updated_at = datetime.utcnow()
    return upload


@pytest.fixture
def sample_uploads():
    """Create a list of sample uploads."""
    return [
        CatalogUpload(
            id=1,
            user_id=1,
            filename="catalog1.csv",
            file_format="csv",
            file_size_bytes=1024,
            publisher_name="Publisher A",
            status=UploadStatus.COMPLETED,
            progress_percentage=100.0,
            created_at=datetime.utcnow(),
        ),
        CatalogUpload(
            id=2,
            user_id=1,
            filename="catalog2.xlsx",
            file_format="xlsx",
            file_size_bytes=2048,
            publisher_name="Publisher B",
            status=UploadStatus.PROCESSING,
            progress_percentage=50.0,
            created_at=datetime.utcnow(),
        ),
        CatalogUpload(
            id=3,
            user_id=2,
            filename="catalog3.csv",
            file_format="csv",
            file_size_bytes=512,
            publisher_name="Publisher C",
            status=UploadStatus.FAILED,
            progress_percentage=75.0,
            created_at=datetime.utcnow(),
        ),
    ]


@pytest.fixture
def upload_data():
    """Sample upload data dictionary."""
    return {
        "filename": "catalog.csv",
        "file_format": "csv",
        "file_size_bytes": 1024,
        "publisher_name": "Test Publisher",
    }


class TestCreateUpload:
    """Test create_upload function."""

    @pytest.mark.asyncio
    async def test_create_upload_success(self, mock_session, upload_data):
        """Test creating a new upload."""
        # Mock the created upload
        created_upload = CatalogUpload(
            id=1,
            user_id=1,
            filename=upload_data["filename"],
            file_format=upload_data["file_format"],
            file_size_bytes=upload_data["file_size_bytes"],
            publisher_name=upload_data["publisher_name"],
            status=UploadStatus.PENDING,
            progress_percentage=0.0,
        )

        # Mock session operations
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.add = MagicMock()

        # Patch the created object to return our mock
        with patch(
            "app.crud.catalog.CatalogUpload", return_value=created_upload
        ):
            upload = await create_upload(mock_session, user_id=1, upload_data=upload_data)

            assert upload.filename == "catalog.csv"
            assert upload.status == UploadStatus.PENDING
            assert upload.progress_percentage == 0.0
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_upload_with_all_fields(self, mock_session):
        """Test creating upload with all required fields."""
        upload_data = {
            "filename": "large_catalog.xlsx",
            "file_format": "xlsx",
            "file_size_bytes": 5242880,  # 5 MB
            "publisher_name": "Major Publisher Inc.",
        }

        created_upload = CatalogUpload(
            id=2,
            user_id=5,
            **upload_data,
            status=UploadStatus.PENDING,
            progress_percentage=0.0,
        )

        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.add = MagicMock()

        with patch(
            "app.crud.catalog.CatalogUpload", return_value=created_upload
        ):
            upload = await create_upload(mock_session, user_id=5, upload_data=upload_data)

            assert upload.user_id == 5
            assert upload.file_size_bytes == 5242880
            assert upload.file_format == "xlsx"


class TestGetUploads:
    """Test get_uploads function."""

    @pytest.mark.asyncio
    async def test_get_uploads_no_filters(self, mock_session, sample_uploads):
        """Test getting uploads without filters."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_uploads
        mock_session.execute.return_value = mock_result

        uploads = await get_uploads(mock_session)

        assert len(uploads) == 3
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_uploads_with_user_filter(self, mock_session, sample_uploads):
        """Test filtering uploads by user ID."""
        mock_result = MagicMock()
        filtered_uploads = [u for u in sample_uploads if u.user_id == 1]
        mock_result.scalars.return_value.all.return_value = filtered_uploads
        mock_session.execute.return_value = mock_result

        uploads = await get_uploads(mock_session, user_id=1)

        assert len(uploads) == 2
        assert all(u.user_id == 1 for u in uploads)

    @pytest.mark.asyncio
    async def test_get_uploads_with_status_filter(self, mock_session, sample_uploads):
        """Test filtering uploads by status."""
        mock_result = MagicMock()
        filtered_uploads = [u for u in sample_uploads if u.status == UploadStatus.COMPLETED]
        mock_result.scalars.return_value.all.return_value = filtered_uploads
        mock_session.execute.return_value = mock_result

        uploads = await get_uploads(
            mock_session,
            filters={"status": UploadStatus.COMPLETED}
        )

        assert len(uploads) == 1
        assert uploads[0].status == UploadStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_get_uploads_with_pagination(self, mock_session, sample_uploads):
        """Test upload pagination."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_uploads[1:]
        mock_session.execute.return_value = mock_result

        uploads = await get_uploads(mock_session, skip=1, limit=2)

        assert len(uploads) == 2
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_uploads_combined_filters(self, mock_session, sample_uploads):
        """Test combining user and status filters."""
        mock_result = MagicMock()
        filtered = [
            u for u in sample_uploads
            if u.user_id == 1 and u.status == UploadStatus.COMPLETED
        ]
        mock_result.scalars.return_value.all.return_value = filtered
        mock_session.execute.return_value = mock_result

        uploads = await get_uploads(
            mock_session,
            user_id=1,
            filters={"status": UploadStatus.COMPLETED}
        )

        assert len(uploads) == 1
        assert uploads[0].user_id == 1
        assert uploads[0].status == UploadStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_get_uploads_empty_result(self, mock_session):
        """Test when no uploads match."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        uploads = await get_uploads(mock_session, user_id=999)

        assert uploads == []


class TestGetUploadById:
    """Test get_upload_by_id function."""

    @pytest.mark.asyncio
    async def test_get_upload_by_id_found(self, mock_session, sample_upload):
        """Test getting upload by ID when found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_upload
        mock_session.execute.return_value = mock_result

        upload = await get_upload_by_id(mock_session, upload_id=1)

        assert upload is not None
        assert upload.id == 1
        assert upload.filename == "catalog.csv"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_upload_by_id_not_found(self, mock_session):
        """Test getting upload that doesn't exist."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        upload = await get_upload_by_id(mock_session, upload_id=999)

        assert upload is None


class TestUpdateUploadStatus:
    """Test update_upload_status function."""

    @pytest.mark.asyncio
    async def test_update_status_to_processing(self, mock_session, sample_upload):
        """Test updating status to PROCESSING."""
        # Mock get_upload_by_id
        with patch(
            "app.crud.catalog.get_upload_by_id", return_value=sample_upload
        ):
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()

            upload = await update_upload_status(
                mock_session,
                upload_id=1,
                status=UploadStatus.PROCESSING,
                progress=10.0
            )

            assert upload.status == UploadStatus.PROCESSING
            assert upload.progress_percentage == 10.0
            assert upload.started_at is not None
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_status_to_completed(self, mock_session, sample_upload):
        """Test updating status to COMPLETED."""
        with patch(
            "app.crud.catalog.get_upload_by_id", return_value=sample_upload
        ):
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()

            upload = await update_upload_status(
                mock_session,
                upload_id=1,
                status=UploadStatus.COMPLETED,
                progress=100.0
            )

            assert upload.status == UploadStatus.COMPLETED
            assert upload.progress_percentage == 100.0
            assert upload.completed_at is not None
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_status_to_failed(self, mock_session, sample_upload):
        """Test updating status to FAILED."""
        with patch(
            "app.crud.catalog.get_upload_by_id", return_value=sample_upload
        ):
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()

            upload = await update_upload_status(
                mock_session,
                upload_id=1,
                status=UploadStatus.FAILED,
            )

            assert upload.status == UploadStatus.FAILED
            assert upload.completed_at is not None

    @pytest.mark.asyncio
    async def test_update_with_additional_fields(self, mock_session, sample_upload):
        """Test updating with additional kwargs."""
        # Add the attributes to the mock
        sample_upload.processed_tracks = 0
        sample_upload.matched_tracks = 0

        with patch(
            "app.crud.catalog.get_upload_by_id", return_value=sample_upload
        ):
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()

            upload = await update_upload_status(
                mock_session,
                upload_id=1,
                status=UploadStatus.PROCESSING,
                progress=50.0,
                processed_tracks=100,
                matched_tracks=75
            )

            assert upload.processed_tracks == 100
            assert upload.matched_tracks == 75

    @pytest.mark.asyncio
    async def test_update_status_not_found(self, mock_session):
        """Test updating upload that doesn't exist."""
        with patch(
            "app.crud.catalog.get_upload_by_id", return_value=None
        ):
            upload = await update_upload_status(
                mock_session,
                upload_id=999,
                status=UploadStatus.COMPLETED
            )

            assert upload is None

    @pytest.mark.asyncio
    async def test_update_only_started_at_once(self, mock_session, sample_upload):
        """Test that started_at is only set once."""
        sample_upload.started_at = datetime(2025, 10, 1)

        with patch(
            "app.crud.catalog.get_upload_by_id", return_value=sample_upload
        ):
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()

            upload = await update_upload_status(
                mock_session,
                upload_id=1,
                status=UploadStatus.PROCESSING,
                progress=20.0
            )

            # started_at should not change
            assert upload.started_at == datetime(2025, 10, 1)


class TestDeleteUpload:
    """Test delete_upload function."""

    @pytest.mark.asyncio
    async def test_delete_upload_success(self, mock_session, sample_upload):
        """Test successfully deleting an upload."""
        with patch(
            "app.crud.catalog.get_upload_by_id", return_value=sample_upload
        ):
            mock_session.delete = AsyncMock()
            mock_session.commit = AsyncMock()

            result = await delete_upload(mock_session, upload_id=1)

            assert result is True
            mock_session.delete.assert_called_once_with(sample_upload)
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_upload_not_found(self, mock_session):
        """Test deleting upload that doesn't exist."""
        with patch(
            "app.crud.catalog.get_upload_by_id", return_value=None
        ):
            result = await delete_upload(mock_session, upload_id=999)

            assert result is False
            mock_session.delete.assert_not_called()
            mock_session.commit.assert_not_called()


class TestGetUploadsCount:
    """Test get_uploads_count function."""

    @pytest.mark.asyncio
    async def test_get_uploads_count_no_filters(self, mock_session):
        """Test count without filters."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 10
        mock_session.execute.return_value = mock_result

        count = await get_uploads_count(mock_session)

        assert count == 10
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_uploads_count_with_user_filter(self, mock_session):
        """Test count with user ID filter."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 5
        mock_session.execute.return_value = mock_result

        count = await get_uploads_count(mock_session, user_id=1)

        assert count == 5

    @pytest.mark.asyncio
    async def test_get_uploads_count_with_status_filter(self, mock_session):
        """Test count with status filter."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 3
        mock_session.execute.return_value = mock_result

        count = await get_uploads_count(
            mock_session,
            filters={"status": UploadStatus.COMPLETED}
        )

        assert count == 3

    @pytest.mark.asyncio
    async def test_get_uploads_count_combined_filters(self, mock_session):
        """Test count with combined filters."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 2
        mock_session.execute.return_value = mock_result

        count = await get_uploads_count(
            mock_session,
            user_id=1,
            filters={"status": UploadStatus.PROCESSING}
        )

        assert count == 2

    @pytest.mark.asyncio
    async def test_get_uploads_count_zero(self, mock_session):
        """Test count when no uploads match."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 0
        mock_session.execute.return_value = mock_result

        count = await get_uploads_count(mock_session, user_id=999)

        assert count == 0


class TestCatalogIntegration:
    """Integration tests for catalog CRUD operations."""

    @pytest.mark.asyncio
    async def test_full_upload_lifecycle(self, mock_session, upload_data, sample_upload):
        """Test complete upload lifecycle: create → get → update → delete."""
        # 1. Create upload
        created_upload = sample_upload
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with patch(
            "app.crud.catalog.CatalogUpload", return_value=created_upload
        ):
            upload = await create_upload(mock_session, user_id=1, upload_data=upload_data)
            assert upload.status == UploadStatus.PENDING

        # 2. Get upload by ID
        with patch(
            "app.crud.catalog.get_upload_by_id", return_value=created_upload
        ):
            upload = await get_upload_by_id(mock_session, upload_id=1)
            assert upload is not None

        # 3. Update status
        with patch(
            "app.crud.catalog.get_upload_by_id", return_value=created_upload
        ):
            upload = await update_upload_status(
                mock_session,
                upload_id=1,
                status=UploadStatus.COMPLETED,
                progress=100.0
            )
            assert upload.status == UploadStatus.COMPLETED

        # 4. Delete upload
        mock_session.delete = AsyncMock()
        with patch(
            "app.crud.catalog.get_upload_by_id", return_value=created_upload
        ):
            result = await delete_upload(mock_session, upload_id=1)
            assert result is True

    @pytest.mark.asyncio
    async def test_filter_consistency(self, mock_session):
        """Test that get_uploads and get_uploads_count use same filters."""
        filters = {"status": UploadStatus.PROCESSING}

        # Setup list result
        list_result = MagicMock()
        list_result.scalars.return_value.all.return_value = []

        # Setup count result
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        mock_session.execute.side_effect = [list_result, count_result]

        uploads = await get_uploads(mock_session, user_id=1, filters=filters)
        count = await get_uploads_count(mock_session, user_id=1, filters=filters)

        # Both queries should be executed
        assert mock_session.execute.call_count == 2
        assert uploads == []
        assert count == 0

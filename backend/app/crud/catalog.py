"""CRUD operations for CatalogUpload entities."""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog_upload import CatalogUpload, UploadStatus


async def create_upload(
    session: AsyncSession, user_id: int, upload_data: Dict
) -> CatalogUpload:
    """Create a new catalog upload record.

    Args:
        session: Database session
        user_id: User ID creating the upload
        upload_data: Upload metadata (filename, file_format, etc.)

    Returns:
        Created CatalogUpload object
    """
    upload = CatalogUpload(
        user_id=user_id,
        filename=upload_data["filename"],
        file_format=upload_data["file_format"],
        file_size_bytes=upload_data["file_size_bytes"],
        publisher_name=upload_data["publisher_name"],
        status=UploadStatus.PENDING,
        progress_percentage=0.0,
    )

    session.add(upload)
    await session.commit()
    await session.refresh(upload)

    return upload


async def get_uploads(
    session: AsyncSession,
    user_id: Optional[int] = None,
    filters: Optional[Dict] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[CatalogUpload]:
    """Get paginated list of catalog uploads.

    Args:
        session: Database session
        user_id: Filter by user ID (None for admin to see all)
        filters: Optional filters (status, etc.)
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of CatalogUpload objects
    """
    query = select(CatalogUpload)

    # Filter by user if provided
    if user_id is not None:
        query = query.where(CatalogUpload.user_id == user_id)

    # Apply filters
    if filters:
        if filters.get("status"):
            query = query.where(CatalogUpload.status == filters["status"])

    # Order by created_at descending
    query = query.order_by(CatalogUpload.created_at.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_upload_by_id(
    session: AsyncSession, upload_id: int
) -> Optional[CatalogUpload]:
    """Get a catalog upload by ID.

    Args:
        session: Database session
        upload_id: Upload ID

    Returns:
        CatalogUpload object or None if not found
    """
    query = select(CatalogUpload).where(CatalogUpload.id == upload_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def update_upload_status(
    session: AsyncSession,
    upload_id: int,
    status: UploadStatus,
    progress: Optional[float] = None,
    **kwargs,
) -> Optional[CatalogUpload]:
    """Update upload status and progress.

    Args:
        session: Database session
        upload_id: Upload ID
        status: New status
        progress: Progress percentage (0-100)
        **kwargs: Additional fields to update (processed_tracks, matched_tracks, etc.)

    Returns:
        Updated CatalogUpload object or None if not found
    """
    upload = await get_upload_by_id(session, upload_id)
    if not upload:
        return None

    upload.status = status
    if progress is not None:
        upload.progress_percentage = progress

    # Update timestamps
    if status == UploadStatus.PROCESSING and upload.started_at is None:
        upload.started_at = datetime.utcnow()
    elif status in [UploadStatus.COMPLETED, UploadStatus.FAILED]:
        upload.completed_at = datetime.utcnow()

    # Update additional fields
    for key, value in kwargs.items():
        if hasattr(upload, key):
            setattr(upload, key, value)

    await session.commit()
    await session.refresh(upload)

    return upload


async def delete_upload(session: AsyncSession, upload_id: int) -> bool:
    """Delete a catalog upload.

    Args:
        session: Database session
        upload_id: Upload ID

    Returns:
        True if deleted, False if not found
    """
    upload = await get_upload_by_id(session, upload_id)
    if not upload:
        return False

    await session.delete(upload)
    await session.commit()

    return True


async def get_uploads_count(
    session: AsyncSession, user_id: Optional[int] = None, filters: Optional[Dict] = None
) -> int:
    """Get total count of uploads matching filters.

    Args:
        session: Database session
        user_id: Filter by user ID
        filters: Optional filters

    Returns:
        Total count of matching uploads
    """
    query = select(func.count(CatalogUpload.id))

    if user_id is not None:
        query = query.where(CatalogUpload.user_id == user_id)

    if filters and filters.get("status"):
        query = query.where(CatalogUpload.status == filters["status"])

    result = await session.execute(query)
    return result.scalar_one()

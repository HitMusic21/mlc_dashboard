"""
Celery tasks for cleanup operations.
"""
import asyncio
from datetime import datetime, timedelta

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import async_session_maker
from app.models.catalog import CatalogUpload, UploadStatus
from app.services.cache import cache_service


async def _cleanup_old_uploads_async() -> dict:
    """
    Clean up old uploads (older than 30 days).
    Deletes uploads in 'completed' or 'failed' status that are older than 30 days.

    Returns:
        dict: Statistics about cleanup operation
    """
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    deleted_count = 0

    async with async_session_maker() as session:
        # Find old uploads to delete
        statement = select(CatalogUpload).where(
            CatalogUpload.created_at < cutoff_date,
            CatalogUpload.status.in_([UploadStatus.COMPLETED, UploadStatus.FAILED]),
        )
        result = await session.execute(statement)
        old_uploads = result.scalars().all()

        # Delete old uploads
        for upload in old_uploads:
            await session.delete(upload)
            deleted_count += 1

        await session.commit()

    return {
        "task": "cleanup_old_uploads",
        "deleted_count": deleted_count,
        "cutoff_date": cutoff_date.isoformat(),
        "status": "success",
    }


async def _cleanup_cache_async() -> dict:
    """
    Clean up expired cache entries.
    Redis handles TTL automatically, but this task can be used for additional cleanup.

    Returns:
        dict: Statistics about cleanup operation
    """
    # Redis automatically evicts expired keys
    # This task can be used for custom cleanup logic if needed

    # For now, just report that cache is using Redis TTL
    return {
        "task": "cleanup_cache",
        "status": "success",
        "message": "Redis handles cache expiry automatically via TTL",
    }


def cleanup_old_uploads():
    """
    Celery task to clean up old uploads.
    Run daily via celery beat.
    """
    from celery_app import celery_app

    @celery_app.task(name="app.tasks.cleanup.cleanup_old_uploads", bind=True)
    def task(self):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_cleanup_old_uploads_async())
        return result

    return task


def cleanup_cache():
    """
    Celery task to clean up cache.
    Run hourly via celery beat.
    """
    from celery_app import celery_app

    @celery_app.task(name="app.tasks.cleanup.cleanup_cache", bind=True)
    def task(self):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(_cleanup_cache_async())
        return result

    return task


# Register tasks
cleanup_old_uploads_task = cleanup_old_uploads()
cleanup_cache_task = cleanup_cache()

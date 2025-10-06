"""Celery task for processing uploaded music catalogs."""

import logging
from datetime import datetime
from typing import Callable, List, Optional

from celery import Task
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.catalog import get_upload_by_id, update_upload_status
from app.crud.matches import bulk_create_matches
from app.crud.works import get_all_works
from app.db.session import AsyncSessionLocal
from app.models.catalog_upload import CatalogUpload, UploadStatus
from app.services.matching.engine import MatchingEngine
from app.services.parsers.csv_parser import CSVParser
from app.services.parsers.excel_parser import ExcelParser
from app.services.parsers.json_parser import JSONParser
from app.services.parsers.xml_parser import XMLParser

logger = logging.getLogger(__name__)


class CatalogProcessingTask(Task):
    """Custom Celery task for catalog processing with retries."""

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3, "countdown": 60}  # Retry with 60s delay
    retry_backoff = True
    retry_backoff_max = 600  # Max 10 minutes
    retry_jitter = True


async def _process_catalog_async(
    upload_id: int, file_content: bytes, filename: str, file_format: str
) -> dict:
    """Process catalog asynchronously (actual implementation).

    Args:
        upload_id: ID of catalog upload
        file_content: Binary file content
        filename: Original filename
        file_format: File format (csv, excel, json, xml)

    Returns:
        Processing statistics
    """
    session: Optional[AsyncSession] = None
    start_time = datetime.utcnow()

    try:
        # Get database session
        session = AsyncSessionLocal()

        # Update status to processing
        await update_upload_status(
            session,
            upload_id,
            UploadStatus.PROCESSING,
            progress_percentage=0,
            status_message="Starting catalog processing...",
        )
        await session.commit()

        logger.info(f"Starting processing for upload {upload_id}")

        # Parse file based on format
        parser = _get_parser(file_format)
        if not parser:
            raise ValueError(f"Unsupported file format: {file_format}")

        tracks = parser.parse(file_content, filename)
        total_tracks = len(tracks)

        logger.info(f"Parsed {total_tracks} tracks from {filename}")

        # Update progress
        await update_upload_status(
            session,
            upload_id,
            UploadStatus.PROCESSING,
            progress_percentage=10,
            status_message=f"Parsed {total_tracks} tracks, starting matching...",
        )
        await session.commit()

        # Initialize matching engine
        engine = MatchingEngine()
        await engine.initialize(session)

        # Progress callback for real-time updates
        async def progress_callback(
            progress: float, processed: int, total: int
        ) -> None:
            """Update progress in database."""
            # Calculate progress: 10% for parsing, 80% for matching, 10% for saving
            match_progress = 10 + (progress * 0.8)

            await update_upload_status(
                session,
                upload_id,
                UploadStatus.PROCESSING,
                progress_percentage=match_progress,
                status_message=f"Matching: {processed}/{total} tracks processed",
            )
            await session.commit()

        # Match catalog against BWARM works
        matches = await engine.match_catalog(upload_id, tracks, progress_callback)

        logger.info(f"Generated {len(matches)} matches for {total_tracks} tracks")

        # Update progress for database save
        await update_upload_status(
            session,
            upload_id,
            UploadStatus.PROCESSING,
            progress_percentage=90,
            status_message="Saving matches to database...",
        )
        await session.commit()

        # Save matches to database
        saved_matches = await bulk_create_matches(session, matches)
        await session.commit()

        # Calculate statistics
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()

        # Count matches by confidence
        high_confidence = sum(
            1 for m in matches if m.get("confidence_level") == "high"
        )
        medium_confidence = sum(
            1 for m in matches if m.get("confidence_level") == "medium"
        )
        low_confidence = sum(
            1 for m in matches if m.get("confidence_level") == "low"
        )

        stats = {
            "total_tracks": total_tracks,
            "total_matches": len(matches),
            "high_confidence_matches": high_confidence,
            "medium_confidence_matches": medium_confidence,
            "low_confidence_matches": low_confidence,
            "processing_time_seconds": processing_time,
            "throughput": total_tracks / processing_time if processing_time > 0 else 0,
        }

        # Update status to completed
        await update_upload_status(
            session,
            upload_id,
            UploadStatus.COMPLETED,
            progress_percentage=100,
            status_message=f"Completed: {len(matches)} matches found",
            processing_stats=stats,
        )
        await session.commit()

        logger.info(
            f"Completed processing for upload {upload_id}: {stats['total_matches']} matches in {processing_time:.2f}s"
        )

        return stats

    except Exception as e:
        logger.error(f"Error processing upload {upload_id}: {e}", exc_info=True)

        # Update status to failed
        if session:
            try:
                await update_upload_status(
                    session,
                    upload_id,
                    UploadStatus.FAILED,
                    status_message=f"Processing failed: {str(e)}",
                )
                await session.commit()
            except Exception as update_error:
                logger.error(f"Failed to update upload status: {update_error}")

        raise

    finally:
        if session:
            await session.close()


def _get_parser(file_format: str):
    """Get appropriate parser for file format.

    Args:
        file_format: File format string

    Returns:
        Parser instance or None
    """
    parsers = {
        "csv": CSVParser(),
        "excel": ExcelParser(),
        "json": JSONParser(),
        "xml": XMLParser(),
    }
    return parsers.get(file_format.lower())


# Import Celery app and create task
from celery_app import celery_app


@celery_app.task(base=CatalogProcessingTask, bind=True)
def process_catalog(
    self, upload_id: int, file_content: bytes, filename: str, file_format: str
):
    """Celery task wrapper for catalog processing.

    This task processes an uploaded catalog file asynchronously:
    1. Parses the file based on format (CSV/Excel/JSON/XML)
    2. Matches tracks against existing musical works
    3. Stores match results
    4. Updates upload status

    Args:
        self: Celery task instance
        upload_id: ID of the catalog upload
        file_content: Binary file content
        filename: Original filename
        file_format: File format (csv, excel, json, xml)

    Returns:
        dict: Processing statistics (tracks_found, matches_created, etc.)
    """
    import asyncio

    logger.info(
        f"Starting catalog processing task for upload_id={upload_id}, "
        f"filename={filename}, format={file_format}"
    )

    try:
        # Run the async processing function
        result = asyncio.run(
            _process_catalog_async(upload_id, file_content, filename, file_format)
        )
        logger.info(f"Catalog processing completed for upload_id={upload_id}: {result}")
        return result
    except Exception as e:
        logger.error(f"Catalog processing failed for upload_id={upload_id}: {e}")
        raise

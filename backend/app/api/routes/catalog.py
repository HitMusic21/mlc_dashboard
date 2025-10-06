"""Catalog API routes."""

from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user, get_upload_owner
from app.core.config import settings
from app.crud import notifications as notifications_crud
from app.crud.catalog import (
    create_upload,
    delete_upload,
    get_uploads,
    get_uploads_count,
)
from app.crud.matches import get_matches_grouped
from app.db.session import get_session
from app.models.catalog_upload import CatalogUpload, FileFormat
from app.models.notification import NotificationSeverity, NotificationType
from app.models.user import User, UserRole
from app.schemas.catalog import (
    CatalogResultsResponse,
    CatalogUploadResponse,
    CatalogUploadStatusResponse,
    CatalogUploadsListResponse,
)
from app.schemas.works import Pagination

router = APIRouter(prefix="/catalog", tags=["Catalog"])


@router.post("/upload", response_model=CatalogUploadResponse, status_code=201)
async def upload_catalog(
    file: UploadFile = File(...),
    publisher_name: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Upload a catalog file for matching.

    Args:
        file: Catalog file (CSV, Excel, JSON, XML)
        publisher_name: Publisher name
        current_user: Current authenticated user
        session: Database session

    Returns:
        CatalogUploadResponse with upload details
    """
    # Validate file extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )

    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in settings.ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_FILE_EXTENSIONS)}",
        )

    # Read file content
    file_content = await file.read()
    file_size = len(file_content)

    # Check file size
    if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Map extension to format
    format_map = {
        "csv": FileFormat.CSV,
        "xlsx": FileFormat.EXCEL,
        "xls": FileFormat.EXCEL,
        "json": FileFormat.JSON,
        "xml": FileFormat.XML,
    }
    file_format = format_map.get(file_ext)

    # Create upload record
    upload_data = {
        "filename": file.filename,
        "file_format": file_format,
        "file_size_bytes": file_size,
        "publisher_name": publisher_name,
    }

    upload = await create_upload(session, current_user.id, upload_data)

    # Create notification for successful upload
    await notifications_crud.create_notification(
        session,
        {
            "user_id": current_user.id,
            "type": NotificationType.SUCCESS,
            "severity": NotificationSeverity.LOW,
            "title": "Catalog Upload Started",
            "message": f"Your catalog '{file.filename}' has been uploaded and is being processed.",
            "related_entity_type": "catalog_upload",
            "related_entity_id": upload.id,
            "action_url": f"/catalog/{upload.id}/status",
        },
    )

    # Trigger Celery task to process catalog asynchronously
    from app.tasks.catalog_processing import process_catalog

    process_catalog.delay(
        upload_id=upload.id,
        file_content=file_content,
        filename=file.filename,
        file_format=upload.file_format,
    )

    return upload


@router.get("/uploads", response_model=CatalogUploadsListResponse)
async def list_uploads(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=1000),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """List catalog uploads.

    Publishers see only their uploads, admins see all.

    Args:
        page: Page number
        limit: Items per page
        status: Filter by status
        current_user: Current authenticated user
        session: Database session

    Returns:
        CatalogUploadsListResponse with paginated uploads
    """
    # Admin sees all, publisher sees only their own
    user_id = None if current_user.role == UserRole.ADMIN else current_user.id

    # Build filters
    filters = {}
    if status:
        filters["status"] = status

    # Get uploads
    skip = (page - 1) * limit
    uploads = await get_uploads(
        session, user_id=user_id, filters=filters, skip=skip, limit=limit
    )

    # Get total count
    total_count = await get_uploads_count(session, user_id=user_id, filters=filters)

    # Calculate pagination
    total_pages = (total_count + limit - 1) // limit

    return CatalogUploadsListResponse(
        data=uploads,
        pagination=Pagination(
            page=page,
            limit=limit,
            total_items=total_count,
            total_pages=total_pages,
        ),
    )


@router.get("/{upload_id}/status", response_model=CatalogUploadStatusResponse)
async def get_upload_status(
    upload: CatalogUpload = Depends(get_upload_owner),
):
    """Get upload processing status.

    Args:
        upload: Catalog upload (verified by dependency)

    Returns:
        CatalogUploadStatusResponse with status and progress
    """
    return upload


@router.get("/{upload_id}/results", response_model=CatalogResultsResponse)
async def get_upload_results(
    upload_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    confidence: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=1),
    upload: CatalogUpload = Depends(get_upload_owner),
    session: AsyncSession = Depends(get_session),
):
    """Get matching results for an upload.

    Args:
        upload_id: Upload ID
        page: Page number
        limit: Items per page
        confidence: Filter by confidence level
        min_score: Minimum match score
        upload: Catalog upload (verified by dependency)
        session: Database session

    Returns:
        CatalogResultsResponse with match results
    """
    # Build filters
    filters = {}
    if confidence:
        filters["confidence"] = confidence
    if min_score:
        filters["min_score"] = min_score

    # Get matches grouped by uploaded track
    match_groups = await get_matches_grouped(session, upload_id, filters)

    # Apply pagination
    skip = (page - 1) * limit
    paginated_groups = match_groups[skip : skip + limit]

    total_pages = (len(match_groups) + limit - 1) // limit

    return CatalogResultsResponse(
        data=paginated_groups,
        pagination=Pagination(
            page=page,
            limit=limit,
            total_items=len(match_groups),
            total_pages=total_pages,
        ),
    )


@router.delete("/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload_endpoint(
    upload_id: int,
    upload: CatalogUpload = Depends(get_upload_owner),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Delete a catalog upload and its matches.

    Args:
        upload_id: Upload ID
        upload: Catalog upload (verified by dependency)
        current_user: Current authenticated user
        session: Database session
    """
    # Store filename before deletion
    filename = upload.filename

    success = await delete_upload(session, upload_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found",
        )

    # Create notification for deletion
    await notifications_crud.create_notification(
        session,
        {
            "user_id": current_user.id,
            "type": NotificationType.INFO,
            "severity": NotificationSeverity.LOW,
            "title": "Catalog Deleted",
            "message": f"Your catalog '{filename}' has been deleted along with all associated matches.",
            "related_entity_type": "catalog_upload",
            "related_entity_id": upload_id,
        },
    )

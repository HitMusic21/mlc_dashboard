"""Admin API routes for managing all users' resources."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_admin
from app.crud.catalog import delete_upload, get_uploads, get_uploads_count
from app.crud.user import get_all_users, get_users_count
from app.db.session import get_session
from app.models.user import User
from app.schemas.catalog import CatalogUploadsListResponse
from app.schemas.works import Pagination

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/uploads", response_model=CatalogUploadsListResponse)
async def list_all_uploads(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=1000),
    status: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """List all catalog uploads across all users (admin only).

    Args:
        page: Page number
        limit: Items per page
        status: Filter by status
        user_id: Filter by specific user
        current_user: Current authenticated admin user
        session: Database session

    Returns:
        CatalogUploadsListResponse with all uploads
    """
    # Build filters
    filters = {}
    if status:
        filters["status"] = status

    # Get uploads (user_id=None means all users, or specific user if provided)
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


@router.delete("/uploads/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_any_upload(
    upload_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Delete any catalog upload (admin only).

    Admins can delete uploads from any user.

    Args:
        upload_id: Upload ID to delete
        current_user: Current authenticated admin user
        session: Database session
    """
    success = await delete_upload(session, upload_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload not found",
        )


@router.get("/users")
async def list_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=1000),
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """List all users in the system (admin only).

    Args:
        page: Page number
        limit: Items per page
        role: Filter by role (publisher, admin)
        is_active: Filter by active status
        current_user: Current authenticated admin user
        session: Database session

    Returns:
        Paginated list of users
    """
    # Build filters
    filters = {}
    if role:
        filters["role"] = role
    if is_active is not None:
        filters["is_active"] = is_active

    # Get users
    skip = (page - 1) * limit
    users = await get_all_users(session, filters=filters, skip=skip, limit=limit)

    # Get total count
    total_count = await get_users_count(session, filters=filters)

    # Calculate pagination
    total_pages = (total_count + limit - 1) // limit

    # Format response
    users_data = []
    for user in users:
        users_data.append(
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login_at.isoformat() if user.last_login_at else None,
            }
        )

    return {
        "data": users_data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_items": total_count,
            "total_pages": total_pages,
        },
    }


@router.get("/statistics")
async def get_admin_statistics(
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    """Get system-wide statistics (admin only).

    Returns aggregated statistics about users, uploads, and matches.

    Args:
        current_user: Current authenticated admin user
        session: Database session

    Returns:
        System-wide statistics
    """
    from sqlalchemy import func, select

    from app.models.catalog_match import CatalogMatch
    from app.models.catalog_upload import CatalogUpload
    from app.models.musical_work import MusicalWork
    from app.models.user import User, UserRole

    # Count users by role
    publisher_count_query = select(func.count()).select_from(User).where(User.role == UserRole.PUBLISHER)
    admin_count_query = select(func.count()).select_from(User).where(User.role == UserRole.ADMIN)

    publisher_count = await session.scalar(publisher_count_query)
    admin_count = await session.scalar(admin_count_query)

    # Count uploads by status
    from app.models.catalog_upload import UploadStatus

    completed_uploads_query = (
        select(func.count())
        .select_from(CatalogUpload)
        .where(CatalogUpload.status == UploadStatus.COMPLETED)
    )
    processing_uploads_query = (
        select(func.count())
        .select_from(CatalogUpload)
        .where(CatalogUpload.status == UploadStatus.PROCESSING)
    )
    failed_uploads_query = (
        select(func.count())
        .select_from(CatalogUpload)
        .where(CatalogUpload.status == UploadStatus.FAILED)
    )

    completed_uploads = await session.scalar(completed_uploads_query)
    processing_uploads = await session.scalar(processing_uploads_query)
    failed_uploads = await session.scalar(failed_uploads_query)

    # Count total works and matches
    total_works_query = select(func.count()).select_from(MusicalWork)
    total_matches_query = select(func.count()).select_from(CatalogMatch)

    total_works = await session.scalar(total_works_query)
    total_matches = await session.scalar(total_matches_query)

    return {
        "users": {
            "total": (publisher_count or 0) + (admin_count or 0),
            "publishers": publisher_count or 0,
            "admins": admin_count or 0,
        },
        "uploads": {
            "total": (
                (completed_uploads or 0)
                + (processing_uploads or 0)
                + (failed_uploads or 0)
            ),
            "completed": completed_uploads or 0,
            "processing": processing_uploads or 0,
            "failed": failed_uploads or 0,
        },
        "catalog": {
            "total_works": total_works or 0,
            "total_matches": total_matches or 0,
        },
    }

"""Saved searches API routes."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.crud import saved_search as saved_search_crud
from app.db.session import get_session
from app.models.user import User
from app.schemas.saved_search import (
    SavedSearchCreate,
    SavedSearchListResponse,
    SavedSearchResponse,
    SavedSearchUpdate,
)

router = APIRouter(prefix="/saved-searches", tags=["Saved Searches"])


@router.post("", response_model=SavedSearchResponse, status_code=status.HTTP_201_CREATED)
async def create_saved_search(
    search_data: SavedSearchCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Create a new saved search.

    Args:
        search_data: Saved search configuration
        current_user: Authenticated user
        session: Database session

    Returns:
        Created SavedSearchResponse

    Raises:
        HTTPException: 400 if validation fails
    """
    saved_search = await saved_search_crud.create_saved_search(
        session, current_user.id, search_data
    )
    return saved_search


@router.get("", response_model=SavedSearchListResponse)
async def get_saved_searches(
    include_presets: bool = Query(True, description="Include system presets"),
    favorites_only: bool = Query(False, description="Only return favorites"),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Get all saved searches for the current user.

    Args:
        include_presets: Include system preset searches
        favorites_only: Only return favorite searches
        current_user: Authenticated user
        session: Database session

    Returns:
        SavedSearchListResponse with list of searches and total count
    """
    searches = await saved_search_crud.get_user_saved_searches(
        session,
        current_user.id,
        include_presets=include_presets,
        favorites_only=favorites_only,
    )

    return SavedSearchListResponse(total=len(searches), searches=searches)


@router.get("/presets", response_model=List[SavedSearchResponse])
async def get_system_presets(
    session: AsyncSession = Depends(get_session),
):
    """Get all system preset searches.

    Args:
        session: Database session

    Returns:
        List of preset SavedSearchResponse objects
    """
    presets = await saved_search_crud.get_system_presets(session)
    return presets


@router.get("/{search_id}", response_model=SavedSearchResponse)
async def get_saved_search(
    search_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Get a specific saved search by ID.

    Args:
        search_id: Search ID
        current_user: Authenticated user
        session: Database session

    Returns:
        SavedSearchResponse

    Raises:
        HTTPException: 404 if search not found or access denied
    """
    saved_search = await saved_search_crud.get_saved_search(
        session, search_id, current_user.id
    )

    if not saved_search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved search not found",
        )

    return saved_search


@router.put("/{search_id}", response_model=SavedSearchResponse)
async def update_saved_search(
    search_id: int,
    update_data: SavedSearchUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Update a saved search.

    Args:
        search_id: Search ID
        update_data: Fields to update
        current_user: Authenticated user
        session: Database session

    Returns:
        Updated SavedSearchResponse

    Raises:
        HTTPException: 404 if search not found or access denied
    """
    saved_search = await saved_search_crud.update_saved_search(
        session, search_id, current_user.id, update_data
    )

    if not saved_search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved search not found",
        )

    return saved_search


@router.delete("/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_search(
    search_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Delete a saved search.

    Args:
        search_id: Search ID
        current_user: Authenticated user
        session: Database session

    Raises:
        HTTPException: 404 if search not found or access denied
    """
    deleted = await saved_search_crud.delete_saved_search(
        session, search_id, current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved search not found",
        )


@router.post("/{search_id}/use", response_model=SavedSearchResponse)
async def record_search_use(
    search_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Record usage of a saved search (updates last_used_at and use_count).

    Args:
        search_id: Search ID
        current_user: Authenticated user
        session: Database session

    Returns:
        Updated SavedSearchResponse

    Raises:
        HTTPException: 404 if search not found or access denied
    """
    saved_search = await saved_search_crud.record_search_use(
        session, search_id, current_user.id
    )

    if not saved_search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved search not found",
        )

    return saved_search


@router.post("/bulk-delete", status_code=status.HTTP_200_OK)
async def bulk_delete_searches(
    search_ids: List[int],
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Delete multiple saved searches.

    Args:
        search_ids: List of search IDs to delete
        current_user: Authenticated user
        session: Database session

    Returns:
        Dictionary with count of deleted searches

    Raises:
        HTTPException: 400 if no search IDs provided
    """
    if not search_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No search IDs provided",
        )

    deleted_count = await saved_search_crud.bulk_delete_searches(
        session, search_ids, current_user.id
    )

    return {"deleted_count": deleted_count, "total_requested": len(search_ids)}

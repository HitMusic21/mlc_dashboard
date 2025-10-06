"""User preferences API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.crud import preferences as preferences_crud
from app.db.session import get_session
from app.models.user import User
from app.schemas.preferences import (
    LayoutUpdateRequest,
    SavedSearchCreateRequest,
    UserPreferencesResponse,
    UserPreferencesUpdate,
)

router = APIRouter(prefix="/preferences", tags=["User Preferences"])


@router.get("", response_model=UserPreferencesResponse)
async def get_user_preferences(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Get current user's preferences.

    Returns default preferences if none exist.

    Args:
        current_user: Authenticated user
        session: Database session

    Returns:
        UserPreferencesResponse with all preference settings
    """
    prefs = await preferences_crud.get_or_create_preferences(session, current_user.id)
    return prefs


@router.put("", response_model=UserPreferencesResponse)
async def update_user_preferences(
    updates: UserPreferencesUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Update current user's preferences.

    Supports partial updates - only provided fields will be updated.

    Args:
        updates: Fields to update
        current_user: Authenticated user
        session: Database session

    Returns:
        Updated UserPreferencesResponse

    Raises:
        HTTPException: 422 if validation fails
    """
    # Convert Pydantic model to dict, excluding unset fields
    update_data = updates.model_dump(exclude_unset=True)

    prefs = await preferences_crud.upsert_preferences(
        session, current_user.id, update_data
    )
    return prefs


@router.post("/layout", response_model=UserPreferencesResponse)
async def update_dashboard_layout(
    request: LayoutUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Update user's dashboard layout configuration.

    Args:
        request: Dashboard layout configuration
        current_user: Authenticated user
        session: Database session

    Returns:
        Updated UserPreferencesResponse with new layout
    """
    prefs = await preferences_crud.update_dashboard_layout(
        session, current_user.id, request.layout
    )
    return prefs


@router.post("/searches", response_model=UserPreferencesResponse)
async def save_search(
    request: SavedSearchCreateRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Save a new search filter configuration.

    Args:
        request: Saved search configuration
        current_user: Authenticated user
        session: Database session

    Returns:
        Updated UserPreferencesResponse with new saved search

    Raises:
        HTTPException: 400 if search name already exists
    """
    try:
        prefs = await preferences_crud.add_saved_search(
            session, current_user.id, request
        )
        return prefs
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/searches/{search_id}", response_model=UserPreferencesResponse)
async def delete_saved_search(
    search_id: str,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Delete a saved search by ID.

    Args:
        search_id: ID of the saved search to delete
        current_user: Authenticated user
        session: Database session

    Returns:
        Updated UserPreferencesResponse without the deleted search

    Raises:
        HTTPException: 404 if search ID not found
    """
    try:
        prefs = await preferences_crud.remove_saved_search(
            session, current_user.id, search_id
        )
        return prefs
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

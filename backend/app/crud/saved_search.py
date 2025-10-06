"""CRUD operations for SavedSearch entities."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.saved_search import SavedSearch
from app.schemas.saved_search import SavedSearchCreate, SavedSearchUpdate


async def create_saved_search(
    session: AsyncSession, user_id: int, search_data: SavedSearchCreate
) -> SavedSearch:
    """Create a new saved search.

    Args:
        session: Database session
        user_id: User ID who owns the search
        search_data: Search creation data

    Returns:
        Created SavedSearch object
    """
    saved_search = SavedSearch(
        user_id=user_id,
        name=search_data.name,
        description=search_data.description,
        filter_config=search_data.filter_config.model_dump(),
        is_favorite=search_data.is_favorite,
    )

    session.add(saved_search)
    await session.commit()
    await session.refresh(saved_search)

    return saved_search


async def get_saved_search(
    session: AsyncSession, search_id: int, user_id: int
) -> Optional[SavedSearch]:
    """Get a saved search by ID.

    Args:
        session: Database session
        search_id: Search ID
        user_id: User ID (for access control)

    Returns:
        SavedSearch object or None if not found/not authorized
    """
    query = select(SavedSearch).where(
        SavedSearch.id == search_id, SavedSearch.user_id == user_id
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_user_saved_searches(
    session: AsyncSession,
    user_id: int,
    include_presets: bool = True,
    favorites_only: bool = False,
) -> List[SavedSearch]:
    """Get all saved searches for a user.

    Args:
        session: Database session
        user_id: User ID
        include_presets: Include system presets
        favorites_only: Only return favorites

    Returns:
        List of SavedSearch objects
    """
    query = select(SavedSearch).where(SavedSearch.user_id == user_id)

    if not include_presets:
        query = query.where(SavedSearch.is_preset == False)  # noqa: E712

    if favorites_only:
        query = query.where(SavedSearch.is_favorite == True)  # noqa: E712

    query = query.order_by(desc(SavedSearch.is_favorite), desc(SavedSearch.last_used_at))

    result = await session.execute(query)
    return list(result.scalars().all())


async def update_saved_search(
    session: AsyncSession,
    search_id: int,
    user_id: int,
    update_data: SavedSearchUpdate,
) -> Optional[SavedSearch]:
    """Update a saved search.

    Args:
        session: Database session
        search_id: Search ID
        user_id: User ID (for access control)
        update_data: Fields to update

    Returns:
        Updated SavedSearch object or None if not found/not authorized
    """
    saved_search = await get_saved_search(session, search_id, user_id)

    if not saved_search:
        return None

    # Update only provided fields
    update_dict = update_data.model_dump(exclude_unset=True)

    # Convert filter_config to dict if provided
    if "filter_config" in update_dict and update_dict["filter_config"] is not None:
        update_dict["filter_config"] = update_dict["filter_config"].model_dump()

    for key, value in update_dict.items():
        setattr(saved_search, key, value)

    await session.commit()
    await session.refresh(saved_search)

    return saved_search


async def delete_saved_search(
    session: AsyncSession, search_id: int, user_id: int
) -> bool:
    """Delete a saved search.

    Args:
        session: Database session
        search_id: Search ID
        user_id: User ID (for access control)

    Returns:
        True if deleted, False if not found/not authorized
    """
    saved_search = await get_saved_search(session, search_id, user_id)

    if not saved_search:
        return False

    await session.delete(saved_search)
    await session.commit()

    return True


async def record_search_use(
    session: AsyncSession, search_id: int, user_id: int
) -> Optional[SavedSearch]:
    """Record usage of a saved search (update last_used_at and use_count).

    Args:
        session: Database session
        search_id: Search ID
        user_id: User ID (for access control)

    Returns:
        Updated SavedSearch object or None if not found/not authorized
    """
    saved_search = await get_saved_search(session, search_id, user_id)

    if not saved_search:
        return None

    saved_search.last_used_at = datetime.utcnow()
    saved_search.use_count += 1

    await session.commit()
    await session.refresh(saved_search)

    return saved_search


async def get_system_presets(session: AsyncSession) -> List[SavedSearch]:
    """Get all system preset searches.

    Args:
        session: Database session

    Returns:
        List of preset SavedSearch objects
    """
    query = select(SavedSearch).where(SavedSearch.is_preset == True)  # noqa: E712
    query = query.order_by(SavedSearch.name)

    result = await session.execute(query)
    return list(result.scalars().all())


async def bulk_delete_searches(
    session: AsyncSession, search_ids: List[int], user_id: int
) -> int:
    """Delete multiple saved searches.

    Args:
        session: Database session
        search_ids: List of search IDs to delete
        user_id: User ID (for access control)

    Returns:
        Number of searches deleted
    """
    deleted_count = 0

    for search_id in search_ids:
        if await delete_saved_search(session, search_id, user_id):
            deleted_count += 1

    return deleted_count

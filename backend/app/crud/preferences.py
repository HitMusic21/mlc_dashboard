"""CRUD operations for UserPreferences entities."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_preferences import ThemeEnum, UserPreferences
from app.schemas.preferences import DashboardLayoutConfig, SavedSearchSchema


async def get_preferences(
    session: AsyncSession, user_id: int
) -> Optional[UserPreferences]:
    """Get user preferences by user ID.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        UserPreferences object or None if not found
    """
    query = select(UserPreferences).where(UserPreferences.user_id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_or_create_preferences(
    session: AsyncSession, user_id: int
) -> UserPreferences:
    """Get user preferences or create defaults if they don't exist.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        UserPreferences object (existing or newly created)
    """
    preferences = await get_preferences(session, user_id)

    if not preferences:
        # Create default preferences
        preferences = UserPreferences(
            user_id=user_id,
            theme=ThemeEnum.LIGHT,
            items_per_page=50,
            notification_email=True,
            notification_push=True,
            language="en",
        )
        session.add(preferences)
        await session.commit()
        await session.refresh(preferences)

    return preferences


async def upsert_preferences(
    session: AsyncSession, user_id: int, update_data: dict
) -> UserPreferences:
    """Update user preferences or create if they don't exist.

    Args:
        session: Database session
        user_id: User ID
        update_data: Fields to update

    Returns:
        Updated UserPreferences object
    """
    preferences = await get_preferences(session, user_id)

    if not preferences:
        # Create new preferences with provided data
        preferences = UserPreferences(user_id=user_id, **update_data)
        session.add(preferences)
    else:
        # Update existing preferences
        for key, value in update_data.items():
            if hasattr(preferences, key) and key not in ["id", "user_id"]:
                setattr(preferences, key, value)

    await session.commit()
    await session.refresh(preferences)

    return preferences


async def update_dashboard_layout(
    session: AsyncSession, user_id: int, layout_config: DashboardLayoutConfig
) -> UserPreferences:
    """Update user's dashboard layout configuration.

    Args:
        session: Database session
        user_id: User ID
        layout_config: Dashboard layout configuration

    Returns:
        Updated UserPreferences object
    """
    preferences = await get_or_create_preferences(session, user_id)

    # Convert Pydantic model to dict for JSONB storage
    preferences.dashboard_layout = layout_config.model_dump()

    await session.commit()
    await session.refresh(preferences)

    return preferences


async def add_saved_search(
    session: AsyncSession, user_id: int, search: SavedSearchSchema
) -> UserPreferences:
    """Add a saved search to user preferences.

    Args:
        session: Database session
        user_id: User ID
        search: Saved search configuration

    Returns:
        Updated UserPreferences object

    Raises:
        ValueError: If a search with the same name already exists
    """
    preferences = await get_or_create_preferences(session, user_id)

    # Initialize saved_searches if None
    if preferences.saved_searches is None:
        preferences.saved_searches = []

    # Check for duplicate names
    existing_names = [s.get("name") for s in preferences.saved_searches]
    if search.name in existing_names:
        raise ValueError(f"A saved search with name '{search.name}' already exists")

    # Add the new search
    search_dict = search.model_dump()
    preferences.saved_searches.append(search_dict)

    # Mark the JSONB column as modified (SQLAlchemy doesn't auto-detect list changes)
    from sqlalchemy.orm import attributes

    attributes.flag_modified(preferences, "saved_searches")

    await session.commit()
    await session.refresh(preferences)

    return preferences


async def remove_saved_search(
    session: AsyncSession, user_id: int, search_id: str
) -> UserPreferences:
    """Remove a saved search from user preferences.

    Args:
        session: Database session
        user_id: User ID
        search_id: ID of the search to remove

    Returns:
        Updated UserPreferences object

    Raises:
        ValueError: If the search ID is not found
    """
    preferences = await get_or_create_preferences(session, user_id)

    if not preferences.saved_searches:
        raise ValueError(f"Saved search with ID '{search_id}' not found")

    # Find and remove the search
    original_count = len(preferences.saved_searches)
    preferences.saved_searches = [
        s for s in preferences.saved_searches if s.get("id") != search_id
    ]

    if len(preferences.saved_searches) == original_count:
        raise ValueError(f"Saved search with ID '{search_id}' not found")

    # Mark the JSONB column as modified
    from sqlalchemy.orm import attributes

    attributes.flag_modified(preferences, "saved_searches")

    await session.commit()
    await session.refresh(preferences)

    return preferences

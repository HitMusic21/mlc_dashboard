#!/usr/bin/env python3
"""
Seed filter presets for saved searches.

This script creates system-level filter presets that all users can access.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.crud.saved_search import create_saved_search
from app.schemas.saved_search import SavedSearchCreate, FilterConfig, FilterCondition

# System user ID for presets (admin user)
SYSTEM_USER_ID = 1

FILTER_PRESETS = [
    {
        "name": "Works Without ISWC",
        "description": "Find all musical works that don't have an ISWC code assigned",
        "filter_config": FilterConfig(
            logic="AND",
            filters=[
                FilterCondition(field="has_iswc", operator="equals", value=False)
            ],
            sort={"field": "created_at", "order": "desc"}
        ),
    },
    {
        "name": "Recent Works (Last 30 Days)",
        "description": "Musical works created in the last 30 days",
        "filter_config": FilterConfig(
            logic="AND",
            filters=[
                FilterCondition(
                    field="created_at",
                    operator="greater_than_or_equal",
                    value="NOW-30d"  # This would need backend support for relative dates
                )
            ],
            sort={"field": "created_at", "order": "desc"}
        ),
    },
    {
        "name": "Disputed Rights",
        "description": "Works with disputed rights that need attention",
        "filter_config": FilterConfig(
            logic="AND",
            filters=[
                FilterCondition(field="has_disputed_rights", operator="equals", value=True)
            ],
            sort={"field": "created_at", "order": "desc"}
        ),
    },
    {
        "name": "Incomplete Metadata",
        "description": "Works missing critical metadata (ISWC or publisher)",
        "filter_config": FilterConfig(
            logic="OR",
            filters=[
                FilterCondition(field="has_iswc", operator="equals", value=False),
                FilterCondition(field="publisher", operator="is_null", value=None),
            ],
            sort={"field": "title", "order": "asc"}
        ),
    },
    {
        "name": "High-Value Works",
        "description": "Works with complete metadata and clear rights",
        "filter_config": FilterConfig(
            logic="AND",
            filters=[
                FilterCondition(field="has_iswc", operator="equals", value=True),
                FilterCondition(field="has_disputed_rights", operator="equals", value=False),
                FilterCondition(field="publisher", operator="is_not_null", value=None),
            ],
            sort={"field": "created_at", "order": "desc"}
        ),
    },
]


async def seed_presets():
    """Create filter presets in the database."""
    # Create async engine and session
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print(f"🌱 Seeding {len(FILTER_PRESETS)} filter presets...")

        for preset_data in FILTER_PRESETS:
            try:
                preset = SavedSearchCreate(
                    name=preset_data["name"],
                    description=preset_data["description"],
                    filter_config=preset_data["filter_config"].model_dump(),
                    is_preset=True,
                    is_favorite=False,
                )

                saved_preset = await create_saved_search(
                    session=session,
                    user_id=SYSTEM_USER_ID,
                    search_data=preset
                )

                await session.commit()
                print(f"✅ Created preset: {saved_preset.name}")

            except Exception as e:
                print(f"❌ Failed to create preset '{preset_data['name']}': {e}")
                await session.rollback()
                continue

    await engine.dispose()
    print("\n✨ Filter presets seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_presets())

"""
Database index optimization script.
Adds indexes to improve query performance.

Run this script to add indexes without using Alembic migrations.
"""
import asyncio

from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import async_session_maker


# Index creation statements
INDEXES = [
    # Musical Works table indexes
    {
        "name": "idx_musical_works_iswc",
        "table": "musicalwork",
        "sql": "CREATE INDEX IF NOT EXISTS idx_musical_works_iswc ON musicalwork(iswc);",
        "description": "Index on ISWC for exact match lookups",
    },
    {
        "name": "idx_musical_works_title",
        "table": "musicalwork",
        "sql": "CREATE INDEX IF NOT EXISTS idx_musical_works_title ON musicalwork(title);",
        "description": "Index on title for search queries",
    },
    {
        "name": "idx_musical_works_year",
        "table": "musicalwork",
        "sql": "CREATE INDEX IF NOT EXISTS idx_musical_works_year ON musicalwork(year);",
        "description": "Index on year for filtering",
    },
    {
        "name": "idx_musical_works_disputed",
        "table": "musicalwork",
        "sql": "CREATE INDEX IF NOT EXISTS idx_musical_works_disputed ON musicalwork(has_disputed_rights);",
        "description": "Index on disputed rights flag for filtering",
    },
    {
        "name": "idx_musical_works_created_at",
        "table": "musicalwork",
        "sql": "CREATE INDEX IF NOT EXISTS idx_musical_works_created_at ON musicalwork(created_at DESC);",
        "description": "Index on created_at for sorting recent works",
    },
    # Contributor table indexes
    {
        "name": "idx_contributor_name",
        "table": "contributor",
        "sql": "CREATE INDEX IF NOT EXISTS idx_contributor_name ON contributor(name);",
        "description": "Index on contributor name for search",
    },
    {
        "name": "idx_contributor_ipi",
        "table": "contributor",
        "sql": "CREATE INDEX IF NOT EXISTS idx_contributor_ipi ON contributor(ipi_name_number);",
        "description": "Index on IPI number for exact lookups",
    },
    {
        "name": "idx_contributor_work_id",
        "table": "contributor",
        "sql": "CREATE INDEX IF NOT EXISTS idx_contributor_work_id ON contributor(work_id);",
        "description": "Foreign key index for work relationships",
    },
    # Catalog Upload table indexes
    {
        "name": "idx_catalog_upload_user_id",
        "table": "catalogupload",
        "sql": "CREATE INDEX IF NOT EXISTS idx_catalog_upload_user_id ON catalogupload(user_id);",
        "description": "Index on user_id for filtering user uploads",
    },
    {
        "name": "idx_catalog_upload_status",
        "table": "catalogupload",
        "sql": "CREATE INDEX IF NOT EXISTS idx_catalog_upload_status ON catalogupload(status);",
        "description": "Index on status for filtering by upload status",
    },
    {
        "name": "idx_catalog_upload_created_at",
        "table": "catalogupload",
        "sql": "CREATE INDEX IF NOT EXISTS idx_catalog_upload_created_at ON catalogupload(created_at DESC);",
        "description": "Index on created_at for sorting recent uploads",
    },
    {
        "name": "idx_catalog_upload_user_status",
        "table": "catalogupload",
        "sql": "CREATE INDEX IF NOT EXISTS idx_catalog_upload_user_status ON catalogupload(user_id, status);",
        "description": "Composite index for user + status queries",
    },
    # Catalog Match table indexes
    {
        "name": "idx_catalog_match_upload_id",
        "table": "catalogmatch",
        "sql": "CREATE INDEX IF NOT EXISTS idx_catalog_match_upload_id ON catalogmatch(upload_id);",
        "description": "Index on upload_id for fetching all matches for an upload",
    },
    {
        "name": "idx_catalog_match_work_id",
        "table": "catalogmatch",
        "sql": "CREATE INDEX IF NOT EXISTS idx_catalog_match_work_id ON catalogmatch(matched_work_id);",
        "description": "Index on work_id for reverse lookups",
    },
    {
        "name": "idx_catalog_match_confidence",
        "table": "catalogmatch",
        "sql": "CREATE INDEX IF NOT EXISTS idx_catalog_match_confidence ON catalogmatch(confidence_level);",
        "description": "Index on confidence level for filtering",
    },
    {
        "name": "idx_catalog_match_score",
        "table": "catalogmatch",
        "sql": "CREATE INDEX IF NOT EXISTS idx_catalog_match_score ON catalogmatch(match_score DESC);",
        "description": "Index on match score for sorting",
    },
    {
        "name": "idx_catalog_match_upload_confidence",
        "table": "catalogmatch",
        "sql": "CREATE INDEX IF NOT EXISTS idx_catalog_match_upload_confidence ON catalogmatch(upload_id, confidence_level);",
        "description": "Composite index for upload + confidence queries",
    },
    # User table indexes
    {
        "name": "idx_user_email",
        "table": "user",
        "sql": "CREATE INDEX IF NOT EXISTS idx_user_email ON \"user\"(email);",
        "description": "Index on email for login lookups (unique constraint already exists)",
    },
    {
        "name": "idx_user_role",
        "table": "user",
        "sql": "CREATE INDEX IF NOT EXISTS idx_user_role ON \"user\"(role);",
        "description": "Index on role for admin queries",
    },
    {
        "name": "idx_user_active",
        "table": "user",
        "sql": "CREATE INDEX IF NOT EXISTS idx_user_active ON \"user\"(is_active);",
        "description": "Index on is_active for filtering active users",
    },
    # Resource table indexes
    {
        "name": "idx_resource_work_id",
        "table": "resource",
        "sql": "CREATE INDEX IF NOT EXISTS idx_resource_work_id ON resource(work_id);",
        "description": "Foreign key index for work relationships",
    },
    {
        "name": "idx_resource_type",
        "table": "resource",
        "sql": "CREATE INDEX IF NOT EXISTS idx_resource_type ON resource(resource_type);",
        "description": "Index on resource type for filtering",
    },
    # Rights Controller table indexes
    {
        "name": "idx_rights_controller_work_id",
        "table": "rightscontroller",
        "sql": "CREATE INDEX IF NOT EXISTS idx_rights_controller_work_id ON rightscontroller(work_id);",
        "description": "Foreign key index for work relationships",
    },
    {
        "name": "idx_rights_controller_territory",
        "table": "rightscontroller",
        "sql": "CREATE INDEX IF NOT EXISTS idx_rights_controller_territory ON rightscontroller(territory);",
        "description": "Index on territory for territorial queries",
    },
]


async def add_indexes(session: AsyncSession) -> None:
    """Add all indexes to the database."""
    print("=" * 60)
    print("Adding Database Indexes for Performance")
    print("=" * 60)
    print()

    success_count = 0
    error_count = 0

    for index in INDEXES:
        try:
            print(f"Creating index: {index['name']}")
            print(f"  Table: {index['table']}")
            print(f"  Description: {index['description']}")

            # Execute index creation
            await session.execute(text(index["sql"]))
            await session.commit()

            print(f"  ✓ Created successfully")
            success_count += 1

        except Exception as e:
            print(f"  ⚠ Error: {e}")
            error_count += 1
            await session.rollback()

        print()

    print("=" * 60)
    print(f"Summary: {success_count} indexes created, {error_count} errors")
    print("=" * 60)


async def analyze_tables(session: AsyncSession) -> None:
    """Run ANALYZE on all tables to update statistics."""
    print("\nAnalyzing tables to update statistics...")

    tables = [
        "musicalwork",
        "contributor",
        "catalogupload",
        "catalogmatch",
        '"user"',
        "resource",
        "rightscontroller",
    ]

    for table in tables:
        try:
            await session.execute(text(f"ANALYZE {table};"))
            print(f"  ✓ Analyzed {table}")
        except Exception as e:
            print(f"  ⚠ Error analyzing {table}: {e}")

    await session.commit()
    print("✓ Analysis complete")


async def main():
    """Main execution function."""
    async with async_session_maker() as session:
        # Add indexes
        await add_indexes(session)

        # Analyze tables
        await analyze_tables(session)

    print("\n✓ Database optimization complete!")
    print("\nRecommendations:")
    print("  1. Monitor slow queries with pg_stat_statements extension")
    print("  2. Run VACUUM ANALYZE periodically to maintain statistics")
    print("  3. Consider partitioning large tables (catalogmatch) if data grows")
    print("  4. Use connection pooling (PgBouncer) in production")
    print()


if __name__ == "__main__":
    asyncio.run(main())

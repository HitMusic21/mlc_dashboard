"""CRUD operations for MusicalWork entities."""

from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.musical_work import MusicalWork
from app.models.resource import Resource
from app.models.work_resource_link import WorkResourceLink


async def get_works(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    filters: Optional[Dict] = None,
) -> List[MusicalWork]:
    """Get paginated list of musical works with optional filters.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        filters: Optional filters (search, has_iswc, has_disputed_rights, etc.)

    Returns:
        List of MusicalWork objects
    """
    query = select(MusicalWork)

    # Apply filters
    if filters:
        if filters.get("search"):
            search_term = f"%{filters['search']}%"
            query = query.where(MusicalWork.title.ilike(search_term))

        if filters.get("has_iswc") is not None:
            if filters["has_iswc"]:
                query = query.where(MusicalWork.iswc.isnot(None))
            else:
                query = query.where(MusicalWork.iswc.is_(None))

        if filters.get("has_disputed_rights") is not None:
            query = query.where(MusicalWork.has_disputed_rights == filters["has_disputed_rights"])

        if filters.get("created_after"):
            query = query.where(MusicalWork.created_at >= filters["created_after"])

        if filters.get("created_before"):
            query = query.where(MusicalWork.created_at <= filters["created_before"])

    # Order by created_at descending
    query = query.order_by(MusicalWork.created_at.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_work_by_id(session: AsyncSession, work_id: int) -> Optional[MusicalWork]:
    """Get a musical work by ID with its resources (optimized with eager loading).

    Uses a single query with join to avoid N+1 problem.

    Args:
        session: Database session
        work_id: Work ID

    Returns:
        MusicalWork object or None if not found
    """
    # Get work and resources in a single query using outerjoin
    query = (
        select(MusicalWork, Resource)
        .outerjoin(WorkResourceLink, MusicalWork.id == WorkResourceLink.musical_work_id)
        .outerjoin(Resource, WorkResourceLink.resource_id == Resource.id)
        .where(MusicalWork.id == work_id)
    )

    result = await session.execute(query)
    rows = result.all()

    if not rows:
        return None

    # First row contains the work
    work = rows[0][0]

    # Collect all resources from the joined rows
    resources = []
    for row in rows:
        if row[1]:  # If resource exists (not null from left join)
            resources.append(row[1])

    # Remove duplicates (if any) by id
    seen_ids = set()
    unique_resources = []
    for resource in resources:
        if resource.id not in seen_ids:
            seen_ids.add(resource.id)
            unique_resources.append(resource)

    work.resources = unique_resources

    return work


async def search_works(
    session: AsyncSession,
    query: str,
    filters: Optional[Dict] = None,
    skip: int = 0,
    limit: int = 50,
) -> List[MusicalWork]:
    """Full-text search for musical works using PostgreSQL tsvector.

    Args:
        session: Database session
        query: Search query string
        filters: Optional additional filters
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of MusicalWork objects sorted by relevance
    """
    # For now, use simple ILIKE search
    # TODO: Implement PostgreSQL full-text search with tsvector
    search_query = select(MusicalWork).where(
        MusicalWork.title.ilike(f"%{query}%")
        | MusicalWork.contributors.ilike(f"%{query}%")
        | MusicalWork.publisher.ilike(f"%{query}%")
    )

    # Apply additional filters
    if filters:
        if filters.get("has_iswc") is not None:
            if filters["has_iswc"]:
                search_query = search_query.where(MusicalWork.iswc.isnot(None))
            else:
                search_query = search_query.where(MusicalWork.iswc.is_(None))

        if filters.get("has_disputed_rights") is not None:
            search_query = search_query.where(
                MusicalWork.has_disputed_rights == filters["has_disputed_rights"]
            )

    # Order by title match first
    search_query = search_query.order_by(MusicalWork.title)

    # Apply pagination
    search_query = search_query.offset(skip).limit(limit)

    result = await session.execute(search_query)
    return list(result.scalars().all())


async def get_works_count(session: AsyncSession, filters: Optional[Dict] = None) -> int:
    """Get total count of works matching filters.

    Args:
        session: Database session
        filters: Optional filters

    Returns:
        Total count of matching works
    """
    query = select(func.count(MusicalWork.id))

    # Apply same filters as get_works
    if filters:
        if filters.get("search"):
            search_term = f"%{filters['search']}%"
            query = query.where(MusicalWork.title.ilike(search_term))

        if filters.get("has_iswc") is not None:
            if filters["has_iswc"]:
                query = query.where(MusicalWork.iswc.isnot(None))
            else:
                query = query.where(MusicalWork.iswc.is_(None))

        if filters.get("has_disputed_rights") is not None:
            query = query.where(MusicalWork.has_disputed_rights == filters["has_disputed_rights"])

        if filters.get("created_after"):
            query = query.where(MusicalWork.created_at >= filters["created_after"])

        if filters.get("created_before"):
            query = query.where(MusicalWork.created_at <= filters["created_before"])

    result = await session.execute(query)
    return result.scalar_one()


async def get_statistics(session: AsyncSession) -> Dict:
    """Get dashboard statistics for musical works.

    Args:
        session: Database session

    Returns:
        Dictionary with statistics
    """
    # Total works
    total_query = select(func.count(MusicalWork.id))
    total_result = await session.execute(total_query)
    total_works = total_result.scalar_one()

    # Works with ISWC
    iswc_query = select(func.count(MusicalWork.id)).where(MusicalWork.iswc.isnot(None))
    iswc_result = await session.execute(iswc_query)
    works_with_iswc = iswc_result.scalar_one()

    # Disputed works
    disputed_query = select(func.count(MusicalWork.id)).where(
        MusicalWork.has_disputed_rights == True  # noqa: E712
    )
    disputed_result = await session.execute(disputed_query)
    disputed_works = disputed_result.scalar_one()

    # Monthly trend (last 12 months)
    from datetime import datetime, timedelta

    twelve_months_ago = datetime.utcnow() - timedelta(days=365)

    # SQLite-compatible date grouping using strftime
    trend_query = (
        select(
            func.strftime("%Y-%m", MusicalWork.created_at).label("month"),
            func.count(MusicalWork.id).label("count"),
        )
        .where(MusicalWork.created_at >= twelve_months_ago)
        .group_by("month")
        .order_by("month")
    )

    trend_result = await session.execute(trend_query)
    monthly_trend = [
        {"month": row.month, "count": row.count}  # month is already formatted as YYYY-MM
        for row in trend_result.all()
    ]

    # Calculate percentages
    works_with_iswc_percentage = (
        (works_with_iswc / total_works * 100) if total_works > 0 else 0.0
    )
    disputed_works_percentage = (
        (disputed_works / total_works * 100) if total_works > 0 else 0.0
    )

    return {
        "total_works": total_works,
        "works_with_iswc": works_with_iswc,
        "works_with_iswc_percentage": works_with_iswc_percentage,
        "disputed_works": disputed_works,
        "disputed_works_percentage": disputed_works_percentage,
        "monthly_trend": monthly_trend,
    }


async def get_mlc_statistics(session: AsyncSession) -> Dict:
    """Get MLC-specific business metrics for dashboard.

    Calculates metrics for:
    - Unmatched recordings (resources without work links)
    - Unclaimed shares (works without publisher info)
    - Low confidence matches
    - Claims tracking

    Args:
        session: Database session

    Returns:
        Dictionary with MLC business metrics
    """
    from app.models.catalog_match import CatalogMatch, ConfidenceLevel
    from app.models.work_resource_link import WorkResourceLink

    # 1. Unmatched Recordings: Resources without any work links
    unmatched_query = (
        select(func.count(Resource.id))
        .select_from(Resource)
        .outerjoin(WorkResourceLink, Resource.id == WorkResourceLink.resource_id)
        .where(WorkResourceLink.id.is_(None))
    )
    unmatched_result = await session.execute(unmatched_query)
    unmatched_recordings = unmatched_result.scalar_one()

    # 2. Unclaimed Shares: Works without publisher information
    unclaimed_query = select(func.count(MusicalWork.id)).where(
        (MusicalWork.publisher.is_(None)) | (MusicalWork.publisher == "")
    )
    unclaimed_result = await session.execute(unclaimed_query)
    unclaimed_shares = unclaimed_result.scalar_one()

    # 3. Low Confidence Matches: Catalog matches with low confidence
    low_confidence_query = select(func.count(CatalogMatch.id)).where(
        CatalogMatch.confidence_level == ConfidenceLevel.LOW
    )
    low_confidence_result = await session.execute(low_confidence_query)
    low_confidence_matches = low_confidence_result.scalar_one()

    # 4. Claims This Month: Count catalog uploads from this month
    from datetime import datetime

    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    from app.models.catalog_upload import CatalogUpload, UploadStatus

    claims_query = select(func.count(CatalogUpload.id)).where(
        CatalogUpload.created_at >= first_day_of_month,
        CatalogUpload.status == UploadStatus.COMPLETED,
    )
    claims_result = await session.execute(claims_query)
    claims_submitted = claims_result.scalar_one()

    # Estimate unclaimed value ($5 per unmatched recording as conservative estimate)
    estimated_unclaimed_value = unmatched_recordings * 5

    # Estimate claims value ($10 per completed upload as average)
    claims_value = claims_submitted * 10

    # Calculate unclaimed percentage
    total_works_query = select(func.count(MusicalWork.id))
    total_works_result = await session.execute(total_works_query)
    total_works = total_works_result.scalar_one()
    unclaimed_percentage = (unclaimed_shares / total_works * 100) if total_works > 0 else 0.0

    return {
        "unmatched_recordings": unmatched_recordings,
        "unclaimed_shares": unclaimed_shares,
        "unclaimed_percentage": unclaimed_percentage,
        "low_confidence_matches": low_confidence_matches,
        "estimated_unclaimed_value": estimated_unclaimed_value,
        "claims_submitted": claims_submitted,
        "claims_value": claims_value,
    }

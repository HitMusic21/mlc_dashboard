"""Works API routes."""

import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.crud.works import (
    get_mlc_statistics,
    get_statistics,
    get_work_by_id,
    get_works,
    get_works_count,
    search_works,
)
from app.db.session import get_session
from app.models.user import User
from app.schemas.works import (
    DashboardStatisticsResponse,
    MLCStatisticsResponse,
    MusicalWorkDetailedResponse,
    Pagination,
    ResponseMeta,
    WorkSearchRequest,
    WorkSearchResponse,
    WorksListResponse,
)
from app.services.cache_service import CacheTTL, cache_service, generate_cache_key

router = APIRouter(prefix="/works", tags=["Works"])


@router.get("/", response_model=WorksListResponse)
async def list_works(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=1000, description="Items per page"),
    search: Optional[str] = Query(None, description="Search query"),
    has_iswc: Optional[bool] = Query(None, description="Filter by ISWC presence"),
    has_disputed_rights: Optional[bool] = Query(
        None, description="Filter by disputed rights"
    ),
    created_after: Optional[str] = Query(None, description="Created after date"),
    created_before: Optional[str] = Query(None, description="Created before date"),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """List musical works with pagination and filtering.

    Cached for 5 minutes to improve performance.

    Args:
        page: Page number
        limit: Items per page
        search: Search query
        has_iswc: Filter by ISWC presence
        has_disputed_rights: Filter by disputed rights
        created_after: Filter by creation date
        created_before: Filter by creation date
        current_user: Current authenticated user
        session: Database session

    Returns:
        WorksListResponse with paginated works
    """
    start_time = time.time()

    # Build filters
    filters = {}
    if search:
        filters["search"] = search
    if has_iswc is not None:
        filters["has_iswc"] = has_iswc
    if has_disputed_rights is not None:
        filters["has_disputed_rights"] = has_disputed_rights
    if created_after:
        filters["created_after"] = created_after
    if created_before:
        filters["created_before"] = created_before

    # Generate cache key
    cache_key = generate_cache_key(
        "works:list",
        page=page,
        limit=limit,
        search=search,
        has_iswc=has_iswc,
        has_disputed_rights=has_disputed_rights,
        created_after=created_after,
        created_before=created_before,
    )

    # Try to get from cache
    cached_response = await cache_service.get(cache_key)
    if cached_response:
        # Return cached response with cache hit indicator
        cached_response["meta"]["cache_hit"] = True
        cached_response["meta"]["response_time_ms"] = (time.time() - start_time) * 1000
        return WorksListResponse(**cached_response)

    # Get works from database
    skip = (page - 1) * limit
    works = await get_works(session, skip=skip, limit=limit, filters=filters)

    # Get total count
    total_count = await get_works_count(session, filters=filters)

    # Calculate pagination
    total_pages = (total_count + limit - 1) // limit

    # Calculate response time
    response_time_ms = (time.time() - start_time) * 1000

    # Build response
    response = WorksListResponse(
        data=works,
        pagination=Pagination(
            page=page,
            limit=limit,
            total_items=total_count,
            total_pages=total_pages,
        ),
        meta=ResponseMeta(response_time_ms=response_time_ms, cache_hit=False),
    )

    # Cache the response (5 minutes)
    await cache_service.set(
        cache_key,
        response.model_dump(mode="json"),
        ttl=CacheTTL.SHORT,
    )

    return response


@router.get("/statistics", response_model=DashboardStatisticsResponse)
async def get_works_statistics(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Get dashboard statistics for musical works.

    Cached for 10 minutes since statistics change infrequently.

    Args:
        current_user: Current authenticated user
        session: Database session

    Returns:
        DashboardStatisticsResponse with statistics
    """
    # Check cache first (10 minute TTL for stats)
    cache_key = "dashboard:statistics"
    cached_stats = await cache_service.get(cache_key)

    if cached_stats:
        return DashboardStatisticsResponse(**cached_stats)

    # Get fresh statistics from database
    stats = await get_statistics(session)

    # Cache for 10 minutes
    await cache_service.set(cache_key, stats, ttl=CacheTTL.MEDIUM)

    return DashboardStatisticsResponse(**stats)


@router.get("/statistics/mlc", response_model=MLCStatisticsResponse)
async def get_mlc_works_statistics(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Get MLC-specific business metrics for dashboard.

    Returns metrics for tracking royalty recovery opportunities:
    - Unmatched recordings (resources without work links)
    - Unclaimed shares (works without publisher info)
    - Low confidence matches requiring review
    - Claims submitted this month

    Cached for 10 minutes since statistics change infrequently.

    Args:
        current_user: Current authenticated user
        session: Database session

    Returns:
        MLCStatisticsResponse with MLC business metrics
    """
    # Check cache first (10 minute TTL for stats)
    cache_key = "dashboard:mlc_statistics"
    cached_stats = await cache_service.get(cache_key)

    if cached_stats:
        return MLCStatisticsResponse(**cached_stats)

    # Get fresh MLC statistics from database
    mlc_stats = await get_mlc_statistics(session)

    # Cache for 10 minutes
    await cache_service.set(cache_key, mlc_stats, ttl=CacheTTL.MEDIUM)

    return MLCStatisticsResponse(**mlc_stats)


@router.get("/{work_id}", response_model=MusicalWorkDetailedResponse)
async def get_work(
    work_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Get a single musical work with resources.

    Args:
        work_id: Work ID
        current_user: Current authenticated user
        session: Database session

    Returns:
        MusicalWorkDetailedResponse with work and resources
    """
    work = await get_work_by_id(session, work_id)

    if not work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work not found",
        )

    return work


@router.post("/search", response_model=WorkSearchResponse)
async def search_works_endpoint(
    request: WorkSearchRequest,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Full-text search for musical works.

    Args:
        request: Search request
        current_user: Current authenticated user
        session: Database session

    Returns:
        WorkSearchResponse with search results
    """
    start_time = time.time()

    # Perform search
    skip = (request.page - 1) * request.limit
    results = await search_works(
        session,
        query=request.query,
        filters=request.filters,
        skip=skip,
        limit=request.limit,
    )

    # Get total count (for now, use same count as regular works)
    # TODO: Implement proper search count
    total_count = len(results)

    # Calculate pagination
    total_pages = (total_count + request.limit - 1) // request.limit

    # Calculate response time
    response_time_ms = (time.time() - start_time) * 1000

    # Add search scores (placeholder - would come from Elasticsearch)
    search_results = []
    for work in results:
        search_result = work.dict() if hasattr(work, "dict") else work.__dict__
        search_result["search_score"] = 1.0  # Placeholder
        search_results.append(search_result)

    return WorkSearchResponse(
        data=search_results,
        pagination=Pagination(
            page=request.page,
            limit=request.limit,
            total_items=total_count,
            total_pages=total_pages,
        ),
        meta=ResponseMeta(
            response_time_ms=response_time_ms,
        ),
    )

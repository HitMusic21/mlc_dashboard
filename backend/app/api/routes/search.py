"""Full-text search API routes using Elasticsearch."""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.crud.works import get_works
from app.db.session import get_session
from app.models.user import User
from app.services.search_service import search_service

router = APIRouter(prefix="/search", tags=["Search"])


@router.post("/reindex", status_code=202)
async def reindex_works(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Reindex all works in Elasticsearch (admin only).

    This endpoint rebuilds the search index from the database.
    Use after bulk data imports or index corruption.

    Args:
        current_user: Current authenticated user (admin only)
        session: Database session

    Returns:
        Status message

    Raises:
        HTTPException: If user is not admin
    """
    from fastapi import HTTPException

    # Only admins can reindex
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    # Get all works from database
    works = await get_works(session, skip=0, limit=10000)  # Get all works

    # Convert to dict for indexing
    works_data = [
        {
            "id": work.id,
            "title": work.title,
            "contributors": work.contributors,
            "publisher": work.publisher,
            "iswc": work.iswc,
            "has_disputed_rights": work.has_disputed_rights,
            "created_at": work.created_at.isoformat() if work.created_at else None,
        }
        for work in works
    ]

    # Reindex in background (in production, use Celery task)
    await search_service.reindex_all(works_data)

    return {
        "status": "reindexing",
        "message": f"Reindexing {len(works_data)} works",
        "count": len(works_data),
    }


@router.get("/works")
async def search_works(
    q: str = Query(..., min_length=2, description="Search query"),
    has_iswc: Optional[bool] = Query(None, description="Filter by ISWC presence"),
    has_disputed_rights: Optional[bool] = Query(
        None, description="Filter by disputed rights"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    current_user: User = Depends(get_current_active_user),
):
    """Full-text search for musical works.

    Searches across title, contributors, and publisher fields with:
    - Fuzzy matching for typos
    - Relevance scoring
    - Result highlighting
    - Multi-field boosting (title^3, contributors^2, publisher^1)

    Args:
        q: Search query string (minimum 2 characters)
        has_iswc: Optional filter for works with/without ISWC
        has_disputed_rights: Optional filter for disputed rights
        page: Page number (1-indexed)
        limit: Results per page (max 100)
        current_user: Current authenticated user

    Returns:
        Search results with highlights and metadata

    Example:
        GET /api/v1/search/works?q=beethoven+symphony&has_iswc=true&page=1&limit=20
    """
    # Build filters
    filters = {}
    if has_iswc is not None:
        filters["has_iswc"] = has_iswc
    if has_disputed_rights is not None:
        filters["has_disputed_rights"] = has_disputed_rights

    # Calculate offset
    offset = (page - 1) * limit

    # Perform search
    results = await search_service.search(
        query=q, filters=filters if filters else None, size=limit, from_=offset
    )

    # Calculate pagination
    total = results.get("total", 0)
    total_pages = (total + limit - 1) // limit if total > 0 else 0

    return {
        "results": results.get("results", []),
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
        "query": q,
        "filters": filters,
        "max_score": results.get("max_score"),
    }


@router.get("/suggest")
async def suggest_works(
    q: str = Query(..., min_length=1, description="Suggestion query"),
    limit: int = Query(5, ge=1, le=20, description="Number of suggestions"),
    current_user: User = Depends(get_current_active_user),
):
    """Get search suggestions for autocomplete.

    Provides typeahead suggestions based on work titles.

    Args:
        q: Partial query string
        limit: Maximum number of suggestions (max 20)
        current_user: Current authenticated user

    Returns:
        List of suggestions

    Example:
        GET /api/v1/search/suggest?q=beetho&limit=5
    """
    # Simple search with title boost
    results = await search_service.search(query=q, size=limit)

    # Extract titles for suggestions
    suggestions = [
        {
            "title": work.get("title"),
            "id": work.get("id"),
            "contributors": work.get("contributors"),
            "score": work.get("_score"),
        }
        for work in results.get("results", [])
    ]

    return {"suggestions": suggestions, "query": q}

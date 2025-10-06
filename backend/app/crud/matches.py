"""CRUD operations for CatalogMatch entities."""

from collections import defaultdict
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog_match import CatalogMatch, ConfidenceLevel
from app.models.musical_work import MusicalWork


async def create_match(session: AsyncSession, match_data: Dict) -> CatalogMatch:
    """Create a new catalog match record.

    Args:
        session: Database session
        match_data: Match data (catalog_upload_id, musical_work_id, scores, etc.)

    Returns:
        Created CatalogMatch object
    """
    match = CatalogMatch(**match_data)
    session.add(match)
    await session.commit()
    await session.refresh(match)
    return match


async def create_matches_bulk(
    session: AsyncSession, matches_data: List[Dict]
) -> List[CatalogMatch]:
    """Create multiple catalog matches in bulk.

    Args:
        session: Database session
        matches_data: List of match data dictionaries

    Returns:
        List of created CatalogMatch objects
    """
    matches = [CatalogMatch(**data) for data in matches_data]
    session.add_all(matches)
    await session.commit()

    return matches


async def get_matches_for_upload(
    session: AsyncSession,
    upload_id: int,
    filters: Optional[Dict] = None,
    skip: int = 0,
    limit: int = 1000,
) -> List[CatalogMatch]:
    """Get all matches for a catalog upload.

    Args:
        session: Database session
        upload_id: Catalog upload ID
        filters: Optional filters (confidence, min_score)
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List of CatalogMatch objects with work details
    """
    query = (
        select(CatalogMatch, MusicalWork)
        .join(MusicalWork, CatalogMatch.musical_work_id == MusicalWork.id)
        .where(CatalogMatch.catalog_upload_id == upload_id)
    )

    # Apply filters
    if filters:
        if filters.get("confidence"):
            confidence_level = ConfidenceLevel(filters["confidence"])
            query = query.where(CatalogMatch.confidence_level == confidence_level)

        if filters.get("min_score"):
            query = query.where(CatalogMatch.match_score >= filters["min_score"])

    # Order by uploaded track title, then by score descending
    query = query.order_by(
        CatalogMatch.uploaded_track_title, CatalogMatch.match_score.desc()
    )

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    rows = result.all()

    # Attach work to match for easy access
    matches = []
    for match, work in rows:
        match.work = work
        matches.append(match)

    return matches


async def get_matches_grouped(
    session: AsyncSession, upload_id: int, filters: Optional[Dict] = None
) -> List[Dict]:
    """Get matches grouped by uploaded track.

    Args:
        session: Database session
        upload_id: Catalog upload ID
        filters: Optional filters

    Returns:
        List of match groups with structure:
        {
            "uploaded_track": {...},
            "matches": [...]
        }
    """
    matches = await get_matches_for_upload(session, upload_id, filters)

    # Group by uploaded track
    grouped = defaultdict(list)
    for match in matches:
        track_key = (
            match.uploaded_track_title,
            match.uploaded_track_artist,
            match.uploaded_track_duration,
        )
        grouped[track_key].append(match)

    # Convert to response format
    result = []
    for (title, artist, duration), track_matches in grouped.items():
        result.append(
            {
                "uploaded_track": {
                    "title": title,
                    "artist": artist,
                    "duration": duration,
                },
                "matches": track_matches,
            }
        )

    return result


async def get_match_statistics(session: AsyncSession, upload_id: int) -> Dict:
    """Get statistics for matches of an upload.

    Args:
        session: Database session
        upload_id: Catalog upload ID

    Returns:
        Dictionary with match statistics
    """
    from sqlalchemy import func

    # Total matches
    total_query = select(func.count(CatalogMatch.id)).where(
        CatalogMatch.catalog_upload_id == upload_id
    )
    total_result = await session.execute(total_query)
    total_matches = total_result.scalar_one()

    # Matches by confidence level
    confidence_query = (
        select(CatalogMatch.confidence_level, func.count(CatalogMatch.id))
        .where(CatalogMatch.catalog_upload_id == upload_id)
        .group_by(CatalogMatch.confidence_level)
    )
    confidence_result = await session.execute(confidence_query)
    by_confidence = {row[0]: row[1] for row in confidence_result.all()}

    # Average match score
    avg_query = select(func.avg(CatalogMatch.match_score)).where(
        CatalogMatch.catalog_upload_id == upload_id
    )
    avg_result = await session.execute(avg_query)
    avg_score = float(avg_result.scalar_one() or 0)

    return {
        "total_matches": total_matches,
        "high_confidence": by_confidence.get(ConfidenceLevel.HIGH, 0),
        "medium_confidence": by_confidence.get(ConfidenceLevel.MEDIUM, 0),
        "low_confidence": by_confidence.get(ConfidenceLevel.LOW, 0),
        "average_score": round(avg_score, 4),
    }

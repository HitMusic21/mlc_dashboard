"""Matching engine orchestrator for catalog processing.

Coordinates the matching process between uploaded tracks and BWARM works.
"""

from collections import defaultdict
from typing import Callable, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog_match import CatalogMatch
from app.models.musical_work import MusicalWork
from app.services.matching.scorer import MatchScorer
from app.services.matching.similarity import normalize_text


class MatchingEngine:
    """Engine for matching uploaded catalog tracks to BWARM works."""

    def __init__(self, session: AsyncSession, max_matches_per_track: int = 10):
        """Initialize matching engine.

        Args:
            session: Database session
            max_matches_per_track: Maximum matches to return per track
        """
        self.session = session
        self.max_matches_per_track = max_matches_per_track
        self.scorer = MatchScorer()

    async def match_track(
        self, uploaded_track: dict, progress_callback: Optional[Callable] = None
    ) -> List[dict]:
        """Match a single uploaded track against BWARM works.

        Args:
            uploaded_track: Dict with title, artist, duration, iswc
            progress_callback: Optional callback for progress updates

        Returns:
            List of match dictionaries with scores and work references
        """
        # Get candidate works from database
        candidates = await self._get_candidate_works(uploaded_track)

        if not candidates:
            return []

        # Score all candidates
        match_results = self.scorer.batch_score_candidates(
            uploaded_track, candidates, self.max_matches_per_track
        )

        # Convert to match dictionaries
        matches = []
        for rank, result in enumerate(match_results, 1):
            matches.append(
                {
                    "musical_work_id": result.work.id,
                    "uploaded_track_title": uploaded_track["title"],
                    "uploaded_track_artist": uploaded_track.get("artist"),
                    "uploaded_track_duration": uploaded_track.get("duration"),
                    "match_score": result.match_score,
                    "confidence_level": result.confidence_level,
                    "rank": rank,
                    "title_similarity_score": result.title_similarity,
                    "artist_similarity_score": result.artist_similarity,
                    "duration_similarity_score": result.duration_similarity,
                }
            )

        return matches

    async def match_catalog(
        self,
        upload_id: int,
        tracks: List[dict],
        progress_callback: Optional[Callable] = None,
    ) -> List[CatalogMatch]:
        """Match an entire catalog of tracks.

        Args:
            upload_id: Catalog upload ID
            tracks: List of track dictionaries
            progress_callback: Optional callback for progress updates

        Returns:
            List of CatalogMatch objects
        """
        # Deduplicate tracks first
        deduplicated_tracks = self._deduplicate_tracks(tracks)

        all_matches = []
        total_tracks = len(deduplicated_tracks)

        for idx, track in enumerate(deduplicated_tracks):
            # Match single track
            matches = await self.match_track(track, progress_callback)

            # Add catalog_upload_id to each match
            for match in matches:
                match["catalog_upload_id"] = upload_id

            all_matches.extend(matches)

            # Call progress callback
            if progress_callback:
                progress = ((idx + 1) / total_tracks) * 100
                await progress_callback(progress, idx + 1, total_tracks)

        return all_matches

    async def _get_candidate_works(self, uploaded_track: dict) -> List[MusicalWork]:
        """Get candidate works for matching.

        Uses pre-filtering strategies:
        1. Exact ISWC match
        2. Title prefix match
        3. Fuzzy title match

        Args:
            uploaded_track: Track to match

        Returns:
            List of candidate MusicalWork objects
        """
        candidates = []

        # Strategy 1: Exact ISWC match
        if uploaded_track.get("iswc"):
            iswc_query = select(MusicalWork).where(
                MusicalWork.iswc == uploaded_track["iswc"]
            )
            result = await self.session.execute(iswc_query)
            iswc_matches = list(result.scalars().all())
            if iswc_matches:
                return iswc_matches  # Return immediately if exact ISWC match

        # Strategy 2: Title similarity using ILIKE
        title = uploaded_track.get("title", "")
        normalized_title = normalize_text(title)

        if normalized_title:
            # Get works with similar titles (first 3 characters)
            prefix = normalized_title[:3] if len(normalized_title) >= 3 else normalized_title
            title_query = (
                select(MusicalWork)
                .where(MusicalWork.title.ilike(f"{prefix}%"))
                .limit(100)  # Limit candidates to prevent excessive matching
            )

            result = await self.session.execute(title_query)
            candidates = list(result.scalars().all())

        # If no candidates found, try broader search
        if not candidates:
            # Fallback: get recent works (last 1000)
            fallback_query = (
                select(MusicalWork)
                .order_by(MusicalWork.created_at.desc())
                .limit(1000)
            )
            result = await self.session.execute(fallback_query)
            candidates = list(result.scalars().all())

        return candidates

    def _deduplicate_tracks(self, tracks: List[dict]) -> List[dict]:
        """Deduplicate uploaded tracks before matching.

        Groups tracks by normalized title and merges metadata.

        Args:
            tracks: List of track dictionaries

        Returns:
            List of deduplicated track dictionaries
        """
        # Group by normalized title
        grouped = defaultdict(list)

        for track in tracks:
            title = track.get("title", "")
            normalized = normalize_text(title)

            if normalized:
                grouped[normalized].append(track)

        # Merge duplicates
        deduplicated = []

        for normalized_title, track_group in grouped.items():
            if len(track_group) == 1:
                # No duplicates
                deduplicated.append(track_group[0])
            else:
                # Merge duplicates - take first track and merge artist info
                merged = track_group[0].copy()

                # Collect all artists
                artists = set()
                for t in track_group:
                    if t.get("artist"):
                        artists.add(t["artist"])

                if artists:
                    merged["artist"] = " / ".join(sorted(artists))

                # Use average duration if available
                durations = [t.get("duration") for t in track_group if t.get("duration")]
                if durations:
                    merged["duration"] = int(sum(durations) / len(durations))

                deduplicated.append(merged)

        return deduplicated

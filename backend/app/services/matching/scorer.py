"""Scoring system for catalog matching.

Calculates weighted match scores and assigns confidence levels.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from app.models.catalog_match import ConfidenceLevel
from app.services.matching.similarity import (
    combined_string_similarity,
    duration_similarity,
    jaro_winkler_similarity,
)


@dataclass
class MatchResult:
    """Result of a match calculation."""

    match_score: Decimal
    confidence_level: ConfidenceLevel
    title_similarity: Decimal
    artist_similarity: Optional[Decimal] = None
    duration_similarity: Optional[Decimal] = None


class MatchScorer:
    """Calculate match scores between uploaded tracks and BWARM works."""

    # Weights for scoring components
    TITLE_WEIGHT = 0.40
    ARTIST_WEIGHT = 0.30
    DURATION_WEIGHT = 0.20
    YEAR_WEIGHT = 0.10

    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    MEDIUM_CONFIDENCE_THRESHOLD = 0.70

    def calculate_match_score(
        self,
        uploaded_title: str,
        uploaded_artist: Optional[str],
        uploaded_duration: Optional[int],
        work_title: str,
        work_contributors: Optional[str],
        work_iswc: Optional[str] = None,
        uploaded_iswc: Optional[str] = None,
    ) -> MatchResult:
        """Calculate match score between uploaded track and BWARM work.

        Args:
            uploaded_title: Title from uploaded catalog
            uploaded_artist: Artist from uploaded catalog
            uploaded_duration: Duration in seconds from uploaded catalog
            work_title: Title from BWARM work
            work_contributors: Contributors from BWARM work
            work_iswc: ISWC from BWARM work
            uploaded_iswc: ISWC from uploaded catalog

        Returns:
            MatchResult with score and confidence level
        """
        # Check for exact ISWC match first
        if (
            work_iswc
            and uploaded_iswc
            and work_iswc.upper() == uploaded_iswc.upper()
        ):
            return MatchResult(
                match_score=Decimal("1.0000"),
                confidence_level=ConfidenceLevel.HIGH,
                title_similarity=Decimal("1.0000"),
                artist_similarity=Decimal("1.0000"),
                duration_similarity=Decimal("1.0000"),
            )

        # Calculate title similarity (required)
        title_score = combined_string_similarity(uploaded_title, work_title)

        # Calculate artist/contributors similarity
        if uploaded_artist and work_contributors:
            artist_score = jaro_winkler_similarity(uploaded_artist, work_contributors)
        else:
            # If artist is missing, use neutral score
            artist_score = 0.5

        # Calculate duration similarity
        if uploaded_duration is not None:
            # BWARM doesn't have duration on works, only on resources
            # Use neutral score for now
            duration_score = 0.5
        else:
            duration_score = 0.5

        # Year similarity placeholder (not implemented yet)
        year_score = 0.5

        # Calculate weighted final score
        final_score = (
            (title_score * self.TITLE_WEIGHT)
            + (artist_score * self.ARTIST_WEIGHT)
            + (duration_score * self.DURATION_WEIGHT)
            + (year_score * self.YEAR_WEIGHT)
        )

        # Determine confidence level
        confidence = self._determine_confidence(final_score)

        return MatchResult(
            match_score=Decimal(str(round(final_score, 4))),
            confidence_level=confidence,
            title_similarity=Decimal(str(round(title_score, 4))),
            artist_similarity=Decimal(str(round(artist_score, 4))),
            duration_similarity=Decimal(str(round(duration_score, 4))),
        )

    def _determine_confidence(self, score: float) -> ConfidenceLevel:
        """Determine confidence level based on score.

        Args:
            score: Match score (0.0 to 1.0)

        Returns:
            ConfidenceLevel enum value
        """
        if score >= self.HIGH_CONFIDENCE_THRESHOLD:
            return ConfidenceLevel.HIGH
        elif score >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def batch_score_candidates(
        self,
        uploaded_track: dict,
        candidate_works: list,
        max_results: int = 10,
    ) -> list[MatchResult]:
        """Score multiple candidate works and return top matches.

        Args:
            uploaded_track: Dict with title, artist, duration, iswc
            candidate_works: List of MusicalWork objects
            max_results: Maximum number of results to return

        Returns:
            List of MatchResults sorted by score (descending)
        """
        results = []

        for work in candidate_works:
            match_result = self.calculate_match_score(
                uploaded_title=uploaded_track.get("title", ""),
                uploaded_artist=uploaded_track.get("artist"),
                uploaded_duration=uploaded_track.get("duration"),
                work_title=work.title,
                work_contributors=work.contributors,
                work_iswc=work.iswc,
                uploaded_iswc=uploaded_track.get("iswc"),
            )

            # Attach work reference for later use
            match_result.work = work
            results.append(match_result)

        # Sort by score descending
        results.sort(key=lambda r: r.match_score, reverse=True)

        # Return top N results
        return results[:max_results]

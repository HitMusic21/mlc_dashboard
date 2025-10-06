"""CatalogMatch SQLModel for BWARM Dashboard.

Stores matching results between uploaded catalog tracks and BWARM works.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKey, Index, Numeric
from sqlmodel import Column, Field, SQLModel


class ConfidenceLevel(str, Enum):
    """Match confidence level enumeration."""

    HIGH = "high"  # >= 0.85
    MEDIUM = "medium"  # >= 0.70 and < 0.85
    LOW = "low"  # < 0.70


class CatalogMatch(SQLModel, table=True):
    """Catalog match entity storing matching results.

    Links uploaded tracks to matched musical works with confidence scores.
    """

    __tablename__ = "catalog_matches"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    catalog_upload_id: int = Field(
        foreign_key="catalog_uploads.id",
        index=True,
        nullable=False,
    )
    musical_work_id: int = Field(
        foreign_key="musical_works.id",
        index=True,
        nullable=False,
    )

    # Uploaded track data (denormalized for performance)
    uploaded_track_title: str = Field(max_length=500)
    uploaded_track_artist: Optional[str] = Field(default=None, max_length=500)
    uploaded_track_duration: Optional[int] = Field(default=None, ge=0)

    # Match scoring
    match_score: Decimal = Field(
        sa_column=Column(Numeric(5, 4)),
        ge=0.0,
        le=1.0,
    )
    confidence_level: ConfidenceLevel = Field(index=True)
    rank: int = Field(ge=1)  # Rank within upload (1 = best match)

    # Algorithm details (JSON or separate columns)
    title_similarity_score: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 4)),
    )
    artist_similarity_score: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 4)),
    )
    duration_similarity_score: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(Numeric(5, 4)),
    )

    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        # Index for upload results query
        Index(
            "idx_catalog_matches_upload_score",
            "catalog_upload_id",
            "match_score",
        ),
        # Index for confidence filtering
        Index(
            "idx_catalog_matches_upload_confidence",
            "catalog_upload_id",
            "confidence_level",
        ),
    )

    def __repr__(self) -> str:
        """String representation of CatalogMatch."""
        return (
            f"<CatalogMatch(id={self.id}, upload_id={self.catalog_upload_id}, "
            f"work_id={self.musical_work_id}, score={self.match_score})>"
        )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "uploaded_track_title": "Yesterday",
                "uploaded_track_artist": "Beatles",
                "uploaded_track_duration": 125,
                "match_score": 0.9543,
                "confidence_level": "high",
                "rank": 1,
            }
        }

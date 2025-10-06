"""Pydantic schemas for Catalog API endpoints."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.works import Pagination


class CatalogUploadResponse(BaseModel):
    """Response schema for catalog upload."""

    id: int
    filename: str
    file_format: str
    file_size_bytes: int
    publisher_name: str
    status: str
    progress_percentage: float = Field(ge=0, le=100)
    total_tracks: int = Field(ge=0)
    processed_tracks: int = Field(ge=0)
    matched_tracks: int = Field(ge=0)
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class CatalogUploadStatusResponse(BaseModel):
    """Response schema for upload status."""

    id: int
    status: str
    progress_percentage: float = Field(ge=0, le=100)
    estimated_time_remaining_seconds: Optional[int] = Field(ge=0, default=None)
    total_tracks: int = Field(ge=0)
    processed_tracks: int = Field(ge=0)
    matched_tracks: int = Field(ge=0)
    duplicate_tracks_merged: int = Field(ge=0)
    error_message: Optional[str] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class UploadedTrackSchema(BaseModel):
    """Schema for uploaded track data."""

    title: str
    artist: Optional[str] = None
    duration: Optional[int] = None


class CatalogMatchResponse(BaseModel):
    """Schema for individual match result."""

    work_id: int
    work_title: str
    work_iswc: Optional[str] = None
    confidence_score: Decimal = Field(ge=0, le=1)
    confidence_level: str
    rank: int = Field(ge=1, description="Rank within matches (1 = best)")
    title_similarity_score: Optional[Decimal] = Field(ge=0, le=1, default=None)
    artist_similarity_score: Optional[Decimal] = Field(ge=0, le=1, default=None)
    duration_similarity_score: Optional[Decimal] = Field(ge=0, le=1, default=None)


class MatchResultGroupResponse(BaseModel):
    """Schema for match result group (one uploaded track with its matches)."""

    uploaded_track: UploadedTrackSchema
    matches: List[CatalogMatchResponse] = Field(
        default_factory=list, description="Matches sorted by score (highest first)"
    )


class CatalogResultsResponse(BaseModel):
    """Response schema for GET /catalog/{id}/results."""

    data: List[MatchResultGroupResponse]
    pagination: Pagination


class CatalogUploadsListResponse(BaseModel):
    """Response schema for GET /catalog/uploads."""

    data: List[CatalogUploadResponse]
    pagination: Pagination

"""Pydantic schemas for Works API endpoints."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    """Pagination metadata."""

    page: int = Field(ge=1, description="Current page number")
    limit: int = Field(ge=1, le=1000, description="Items per page")
    total_items: int = Field(ge=0, description="Total number of items")
    total_pages: int = Field(ge=0, description="Total number of pages")


class ResponseMeta(BaseModel):
    """Response metadata."""

    response_time_ms: float = Field(ge=0, description="Response time in milliseconds")


class ResourceResponse(BaseModel):
    """Resource response schema."""

    id: int
    isrc: Optional[str] = None
    resource_type: str
    title: str
    artist: Optional[str] = None
    duration_seconds: Optional[int] = None
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class MusicalWorkResponse(BaseModel):
    """Musical work response schema for list endpoints."""

    id: int
    title: str
    iswc: Optional[str] = None
    contributors: Optional[str] = None
    publisher: Optional[str] = None
    territory: Optional[str] = None
    has_disputed_rights: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class MusicalWorkDetailedResponse(MusicalWorkResponse):
    """Detailed musical work response with resources."""

    resources: List[ResourceResponse] = []


class WorksListResponse(BaseModel):
    """Response schema for GET /works."""

    data: List[MusicalWorkResponse]
    pagination: Pagination
    meta: ResponseMeta


class WorkSearchRequest(BaseModel):
    """Request schema for POST /works/search."""

    query: str = Field(min_length=1, max_length=500, description="Search query")
    filters: Optional[dict] = Field(default=None, description="Additional filters")
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=50, ge=1, le=1000, description="Items per page")


class MusicalWorkSearchResult(MusicalWorkResponse):
    """Musical work search result with score."""

    search_score: float = Field(ge=0, description="Search relevance score")


class WorkSearchResponse(BaseModel):
    """Response schema for POST /works/search."""

    data: List[MusicalWorkSearchResult]
    pagination: Pagination
    meta: ResponseMeta

    class Config:
        """Pydantic config."""

        json_schema_extra = {"search_time_ms": 0}


class MonthlyTrendItem(BaseModel):
    """Monthly trend data point."""

    month: str = Field(description="Month in YYYY-MM format")
    count: int = Field(ge=0, description="Number of works")


class DashboardStatisticsResponse(BaseModel):
    """Response schema for GET /works/statistics."""

    total_works: int = Field(ge=0, description="Total number of works")
    works_with_iswc: int = Field(ge=0, description="Works with ISWC assigned")
    works_with_iswc_percentage: float = Field(
        default=0.0, ge=0, le=100, description="Percentage of works with ISWC"
    )
    disputed_works: int = Field(ge=0, description="Works with disputed rights")
    disputed_works_percentage: float = Field(
        default=0.0, ge=0, le=100, description="Percentage of works with disputed rights"
    )
    monthly_trend: List[MonthlyTrendItem] = Field(
        default_factory=list, description="Monthly work creation trend"
    )


class MLCStatisticsResponse(BaseModel):
    """Response schema for GET /works/statistics/mlc.

    MLC-specific business metrics for tracking royalty recovery opportunities.
    """

    unmatched_recordings: int = Field(
        ge=0, description="Recordings without rightsholder links"
    )
    unclaimed_shares: int = Field(
        ge=0, description="Works missing publisher information"
    )
    unclaimed_percentage: float = Field(
        default=0.0, ge=0, le=100, description="Percentage of unclaimed works"
    )
    low_confidence_matches: int = Field(
        ge=0, description="Matches requiring manual review"
    )
    estimated_unclaimed_value: int = Field(
        ge=0, description="Estimated unclaimed royalty value in USD"
    )
    claims_submitted: int = Field(
        ge=0, description="Claims submitted this month"
    )
    claims_value: int = Field(
        ge=0, description="Estimated value of submitted claims in USD"
    )

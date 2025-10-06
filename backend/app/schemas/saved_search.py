"""Pydantic schemas for saved search API."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class FilterCondition(BaseModel):
    """Individual filter condition schema."""

    field: str = Field(..., description="Field name to filter on")
    operator: Literal[
        "equals",
        "not_equals",
        "contains",
        "not_contains",
        "starts_with",
        "ends_with",
        "greater_than",
        "less_than",
        "greater_than_or_equal",
        "less_than_or_equal",
        "in",
        "not_in",
        "is_null",
        "is_not_null",
    ] = Field(..., description="Comparison operator")
    value: Any = Field(None, description="Filter value (can be any type)")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "field": "has_iswc",
                "operator": "equals",
                "value": False,
            }
        }


class FilterConfig(BaseModel):
    """Complete filter configuration with logic."""

    logic: Literal["AND", "OR"] = Field(default="AND", description="Filter logic operator")
    filters: List[FilterCondition] = Field(
        default_factory=list, description="List of filter conditions"
    )
    sort: Optional[Dict[str, str]] = Field(
        None, description="Sort configuration {field, order}"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "logic": "AND",
                "filters": [
                    {"field": "has_iswc", "operator": "equals", "value": False},
                    {"field": "title", "operator": "contains", "value": "love"},
                ],
                "sort": {"field": "created_at", "order": "desc"},
            }
        }


class SavedSearchCreate(BaseModel):
    """Schema for creating a new saved search."""

    name: str = Field(..., min_length=1, max_length=255, description="Search name")
    description: Optional[str] = Field(
        None, max_length=1000, description="Search description"
    )
    filter_config: FilterConfig = Field(..., description="Filter configuration")
    is_favorite: bool = Field(default=False, description="Mark as favorite")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "name": "Works without ISWC",
                "description": "Find all works missing ISWC codes",
                "filter_config": {
                    "logic": "AND",
                    "filters": [{"field": "has_iswc", "operator": "equals", "value": False}],
                },
                "is_favorite": False,
            }
        }


class SavedSearchUpdate(BaseModel):
    """Schema for updating a saved search (partial updates allowed)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    filter_config: Optional[FilterConfig] = None
    is_favorite: Optional[bool] = None

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "name": "Updated Search Name",
                "is_favorite": True,
            }
        }


class SavedSearchResponse(BaseModel):
    """Schema for saved search response."""

    id: int = Field(..., description="Search ID")
    user_id: int = Field(..., description="Owner user ID")
    name: str = Field(..., description="Search name")
    description: Optional[str] = Field(None, description="Search description")
    filter_config: Dict[str, Any] = Field(..., description="Filter configuration")
    is_preset: bool = Field(..., description="Is a system preset")
    is_favorite: bool = Field(..., description="Is marked as favorite")
    last_used_at: Optional[datetime] = Field(None, description="Last use timestamp")
    use_count: int = Field(..., description="Usage count")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "name": "Works without ISWC",
                "description": "Find all works missing ISWC codes",
                "filter_config": {
                    "logic": "AND",
                    "filters": [{"field": "has_iswc", "operator": "equals", "value": False}],
                },
                "is_preset": False,
                "is_favorite": True,
                "last_used_at": "2025-10-06T15:30:00Z",
                "use_count": 15,
                "created_at": "2025-10-01T10:00:00Z",
                "updated_at": "2025-10-06T15:30:00Z",
            }
        }


class SavedSearchListResponse(BaseModel):
    """Schema for list of saved searches."""

    total: int = Field(..., description="Total count")
    searches: List[SavedSearchResponse] = Field(..., description="List of searches")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "total": 5,
                "searches": [
                    {
                        "id": 1,
                        "user_id": 1,
                        "name": "Works without ISWC",
                        "description": "Find all works missing ISWC codes",
                        "filter_config": {
                            "logic": "AND",
                            "filters": [
                                {"field": "has_iswc", "operator": "equals", "value": False}
                            ],
                        },
                        "is_preset": False,
                        "is_favorite": True,
                        "last_used_at": "2025-10-06T15:30:00Z",
                        "use_count": 15,
                        "created_at": "2025-10-01T10:00:00Z",
                        "updated_at": "2025-10-06T15:30:00Z",
                    }
                ],
            }
        }

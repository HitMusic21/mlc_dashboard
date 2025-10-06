"""Pydantic schemas for user preferences API."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class DashboardLayoutConfig(BaseModel):
    """Dashboard layout configuration schema."""

    widgets: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Array of widget configurations with positions",
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "widgets": [
                    {"id": "stat-card-1", "position": {"x": 0, "y": 0, "w": 6, "h": 2}},
                    {"id": "chart-panel", "position": {"x": 0, "y": 2, "w": 12, "h": 4}},
                ]
            }
        }


class SavedSearchSchema(BaseModel):
    """Saved search configuration schema."""

    id: Optional[str] = Field(None, description="Search ID (auto-generated if not provided)")
    name: str = Field(..., min_length=1, max_length=100, description="Search name")
    filters: dict[str, Any] = Field(..., description="Filter configuration")
    created_at: Optional[datetime] = Field(
        None, description="Creation timestamp (auto-generated)"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "id": "search-1",
                "name": "Disputed Rights",
                "filters": {"has_disputed_rights": True, "created_after": "2025-01-01"},
                "created_at": "2025-01-15T10:30:00Z",
            }
        }


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences (partial updates allowed)."""

    dashboard_layout: Optional[DashboardLayoutConfig] = None
    saved_searches: Optional[list[SavedSearchSchema]] = None
    theme: Optional[str] = Field(None, pattern="^(light|dark|auto)$")
    items_per_page: Optional[int] = Field(None, ge=10, le=200)
    notification_email: Optional[bool] = None
    notification_push: Optional[bool] = None
    language: Optional[str] = Field(None, min_length=2, max_length=10)
    timezone: Optional[str] = Field(None, min_length=1, max_length=50)

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        """Validate ISO 639-1 language code format."""
        if v and len(v) not in (2, 5):  # en or en-US
            raise ValueError("Language must be ISO 639-1 format (e.g., 'en' or 'en-US')")
        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "theme": "dark",
                "items_per_page": 100,
                "notification_email": False,
            }
        }


class UserPreferencesResponse(BaseModel):
    """Schema for user preferences response."""

    id: UUID
    user_id: int
    dashboard_layout: Optional[DashboardLayoutConfig] = None
    saved_searches: Optional[list[SavedSearchSchema]] = None
    theme: str
    items_per_page: int
    notification_email: bool
    notification_push: bool
    language: str
    timezone: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987e4567-e89b-12d3-a456-426614174999",
                "dashboard_layout": {
                    "widgets": [
                        {"id": "stat-card-1", "position": {"x": 0, "y": 0, "w": 6, "h": 2}}
                    ]
                },
                "saved_searches": [
                    {
                        "id": "search-1",
                        "name": "Disputed Rights",
                        "filters": {"has_disputed_rights": True},
                        "created_at": "2025-01-15T10:30:00Z",
                    }
                ],
                "theme": "dark",
                "items_per_page": 100,
                "notification_email": True,
                "notification_push": False,
                "language": "en",
                "timezone": "America/New_York",
                "created_at": "2025-01-10T08:00:00Z",
                "updated_at": "2025-01-15T14:30:00Z",
            }
        }


class LayoutUpdateRequest(BaseModel):
    """Schema for dashboard layout update request."""

    layout: DashboardLayoutConfig = Field(..., description="New dashboard layout configuration")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "layout": {
                    "widgets": [
                        {"id": "stat-card-1", "position": {"x": 0, "y": 0, "w": 6, "h": 2}},
                        {"id": "chart-panel", "position": {"x": 6, "y": 0, "w": 6, "h": 4}},
                    ]
                }
            }
        }


class SavedSearchCreateRequest(BaseModel):
    """Schema for creating a saved search."""

    name: str = Field(..., min_length=1, max_length=100)
    filters: dict[str, Any] = Field(..., description="Filter configuration object")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {"name": "High Value Works", "filters": {"min_value": 10000, "has_iswc": True}}
        }

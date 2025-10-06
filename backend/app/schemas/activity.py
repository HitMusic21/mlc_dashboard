"""Pydantic schemas for activity log API."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ActivityLogCreate(BaseModel):
    """Schema for creating an activity log entry."""

    user_id: Optional[UUID] = Field(None, description="User ID (null for system events)")
    action: str = Field(..., min_length=1, max_length=100, description="Action identifier")
    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[UUID] = None
    description: str = Field(..., min_length=1, max_length=500)
    log_metadata: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)
    status: str = Field(
        default="success", pattern="^(success|failure|partial)$"
    )

    @field_validator("action")
    @classmethod
    def validate_action_format(cls, v: str) -> str:
        """Validate action follows {entity}.{verb} format."""
        if "." not in v:
            raise ValueError("Action must follow format: {entity}.{verb} (e.g., 'catalog.upload')")
        parts = v.split(".")
        if len(parts) != 2 or not all(parts):
            raise ValueError("Action must have exactly one dot separating entity and verb")
        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "action": "catalog.upload",
                "entity_type": "catalog_upload",
                "entity_id": "987e4567-e89b-12d3-a456-426614174999",
                "description": "User uploaded catalog 'Publisher X - Q1 2025.csv'",
                "metadata": {
                    "filename": "Publisher X - Q1 2025.csv",
                    "file_size": 2048576,
                    "total_tracks": 1500,
                },
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "status": "success",
            }
        }


class ActivityLogResponse(BaseModel):
    """Schema for activity log response."""

    id: UUID
    user_id: Optional[UUID] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    description: str
    log_metadata: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "222e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "action": "catalog.upload",
                "entity_type": "catalog_upload",
                "entity_id": "987e4567-e89b-12d3-a456-426614174999",
                "description": "User uploaded catalog 'Publisher X - Q1 2025.csv'",
                "metadata": {
                    "filename": "Publisher X - Q1 2025.csv",
                    "file_size": 2048576,
                    "file_format": "csv",
                    "total_tracks": 1500,
                },
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                "status": "success",
                "created_at": "2025-01-15T14:25:00Z",
            }
        }


class ActivityStatsResponse(BaseModel):
    """Schema for activity statistics response."""

    total_actions: int = Field(..., ge=0)
    actions_by_type: dict[str, int] = Field(
        default_factory=dict, description="Count of actions by type"
    )
    recent_activities: list[ActivityLogResponse] = Field(
        default_factory=list, description="Last 10 activities"
    )
    most_common_actions: list[dict[str, Any]] = Field(
        default_factory=list, description="Top 5 most common actions"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "total_actions": 1250,
                "actions_by_type": {
                    "catalog.upload": 450,
                    "search.execute": 320,
                    "user.login": 280,
                    "catalog.export_results": 200,
                },
                "recent_activities": [
                    {
                        "id": "222e4567-e89b-12d3-a456-426614174000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "action": "catalog.upload",
                        "entity_type": "catalog_upload",
                        "entity_id": "987e4567-e89b-12d3-a456-426614174999",
                        "description": "Uploaded catalog file",
                        "metadata": {"filename": "Q1-2025.csv"},
                        "ip_address": "192.168.1.100",
                        "user_agent": "Mozilla/5.0",
                        "status": "success",
                        "created_at": "2025-01-15T14:25:00Z",
                    }
                ],
                "most_common_actions": [
                    {"action": "catalog.upload", "count": 450},
                    {"action": "search.execute", "count": 320},
                    {"action": "user.login", "count": 280},
                ],
            }
        }

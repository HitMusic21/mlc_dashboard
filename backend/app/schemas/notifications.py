"""Pydantic schemas for notifications API."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""

    user_id: UUID
    type: str = Field(..., pattern="^(info|success|warning|error)$")
    severity: str = Field(
        default="low", pattern="^(low|medium|high|critical)$"
    )
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    related_entity_type: Optional[str] = Field(None, max_length=50)
    related_entity_id: Optional[UUID] = None
    action_url: Optional[str] = Field(None, max_length=500)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "success",
                "severity": "medium",
                "title": "Catalog Upload Complete",
                "message": "Your catalog has been processed successfully with 1,234 matches found.",
                "related_entity_type": "catalog_upload",
                "related_entity_id": "987e4567-e89b-12d3-a456-426614174999",
                "action_url": "/catalog/results/987e4567-e89b-12d3-a456-426614174999",
            }
        }


class NotificationResponse(BaseModel):
    """Schema for notification response."""

    id: UUID
    user_id: UUID
    type: str
    severity: str
    title: str
    message: str
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    action_url: Optional[str] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "111e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "success",
                "severity": "medium",
                "title": "Catalog Upload Complete",
                "message": "Your catalog 'Q1-2025.csv' processed: 1,234 matches found.",
                "related_entity_type": "catalog_upload",
                "related_entity_id": "987e4567-e89b-12d3-a456-426614174999",
                "action_url": "/catalog/results/987e4567-e89b-12d3-a456-426614174999",
                "is_read": False,
                "read_at": None,
                "created_at": "2025-01-15T14:30:00Z",
            }
        }


class NotificationListResponse(BaseModel):
    """Schema for paginated notifications list response."""

    notifications: list[NotificationResponse]
    total: int
    page: int
    limit: int
    has_more: bool

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "notifications": [
                    {
                        "id": "111e4567-e89b-12d3-a456-426614174000",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "type": "success",
                        "severity": "medium",
                        "title": "Catalog Upload Complete",
                        "message": "Processing complete with 1,234 matches.",
                        "related_entity_type": "catalog_upload",
                        "related_entity_id": "987e4567-e89b-12d3-a456-426614174999",
                        "action_url": "/catalog/results/987e4567-e89b-12d3-a456-426614174999",
                        "is_read": False,
                        "read_at": None,
                        "created_at": "2025-01-15T14:30:00Z",
                    }
                ],
                "total": 25,
                "page": 1,
                "limit": 20,
                "has_more": True,
            }
        }


class UnreadCountResponse(BaseModel):
    """Schema for unread notification count response."""

    count: int = Field(..., ge=0, description="Number of unread notifications")

    class Config:
        """Pydantic config."""

        json_schema_extra = {"example": {"count": 5}}


class MarkAllReadResponse(BaseModel):
    """Schema for mark all as read response."""

    marked_count: int = Field(..., ge=0, description="Number of notifications marked as read")

    class Config:
        """Pydantic config."""

        json_schema_extra = {"example": {"marked_count": 12}}


class ClearReadResponse(BaseModel):
    """Schema for clear read notifications response."""

    deleted_count: int = Field(..., ge=0, description="Number of read notifications deleted")

    class Config:
        """Pydantic config."""

        json_schema_extra = {"example": {"deleted_count": 8}}

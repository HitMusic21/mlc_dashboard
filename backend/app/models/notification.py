"""Notification model for user alerts and system messages."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Index


class NotificationType(str, Enum):
    """Notification type classification."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationSeverity(str, Enum):
    """Notification severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Notification(SQLModel, table=True):
    """User notification for events, status updates, and alerts.

    Tracks important events like upload completion, errors, and system alerts.
    Supports read/unread status, severity levels, and optional action URLs.
    """

    __tablename__ = "notifications"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign key
    user_id: int = Field(foreign_key="users.id", index=True)

    # Classification
    type: NotificationType = Field(default=NotificationType.INFO, index=True)
    severity: NotificationSeverity = Field(default=NotificationSeverity.LOW)

    # Content
    title: str = Field(max_length=200)
    message: str = Field(max_length=1000)

    # Related entity (optional)
    related_entity_type: Optional[str] = Field(default=None, max_length=50)
    related_entity_id: Optional[UUID] = Field(default=None, index=True)

    # Action
    action_url: Optional[str] = Field(default=None, max_length=500)

    # Status
    is_read: bool = Field(default=False, index=True)
    read_at: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    # user: Optional["User"] = Relationship(back_populates="notifications")

    __table_args__ = (
        # Composite index for efficient unread queries
        Index(
            "ix_notifications_user_unread",
            "user_id",
            "is_read",
            "created_at",
            postgresql_using="btree",
        ),
        # Index for user's notification feed (all notifications)
        Index(
            "ix_notifications_user_feed", "user_id", "created_at", postgresql_using="btree"
        ),
        # Index for cleanup operations
        Index("ix_notifications_created_at", "created_at", postgresql_using="btree"),
    )

    def mark_as_read(self) -> None:
        """Mark notification as read with timestamp."""
        self.is_read = True
        self.read_at = datetime.utcnow()

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "success",
                "severity": "medium",
                "title": "Catalog Upload Complete",
                "message": "Your catalog 'Publisher X - Q1 2025.csv' has been processed successfully. Found 1,234 matches.",
                "related_entity_type": "catalog_upload",
                "related_entity_id": "987e4567-e89b-12d3-a456-426614174999",
                "action_url": "/catalog/results/987e4567-e89b-12d3-a456-426614174999",
                "is_read": False,
                "read_at": None,
                "created_at": "2025-01-15T14:30:00Z",
            }
        }

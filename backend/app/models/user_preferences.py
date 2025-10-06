"""User preferences model for dashboard customization and app settings."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, JSON, Relationship, SQLModel
from sqlalchemy import Index


class ThemeEnum(str, Enum):
    """UI theme options."""

    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class UserPreferences(SQLModel, table=True):
    """User preferences for dashboard layout, theme, and application settings.

    Stores user-specific customizations including dashboard widget layout,
    saved searches, theme preference, pagination settings, and notification preferences.
    """

    __tablename__ = "user_preferences"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign key - one-to-one relationship with User
    user_id: int = Field(foreign_key="users.id", unique=True)

    # Dashboard customization
    dashboard_layout: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    saved_searches: Optional[list] = Field(default=None, sa_column=Column(JSON))

    # UI preferences
    theme: ThemeEnum = Field(default=ThemeEnum.LIGHT)
    items_per_page: int = Field(default=50, ge=10, le=200)

    # Notification preferences
    notification_email: bool = Field(default=True)
    notification_push: bool = Field(default=True)

    # Localization
    language: str = Field(default="en", max_length=10)
    timezone: str = Field(default="UTC", max_length=50)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    # user: Optional["User"] = Relationship(back_populates="preferences")

    __table_args__ = (
        # Ensure one preference per user
        Index("ix_user_preferences_user_id", "user_id", unique=True),
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "dashboard_layout": {
                    "widgets": [
                        {"id": "stat-card-1", "position": {"x": 0, "y": 0, "w": 6, "h": 2}},
                        {"id": "chart-panel", "position": {"x": 0, "y": 2, "w": 12, "h": 4}},
                    ]
                },
                "saved_searches": [
                    {
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
            }
        }

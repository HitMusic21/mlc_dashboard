"""Resource SQLModel for BWARM Dashboard.

Represents recordings or videos associated with musical works.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Index
from sqlmodel import Field, SQLModel


class ResourceType(str, Enum):
    """Resource type enumeration."""

    RECORDING = "recording"
    VIDEO = "video"


class Resource(SQLModel, table=True):
    """Resource entity representing recordings or videos.

    Resources are linked to MusicalWorks via WorkResourceLink.
    """

    __tablename__ = "resources"

    id: Optional[int] = Field(default=None, primary_key=True)
    isrc: Optional[str] = Field(default=None, index=True, max_length=12)
    resource_type: ResourceType = Field(index=True)

    # Metadata
    title: str = Field(min_length=1, max_length=500)
    artist: Optional[str] = Field(default=None, max_length=500)
    duration_seconds: Optional[int] = Field(default=None, ge=0)
    release_date: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    __table_args__ = (
        # Index for ISRC lookups
        Index("idx_resources_isrc", "isrc"),
        # Index for resource type filtering
        Index("idx_resources_type", "resource_type"),
    )

    def __repr__(self) -> str:
        """String representation of Resource."""
        return f"<Resource(id={self.id}, title='{self.title}', type='{self.resource_type}')>"

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "isrc": "USCA20100123",
                "resource_type": "recording",
                "title": "Yesterday (Remastered 2009)",
                "artist": "The Beatles",
                "duration_seconds": 125,
            }
        }

"""CatalogUpload SQLModel for BWARM Dashboard.

Tracks catalog file uploads and processing status.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKey, Index
from sqlmodel import Field, SQLModel


class UploadStatus(str, Enum):
    """Upload processing status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileFormat(str, Enum):
    """Supported file format enumeration."""

    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    XML = "xml"


class CatalogUpload(SQLModel, table=True):
    """Catalog upload entity tracking file processing.

    Stores metadata about uploaded catalog files and their processing status.
    """

    __tablename__ = "catalog_uploads"

    id: Optional[int] = Field(default=None, primary_key=True)

    # User relationship
    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
    )

    # File information
    filename: str = Field(max_length=255)
    file_format: FileFormat = Field(index=True)
    file_size_bytes: int = Field(ge=0)

    # Publisher information
    publisher_name: str = Field(max_length=255)

    # Processing status
    status: UploadStatus = Field(default=UploadStatus.PENDING, index=True)
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    estimated_time_remaining_seconds: Optional[int] = Field(default=None, ge=0)

    # Statistics
    total_tracks: int = Field(default=0, ge=0)
    processed_tracks: int = Field(default=0, ge=0)
    matched_tracks: int = Field(default=0, ge=0)
    duplicate_tracks_merged: int = Field(default=0, ge=0)

    # Error tracking
    error_message: Optional[str] = Field(default=None, max_length=2000)

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
    )
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    __table_args__ = (
        # Index for user's uploads query
        Index("idx_catalog_uploads_user_status", "user_id", "status"),
        # Index for date range queries
        Index("idx_catalog_uploads_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation of CatalogUpload."""
        return (
            f"<CatalogUpload(id={self.id}, filename='{self.filename}', "
            f"status='{self.status}')>"
        )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "filename": "publisher_catalog_2024.csv",
                "file_format": "csv",
                "file_size_bytes": 10485760,
                "publisher_name": "Sony Music Publishing",
                "status": "pending",
                "total_tracks": 5000,
            }
        }

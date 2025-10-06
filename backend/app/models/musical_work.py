"""MusicalWork SQLModel for BWARM Dashboard.

Represents a musical work in the BWARM database with metadata and rights information.
"""

from datetime import datetime
from os import environ
from typing import Optional

from sqlalchemy import Column, Index, String, text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlmodel import Field, SQLModel


class MusicalWork(SQLModel, table=True):
    """Musical work entity with metadata and rights information.

    Primary entity in the BWARM database representing musical compositions.
    Includes full-text search support via PostgreSQL tsvector.
    """

    __tablename__ = "musical_works"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=1, max_length=500)
    iswc: Optional[str] = Field(default=None, index=True, max_length=15)

    # Contributor information
    contributors: Optional[str] = Field(default=None, max_length=2000)
    publisher: Optional[str] = Field(default=None, max_length=500)

    # Territory and rights
    territory: Optional[str] = Field(default=None, max_length=2)
    has_disputed_rights: bool = Field(default=False, index=True)

    # Full-text search vector (PostgreSQL specific, falls back to String for SQLite)
    search_vector: Optional[str] = Field(
        default=None,
        sa_column=Column(
            TSVECTOR if "postgresql" in environ.get("DATABASE_URL", "sqlite") else String,
            nullable=True
        ),
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    __table_args__ = (
        # GIN index for full-text search
        Index("idx_musical_works_search_vector", "search_vector", postgresql_using="gin"),
        # Composite index for common queries
        Index("idx_musical_works_iswc_disputed", "iswc", "has_disputed_rights"),
        # Index for date range queries
        Index("idx_musical_works_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation of MusicalWork."""
        return f"<MusicalWork(id={self.id}, title='{self.title}', iswc='{self.iswc}')>"

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "title": "Yesterday",
                "iswc": "T-070.127.829-8",
                "contributors": "John Lennon, Paul McCartney",
                "publisher": "Sony/ATV Music Publishing",
                "territory": "US",
                "has_disputed_rights": False,
            }
        }

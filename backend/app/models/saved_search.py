"""SavedSearch SQLModel for BWARM Dashboard.

Represents user-defined search filters that can be saved and reused.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class SavedSearch(SQLModel, table=True):
    """Saved search entity for persisting filter configurations.

    Stores user-defined search criteria with flexible filter logic supporting
    AND/OR operations, field filters, and custom search parameters.
    """

    __tablename__ = "saved_searches"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Ownership
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)

    # Search metadata
    name: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)

    # Filter configuration (stored as JSON)
    # Example structure:
    # {
    #   "logic": "AND",  # or "OR"
    #   "filters": [
    #     {"field": "has_iswc", "operator": "equals", "value": true},
    #     {"field": "title", "operator": "contains", "value": "love"}
    #   ],
    #   "sort": {"field": "created_at", "order": "desc"}
    # }
    filter_config: Dict[str, Any] = Field(
        default={},
        sa_column=Column(JSON, nullable=False),
    )

    # Preset indicator
    is_preset: bool = Field(default=False, index=True)

    # Usage tracking
    last_used_at: Optional[datetime] = Field(default=None)
    use_count: int = Field(default=0)

    # Favorites
    is_favorite: bool = Field(default=False, index=True)

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

    def __repr__(self) -> str:
        """String representation of SavedSearch."""
        return f"<SavedSearch(id={self.id}, name='{self.name}', user_id={self.user_id})>"

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "name": "Works without ISWC",
                "description": "Find all works missing ISWC codes",
                "filter_config": {
                    "logic": "AND",
                    "filters": [
                        {"field": "has_iswc", "operator": "equals", "value": False},
                    ],
                },
                "is_favorite": False,
            }
        }

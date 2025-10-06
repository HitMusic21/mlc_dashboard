"""WorkResourceLink SQLModel for BWARM Dashboard.

Junction table for many-to-many relationship between MusicalWork and Resource.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlmodel import Field, SQLModel


class WorkResourceLink(SQLModel, table=True):
    """Junction table linking musical works to resources.

    Implements many-to-many relationship between MusicalWork and Resource entities.
    """

    __tablename__ = "work_resource_links"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign keys
    musical_work_id: int = Field(
        foreign_key="musical_works.id",
        index=True,
        nullable=False,
    )
    resource_id: int = Field(
        foreign_key="resources.id",
        index=True,
        nullable=False,
    )

    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        # Prevent duplicate links
        UniqueConstraint(
            "musical_work_id",
            "resource_id",
            name="uq_work_resource_link",
        ),
    )

    def __repr__(self) -> str:
        """String representation of WorkResourceLink."""
        return (
            f"<WorkResourceLink(work_id={self.musical_work_id}, "
            f"resource_id={self.resource_id})>"
        )

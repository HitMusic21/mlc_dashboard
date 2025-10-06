"""User SQLModel for BWARM Dashboard.

Represents application users with authentication and role-based access.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    """User role enumeration."""

    PUBLISHER = "publisher"
    ADMIN = "admin"


class User(SQLModel, table=True):
    """User entity with authentication and authorization.

    Stores user credentials and profile information. Passwords are hashed using bcrypt.
    """

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Authentication
    email: str = Field(index=True, unique=True, max_length=255)
    hashed_password: str = Field(max_length=255)

    # Profile
    full_name: str = Field(max_length=255)
    role: UserRole = Field(default=UserRole.PUBLISHER, index=True)
    is_active: bool = Field(default=True, index=True)

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
    last_login_at: Optional[datetime] = Field(default=None)

    __table_args__ = (
        # Ensure email uniqueness at database level
        UniqueConstraint("email", name="uq_users_email"),
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "email": "publisher@example.com",
                "full_name": "John Publisher",
                "role": "publisher",
                "is_active": True,
            }
        }

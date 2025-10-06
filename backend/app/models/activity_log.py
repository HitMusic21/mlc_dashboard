"""Activity log model for audit trail and user action tracking."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, JSON, Relationship, SQLModel
from sqlalchemy import Index


class ActivityStatus(str, Enum):
    """Activity execution status."""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


class ActivityLog(SQLModel, table=True):
    """Audit trail for user actions and system events.

    Records all significant user actions and system events for security,
    compliance, and debugging purposes. Includes metadata for detailed analysis.
    """

    __tablename__ = "activity_logs"

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign key (nullable for system events)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)

    # Action identification
    action: str = Field(max_length=100, index=True)
    entity_type: Optional[str] = Field(default=None, max_length=50)
    entity_id: Optional[UUID] = Field(default=None, index=True)

    # Description and metadata
    description: str = Field(max_length=500)
    log_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Client information
    ip_address: Optional[str] = Field(default=None, max_length=45)  # IPv4 or IPv6
    user_agent: Optional[str] = Field(default=None, max_length=500)

    # Status
    status: ActivityStatus = Field(default=ActivityStatus.SUCCESS)

    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    # user: Optional["User"] = Relationship(back_populates="activity_logs")

    __table_args__ = (
        # Index for user's activity history
        Index(
            "ix_activity_logs_user_history",
            "user_id",
            "created_at",
            postgresql_using="btree",
        ),
        # Index for action-specific queries
        Index(
            "ix_activity_logs_action_time",
            "action",
            "created_at",
            postgresql_using="btree",
        ),
        # Index for entity audit trail
        Index(
            "ix_activity_logs_entity",
            "entity_type",
            "entity_id",
            "created_at",
            postgresql_using="btree",
        ),
    )

    @classmethod
    def format_action(cls, entity: str, verb: str) -> str:
        """Format action string following standard pattern.

        Args:
            entity: Entity type (e.g., 'catalog', 'user', 'search')
            verb: Action verb (e.g., 'upload', 'login', 'execute')

        Returns:
            Formatted action string: '{entity}.{verb}'
        """
        return f"{entity}.{verb}"

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
                    "file_format": "csv",
                    "total_tracks": 1500,
                },
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "status": "success",
                "created_at": "2025-01-15T14:25:00Z",
            }
        }


# Common action constants for type safety
class Actions:
    """Common activity actions for consistent logging."""

    # User actions
    USER_LOGIN = ActivityLog.format_action("user", "login")
    USER_LOGOUT = ActivityLog.format_action("user", "logout")
    USER_REGISTER = ActivityLog.format_action("user", "register")
    USER_UPDATE_PROFILE = ActivityLog.format_action("user", "update_profile")

    # Catalog actions
    CATALOG_UPLOAD = ActivityLog.format_action("catalog", "upload")
    CATALOG_DELETE = ActivityLog.format_action("catalog", "delete")
    CATALOG_EXPORT_RESULTS = ActivityLog.format_action("catalog", "export_results")

    # Search actions
    SEARCH_EXECUTE = ActivityLog.format_action("search", "execute")
    FILTER_APPLY = ActivityLog.format_action("filter", "apply")

    # Preferences actions
    PREFERENCES_UPDATE = ActivityLog.format_action("preferences", "update")
    NOTIFICATION_MARK_READ = ActivityLog.format_action("notification", "mark_read")

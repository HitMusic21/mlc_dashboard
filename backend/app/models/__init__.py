"""SQLModel models for BWARM Dashboard.

All models must be imported here for Alembic autogenerate to detect them.
"""

from app.models.activity_log import Actions, ActivityLog, ActivityStatus
from app.models.catalog_match import CatalogMatch, ConfidenceLevel
from app.models.catalog_upload import CatalogUpload, FileFormat, UploadStatus
from app.models.musical_work import MusicalWork
from app.models.notification import Notification, NotificationSeverity, NotificationType
from app.models.resource import Resource, ResourceType
from app.models.saved_search import SavedSearch
from app.models.user import User, UserRole
from app.models.user_preferences import ThemeEnum, UserPreferences
from app.models.work_resource_link import WorkResourceLink

__all__ = [
    "MusicalWork",
    "Resource",
    "ResourceType",
    "WorkResourceLink",
    "User",
    "UserRole",
    "CatalogUpload",
    "UploadStatus",
    "FileFormat",
    "CatalogMatch",
    "ConfidenceLevel",
    "UserPreferences",
    "ThemeEnum",
    "Notification",
    "NotificationType",
    "NotificationSeverity",
    "ActivityLog",
    "ActivityStatus",
    "Actions",
    "SavedSearch",
]

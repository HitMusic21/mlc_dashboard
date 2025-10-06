"""Add user preferences, notifications, and activity log

Revision ID: 002
Revises: 001
Create Date: 2025-10-05 16:45:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create user_preferences table
    op.create_table(
        "user_preferences",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("dashboard_layout", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("saved_searches", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "theme",
            sa.Enum("light", "dark", "auto", name="themeenum"),
            nullable=False,
            server_default="light",
        ),
        sa.Column("items_per_page", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("notification_email", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("notification_push", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("language", sa.String(length=10), nullable=False, server_default="en"),
        sa.Column("timezone", sa.String(length=50), nullable=False, server_default="UTC"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_user_preferences_user_id"),
        sa.PrimaryKeyConstraint("id", name="pk_user_preferences"),
        sa.UniqueConstraint("user_id", name="uq_user_preferences_user_id"),
        sa.CheckConstraint(
            "items_per_page >= 10 AND items_per_page <= 200",
            name="ck_user_preferences_items_per_page",
        ),
    )
    op.create_index("ix_user_preferences_user_id", "user_preferences", ["user_id"], unique=True)

    # Create notifications table
    op.create_table(
        "notifications",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("info", "success", "warning", "error", name="notificationtype"),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.Enum("low", "medium", "high", "critical", name="notificationseverity"),
            nullable=False,
            server_default="low",
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("message", sa.String(length=1000), nullable=False),
        sa.Column("related_entity_type", sa.String(length=50), nullable=True),
        sa.Column("related_entity_id", sa.UUID(), nullable=True),
        sa.Column("action_url", sa.String(length=500), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_notifications_user_id"),
        sa.PrimaryKeyConstraint("id", name="pk_notifications"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_type", "notifications", ["type"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])
    op.create_index("ix_notifications_related_entity_id", "notifications", ["related_entity_id"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])
    op.create_index(
        "ix_notifications_user_unread",
        "notifications",
        ["user_id", "is_read", "created_at"],
        postgresql_using="btree",
    )
    op.create_index(
        "ix_notifications_user_feed",
        "notifications",
        ["user_id", "created_at"],
        postgresql_using="btree",
    )

    # Create activity_logs table
    op.create_table(
        "activity_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=True),
        sa.Column("entity_id", sa.UUID(), nullable=True),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("log_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column(
            "status",
            sa.Enum("success", "failure", "partial", name="activitystatus"),
            nullable=False,
            server_default="success",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_activity_logs_user_id"),
        sa.PrimaryKeyConstraint("id", name="pk_activity_logs"),
    )
    op.create_index("ix_activity_logs_user_id", "activity_logs", ["user_id"])
    op.create_index("ix_activity_logs_action", "activity_logs", ["action"])
    op.create_index("ix_activity_logs_entity_id", "activity_logs", ["entity_id"])
    op.create_index("ix_activity_logs_created_at", "activity_logs", ["created_at"])
    op.create_index(
        "ix_activity_logs_user_history",
        "activity_logs",
        ["user_id", "created_at"],
        postgresql_using="btree",
    )
    op.create_index(
        "ix_activity_logs_action_time",
        "activity_logs",
        ["action", "created_at"],
        postgresql_using="btree",
    )
    op.create_index(
        "ix_activity_logs_entity",
        "activity_logs",
        ["entity_type", "entity_id", "created_at"],
        postgresql_using="btree",
    )


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop activity_logs table and indexes
    op.drop_index("ix_activity_logs_entity", table_name="activity_logs")
    op.drop_index("ix_activity_logs_action_time", table_name="activity_logs")
    op.drop_index("ix_activity_logs_user_history", table_name="activity_logs")
    op.drop_index("ix_activity_logs_created_at", table_name="activity_logs")
    op.drop_index("ix_activity_logs_entity_id", table_name="activity_logs")
    op.drop_index("ix_activity_logs_action", table_name="activity_logs")
    op.drop_index("ix_activity_logs_user_id", table_name="activity_logs")
    op.drop_table("activity_logs")
    op.execute("DROP TYPE activitystatus")

    # Drop notifications table and indexes
    op.drop_index("ix_notifications_user_feed", table_name="notifications")
    op.drop_index("ix_notifications_user_unread", table_name="notifications")
    op.drop_index("ix_notifications_created_at", table_name="notifications")
    op.drop_index("ix_notifications_related_entity_id", table_name="notifications")
    op.drop_index("ix_notifications_is_read", table_name="notifications")
    op.drop_index("ix_notifications_type", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
    op.execute("DROP TYPE notificationseverity")
    op.execute("DROP TYPE notificationtype")

    # Drop user_preferences table and indexes
    op.drop_index("ix_user_preferences_user_id", table_name="user_preferences")
    op.drop_table("user_preferences")
    op.execute("DROP TYPE themeenum")

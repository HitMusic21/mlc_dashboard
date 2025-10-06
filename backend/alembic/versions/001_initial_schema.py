"""Initial schema with all models

Revision ID: 001
Revises:
Create Date: 2025-10-04

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply migration."""
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column(
            "hashed_password", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
        sa.Column("full_name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("role", sa.Enum("publisher", "admin", name="userrole"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)
    op.create_index(op.f("ix_users_is_active"), "users", ["is_active"], unique=False)

    # Create musical_works table
    op.create_table(
        "musical_works",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("iswc", sqlmodel.sql.sqltypes.AutoString(length=15), nullable=True),
        sa.Column("contributors", sqlmodel.sql.sqltypes.AutoString(length=2000), nullable=True),
        sa.Column("publisher", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("territory", sqlmodel.sql.sqltypes.AutoString(length=2), nullable=True),
        sa.Column("has_disputed_rights", sa.Boolean(), nullable=False),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_musical_works_title"), "musical_works", ["title"], unique=False)
    op.create_index(op.f("ix_musical_works_iswc"), "musical_works", ["iswc"], unique=False)
    op.create_index(
        op.f("ix_musical_works_has_disputed_rights"),
        "musical_works",
        ["has_disputed_rights"],
        unique=False,
    )
    op.create_index(
        "idx_musical_works_search_vector",
        "musical_works",
        ["search_vector"],
        unique=False,
        postgresql_using="gin",
    )
    op.create_index(
        "idx_musical_works_iswc_disputed",
        "musical_works",
        ["iswc", "has_disputed_rights"],
        unique=False,
    )
    op.create_index(
        "idx_musical_works_created_at", "musical_works", ["created_at"], unique=False
    )

    # Create resources table
    op.create_table(
        "resources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("isrc", sqlmodel.sql.sqltypes.AutoString(length=12), nullable=True),
        sa.Column(
            "resource_type", sa.Enum("recording", "video", name="resourcetype"), nullable=False
        ),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("artist", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("release_date", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_resources_isrc", "resources", ["isrc"], unique=False)
    op.create_index("idx_resources_type", "resources", ["resource_type"], unique=False)

    # Create work_resource_links table
    op.create_table(
        "work_resource_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("musical_work_id", sa.Integer(), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["musical_work_id"], ["musical_works.id"]),
        sa.ForeignKeyConstraint(["resource_id"], ["resources.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("musical_work_id", "resource_id", name="uq_work_resource_link"),
    )
    op.create_index(
        op.f("ix_work_resource_links_musical_work_id"),
        "work_resource_links",
        ["musical_work_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_work_resource_links_resource_id"),
        "work_resource_links",
        ["resource_id"],
        unique=False,
    )

    # Create catalog_uploads table
    op.create_table(
        "catalog_uploads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("filename", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column(
            "file_format",
            sa.Enum("csv", "excel", "json", "xml", name="fileformat"),
            nullable=False,
        ),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column(
            "publisher_name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "processing", "completed", "failed", name="uploadstatus"),
            nullable=False,
        ),
        sa.Column("progress_percentage", sa.Float(), nullable=False),
        sa.Column("estimated_time_remaining_seconds", sa.Integer(), nullable=True),
        sa.Column("total_tracks", sa.Integer(), nullable=False),
        sa.Column("processed_tracks", sa.Integer(), nullable=False),
        sa.Column("matched_tracks", sa.Integer(), nullable=False),
        sa.Column("duplicate_tracks_merged", sa.Integer(), nullable=False),
        sa.Column("error_message", sqlmodel.sql.sqltypes.AutoString(length=2000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_catalog_uploads_file_format"),
        "catalog_uploads",
        ["file_format"],
        unique=False,
    )
    op.create_index(op.f("ix_catalog_uploads_status"), "catalog_uploads", ["status"], unique=False)
    op.create_index(
        op.f("ix_catalog_uploads_user_id"), "catalog_uploads", ["user_id"], unique=False
    )
    op.create_index(
        "idx_catalog_uploads_user_status",
        "catalog_uploads",
        ["user_id", "status"],
        unique=False,
    )
    op.create_index(
        "idx_catalog_uploads_created_at", "catalog_uploads", ["created_at"], unique=False
    )

    # Create catalog_matches table
    op.create_table(
        "catalog_matches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("catalog_upload_id", sa.Integer(), nullable=False),
        sa.Column("musical_work_id", sa.Integer(), nullable=False),
        sa.Column(
            "uploaded_track_title", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False
        ),
        sa.Column(
            "uploaded_track_artist", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True
        ),
        sa.Column("uploaded_track_duration", sa.Integer(), nullable=True),
        sa.Column("match_score", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column(
            "confidence_level",
            sa.Enum("high", "medium", "low", name="confidencelevel"),
            nullable=False,
        ),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("title_similarity_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("artist_similarity_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("duration_similarity_score", sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["catalog_upload_id"], ["catalog_uploads.id"]),
        sa.ForeignKeyConstraint(["musical_work_id"], ["musical_works.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_catalog_matches_catalog_upload_id"),
        "catalog_matches",
        ["catalog_upload_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_catalog_matches_musical_work_id"),
        "catalog_matches",
        ["musical_work_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_catalog_matches_confidence_level"),
        "catalog_matches",
        ["confidence_level"],
        unique=False,
    )
    op.create_index(
        "idx_catalog_matches_upload_score",
        "catalog_matches",
        ["catalog_upload_id", "match_score"],
        unique=False,
    )
    op.create_index(
        "idx_catalog_matches_upload_confidence",
        "catalog_matches",
        ["catalog_upload_id", "confidence_level"],
        unique=False,
    )


def downgrade() -> None:
    """Revert migration."""
    op.drop_table("catalog_matches")
    op.drop_table("catalog_uploads")
    op.drop_table("work_resource_links")
    op.drop_table("resources")
    op.drop_table("musical_works")
    op.drop_table("users")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS confidencelevel")
    op.execute("DROP TYPE IF EXISTS uploadstatus")
    op.execute("DROP TYPE IF EXISTS fileformat")
    op.execute("DROP TYPE IF EXISTS resourcetype")
    op.execute("DROP TYPE IF EXISTS userrole")

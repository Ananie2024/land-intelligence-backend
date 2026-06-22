"""backup_jobs

Revision ID: 7b9c2d1e4f60
Revises: 929fabf1334d, 315a1f2b3c4d
Create Date: 2026-06-22 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision: str = "7b9c2d1e4f60"
down_revision: Union[str, tuple[str, str], None] = (
    "929fabf1334d",
    "315a1f2b3c4d",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "backup_jobs",
        sa.Column("job_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="PENDING", nullable=False),
        sa.Column("tier", sa.String(length=50), nullable=False),
        sa.Column("source_path", sa.String(length=1000), nullable=True),
        sa.Column("destination_path", sa.String(length=1000), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("file_count", sa.BigInteger(), nullable=True),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("id", mysql.CHAR(length=36), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_backup_jobs_status", "backup_jobs", ["status"], unique=False)
    op.create_index("ix_backup_jobs_tier", "backup_jobs", ["tier"], unique=False)
    op.create_index("ix_backup_jobs_created_at", "backup_jobs", ["created_at"], unique=False)

    op.create_table(
        "backup_verifications",
        sa.Column("backup_job_id", mysql.CHAR(length=36), nullable=False),
        sa.Column("verified_at", sa.DateTime(), nullable=True),
        sa.Column("verified_by", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="PENDING", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("id", mysql.CHAR(length=36), nullable=False),
        sa.ForeignKeyConstraint(["backup_job_id"], ["backup_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_backup_verifications_backup_job_id",
        "backup_verifications",
        ["backup_job_id"],
        unique=False,
    )
    op.create_index(
        "ix_backup_verifications_status",
        "backup_verifications",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_backup_verifications_status", table_name="backup_verifications")
    op.drop_index("ix_backup_verifications_backup_job_id", table_name="backup_verifications")
    op.drop_table("backup_verifications")
    op.drop_index("ix_backup_jobs_created_at", table_name="backup_jobs")
    op.drop_index("ix_backup_jobs_tier", table_name="backup_jobs")
    op.drop_index("ix_backup_jobs_status", table_name="backup_jobs")
    op.drop_table("backup_jobs")

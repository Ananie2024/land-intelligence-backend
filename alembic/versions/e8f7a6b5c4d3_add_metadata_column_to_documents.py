"""add_metadata_column_to_documents

Revision ID: e8f7a6b5c4d3
Revises: 032eaed0a76e
Create Date: 2026-07-17 12:36:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8f7a6b5c4d3'
down_revision: Union[str, None] = 'simplify_parish_entity_20260716'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add metadata column to documents table."""
    op.add_column('documents', sa.Column('metadata', sa.JSON(), nullable=True, comment='JSON field for additional attributes'))


def downgrade() -> None:
    """Remove metadata column from documents table."""
    op.drop_column('documents', 'metadata')
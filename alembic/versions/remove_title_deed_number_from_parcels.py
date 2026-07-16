"""remove_title_deed_number_from_parcels

Revision ID: remove_title_deed_number
Revises: b2c3d4e5f6a7
Create Date: 2026-07-16 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'remove_title_deed_number'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the idx_title_deed index first
    op.drop_index('idx_title_deed', table_name='parcels')
    
    # Drop the title_deed_number column
    op.drop_column('parcels', 'title_deed_number')


def downgrade() -> None:
    # Re-add the title_deed_number column
    op.add_column('parcels', sa.Column('title_deed_number', sa.String(100), nullable=True))
    
    # Recreate the index
    op.create_index('idx_title_deed', 'parcels', ['title_deed_number'])
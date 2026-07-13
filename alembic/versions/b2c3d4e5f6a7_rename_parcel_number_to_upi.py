"""rename_parcel_number_to_upi
 
Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-13 15:33:00.000000
 
"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename parcel_number column to upi in parcels table
    op.alter_column('parcels', 'parcel_number', new_column_name='upi')
    
    # Rename idx_parcel_number to idx_parcel_upi
    op.drop_index('idx_parcel_number', table_name='parcels')
    op.create_index('idx_parcel_upi', 'parcels', ['upi'], unique=True)


def downgrade() -> None:
    # Rename upi column back to parcel_number
    op.alter_column('parcels', 'upi', new_column_name='parcel_number')
    
    # Rename idx_parcel_upi back to idx_parcel_number
    op.drop_index('idx_parcel_upi', table_name='parcels')
    op.create_index('idx_parcel_number', 'parcels', ['parcel_number'], unique=True)
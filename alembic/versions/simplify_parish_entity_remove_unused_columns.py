"""
Simplify Parish Entity - Remove Unused Columns
Land Intelligence System

This migration removes the bulky contact and metadata fields from the parish table
since other data is kept in other systems.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'simplify_parish_entity_20260716'
down_revision = '032eaed0a76e'  # After merge migration
branch_labels = None
depends_on = None


def upgrade():
    """Remove unused parish columns."""
    # Drop columns that are no longer needed
    op.drop_column('parishes', 'contact_email')
    op.drop_column('parishes', 'contact_phone')
    op.drop_column('parishes', 'contact_person')
    op.drop_column('parishes', 'address')
    op.drop_column('parishes', 'description')
    op.drop_column('parishes', 'code')
    op.drop_column('parishes', 'parcel_count')
    op.drop_column('parishes', 'boundary_wkb')


def downgrade():
    """Restore parish columns for rollback."""
    op.add_column('parishes', sa.Column('boundary_wkb', sa.Text(), nullable=True))
    op.add_column('parishes', sa.Column('parcel_count', sa.Integer(), server_default='0', nullable=False))
    op.add_column('parishes', sa.Column('code', sa.String(20), nullable=False, unique=True))
    op.add_column('parishes', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('parishes', sa.Column('address', sa.String(500), nullable=True))
    op.add_column('parishes', sa.Column('contact_person', sa.String(200), nullable=True))
    op.add_column('parishes', sa.Column('contact_phone', sa.String(50), nullable=True))
    op.add_column('parishes', sa.Column('contact_email', sa.String(200), nullable=True))
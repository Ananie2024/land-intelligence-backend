"""initial_schema_full

Revision ID: c2341b14cb56
Revises: 929fabf1334d
Create Date: 2026-06-16 16:28:18.865873

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'c2341b14cb56'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create document_types
    op.create_table('document_types',
        sa.Column('id', mysql.CHAR(length=36), nullable=False, comment='UUID primary key'),
        sa.Column('name', sa.String(length=100), nullable=False, comment="Type name (e.g., 'Title Deed', 'Survey Map')"),
        sa.Column('code', sa.String(length=20), nullable=False, comment="Unique type code (e.g., 'TITLE', 'MAP')"),
        sa.Column('description', sa.Text(), nullable=True, comment='Description of document type'),
        sa.Column('requires_verification', sa.Boolean(), server_default='0', nullable=False, comment='Whether documents of this type require verification'),
        sa.Column('retention_years', sa.String(length=10), server_default='PERMANENT', nullable=False, comment="Retention period in years or 'PERMANENT'"),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_document_types_name', 'document_types', ['name'], unique=True)
    op.create_index('ix_document_types_code', 'document_types', ['code'], unique=True)

    # 2. Create parishes
    op.create_table('parishes',
        sa.Column('id', mysql.CHAR(length=36), nullable=False, comment='UUID primary key'),
        sa.Column('name', sa.String(length=200), nullable=False, comment='Official parish name'),
        sa.Column('code', sa.String(length=20), nullable=False, comment='Unique parish code (e.g., PAR-001)'),
        sa.Column('description', sa.Text(), nullable=True, comment='Description of parish boundaries and history'),
        sa.Column('address', sa.String(length=500), nullable=True, comment='Physical address of parish office'),
        sa.Column('contact_person', sa.String(length=200), nullable=True, comment='Name of primary contact person'),
        sa.Column('contact_phone', sa.String(length=50), nullable=True, comment='Phone number for parish office'),
        sa.Column('contact_email', sa.String(length=200), nullable=True, comment='Email address for parish office'),
        sa.Column('parcel_count', sa.Integer(), server_default='0', nullable=False, comment='Cached count of active parcels in this parish'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_parishes_name', 'parishes', ['name'], unique=False)
    op.create_index('ix_parishes_code', 'parishes', ['code'], unique=True)

    # 3. Create land_use_categories
    op.create_table('land_use_categories',
        sa.Column('id', mysql.CHAR(length=36), nullable=False, comment='UUID primary key'),
        sa.Column('name', sa.String(length=100), nullable=False, comment="Category name (e.g., 'Residential', 'Agricultural')"),
        sa.Column('code', sa.String(length=20), nullable=False, comment="Unique category code (e.g., 'RES', 'AGR')"),
        sa.Column('description', sa.Text(), nullable=True, comment='Description of land use category'),
        sa.Column('base_tax_rate', sa.Float(), server_default='0.0', nullable=False, comment='Base tax rate per square meter'),
        sa.Column('tax_rate_unit', sa.String(length=20), server_default='per_sqm', nullable=False, comment="Unit for tax rate (e.g., 'per_sqm', 'flat')"),
        sa.Column('requires_approval', sa.Boolean(), server_default='0', nullable=False, comment='Whether this land use requires special approval'),
        sa.Column('zoning_restrictions', sa.Text(), nullable=True, comment='Any zoning restrictions applicable'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_land_use_categories_name', 'land_use_categories', ['name'], unique=True)
    op.create_index('ix_land_use_categories_code', 'land_use_categories', ['code'], unique=True)

    # 4. Create parcels
    op.create_table('parcels',
        sa.Column('id', mysql.CHAR(length=36), nullable=False, comment='UUID primary key'),
        sa.Column('parcel_number', sa.String(length=50), nullable=False, comment='Unique parcel identifier'),
        sa.Column('parish_id', mysql.CHAR(length=36), nullable=False, comment='Foreign key to parish'),
        sa.Column('land_use_category_id', mysql.CHAR(length=36), nullable=True, comment='Foreign key to land use category'),
        sa.Column('area_sqm', sa.Float(), nullable=False, comment='Area in square meters'),
        sa.Column('geometry_wkb', sa.Text(), nullable=True, comment='Spatial geometry in WKB format (hex)'),
        sa.Column('title_deed_number', sa.String(length=100), nullable=True, comment='Official title deed reference'),
        sa.Column('owner_name', sa.String(length=500), nullable=False, comment='Name of land owner'),
        sa.Column('owner_contact', sa.String(length=500), nullable=True, comment='Contact information for owner'),
        sa.Column('location_description', sa.Text(), nullable=True, comment='Text description of location'),
        sa.Column('valuation', sa.Float(), nullable=True, comment='Current valuation amount'),
        sa.Column('valuation_date', sa.String(length=10), nullable=True, comment='Date of last valuation'),
        sa.Column('metadata', sa.JSON(), nullable=True, comment='JSON field for additional attributes'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
        sa.ForeignKeyConstraint(['land_use_category_id'], ['land_use_categories.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['parish_id'], ['parishes.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('parcel_number')
    )
    op.create_index('idx_parcel_number', 'parcels', ['parcel_number'], unique=True)
    op.create_index('idx_owner_name', 'parcels', ['owner_name'], unique=False)
    op.create_index('idx_title_deed', 'parcels', ['title_deed_number'], unique=False)
    op.create_index('ix_parcels_parish_id', 'parcels', ['parish_id'], unique=False)
    op.create_index('ix_parcels_land_use_category_id', 'parcels', ['land_use_category_id'], unique=False)

    # 5. Create audit_logs
    op.create_table('audit_logs',
        sa.Column('id', mysql.CHAR(length=36), nullable=False, comment='UUID primary key'),
        sa.Column('table_name', sa.String(length=100), nullable=False, comment='Name of the table that was modified'),
        sa.Column('record_id', mysql.CHAR(length=36), nullable=False, comment='UUID of the record that was modified'),
        sa.Column('action', sa.String(length=20), nullable=False, comment='Type of action (CREATE, UPDATE, DELETE, SOFT_DELETE, RESTORE)'),
        sa.Column('old_value', sa.JSON(), nullable=True, comment='JSON representation of values before change'),
        sa.Column('new_value', sa.JSON(), nullable=True, comment='JSON representation of values after change'),
        sa.Column('performed_by', mysql.CHAR(length=36), nullable=False, comment='User ID who performed the action'),
        sa.Column('performed_at', sa.DateTime(), nullable=False, comment='Timestamp when action was performed'),
        sa.Column('ip_address', sa.String(length=45), nullable=True, comment='IP address of the client'),
        sa.Column('user_agent', sa.String(length=500), nullable=True, comment='User agent string from client'),
        sa.Column('correlation_id', sa.String(length=36), nullable=True, comment='Request correlation ID for tracing'),
        sa.Column('metadata', sa.JSON(), nullable=True, comment='JSON field for additional audit context'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_table_name', 'audit_logs', ['table_name'], unique=False)
    op.create_index('ix_audit_logs_record_id', 'audit_logs', ['record_id'], unique=False)
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'], unique=False)
    op.create_index('ix_audit_logs_performed_by', 'audit_logs', ['performed_by'], unique=False)
    op.create_index('ix_audit_logs_performed_at', 'audit_logs', ['performed_at'], unique=False)
    op.create_index('idx_audit_table_record', 'audit_logs', ['table_name', 'record_id'], unique=False)
    op.create_index('idx_audit_performed_by_date', 'audit_logs', ['performed_by', 'performed_at'], unique=False)
    op.create_index('idx_audit_action_date', 'audit_logs', ['action', 'performed_at'], unique=False)
    op.create_index('idx_audit_correlation', 'audit_logs', ['correlation_id'], unique=False)


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('parcels')
    op.drop_table('land_use_categories')
    op.drop_table('parishes')
    op.drop_table('document_types')

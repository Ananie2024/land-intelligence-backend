"""clean_postgresql_schema

Revision ID: a1b2c3d4e5f6
Revises: 
Create Date: 2026-06-25 12:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create document_types
    op.create_table(
        'document_types',
        sa.Column('id', sa.String(36), nullable=False, comment='UUID primary key'),
        sa.Column('name', sa.String(100), nullable=False, comment="Type name (e.g., 'Title Deed', 'Survey Map')"),
        sa.Column('code', sa.String(20), nullable=False, comment="Unique type code (e.g., 'TITLE', 'MAP')"),
        sa.Column('description', sa.Text(), nullable=True, comment='Description of document type'),
        sa.Column('requires_verification', sa.Boolean(), server_default=sa.text('false'), nullable=False, comment='Whether documents of this type require verification'),
        sa.Column('retention_years', sa.String(10), server_default='PERMANENT', nullable=False, comment="Retention period in years or 'PERMANENT'"),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_document_types_name', 'document_types', ['name'], unique=True)
    op.create_index('ix_document_types_code', 'document_types', ['code'], unique=True)

    # 2. Create parishes
    op.create_table(
        'parishes',
        sa.Column('id', sa.String(36), nullable=False, comment='UUID primary key'),
        sa.Column('name', sa.String(200), nullable=False, comment='Official parish name'),
        sa.Column('code', sa.String(20), nullable=False, comment='Unique parish code (e.g., PAR-001)'),
        sa.Column('description', sa.Text(), nullable=True, comment='Description of parish boundaries and history'),
        sa.Column('address', sa.String(500), nullable=True, comment='Physical address of parish office'),
        sa.Column('contact_person', sa.String(200), nullable=True, comment='Name of primary contact person'),
        sa.Column('contact_phone', sa.String(50), nullable=True, comment='Phone number for parish office'),
        sa.Column('contact_email', sa.String(200), nullable=True, comment='Email address for parish office'),
        sa.Column('parcel_count', sa.Integer(), server_default='0', nullable=False, comment='Cached count of active parcels in this parish'),
        sa.Column('boundary_wkb', Geometry(geometry_type='MULTIPOLYGON', srid=4326), nullable=True, comment='Spatial boundary of the parish (MULTIPOLYGON) in WGS84'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_parishes_name', 'parishes', ['name'], unique=False)
    op.create_index('ix_parishes_code', 'parishes', ['code'], unique=True)

    # 3. Create land_use_categories
    op.create_table(
        'land_use_categories',
        sa.Column('id', sa.String(36), nullable=False, comment='UUID primary key'),
        sa.Column('name', sa.String(100), nullable=False, comment="Category name (e.g., 'Residential', 'Agricultural')"),
        sa.Column('code', sa.String(20), nullable=False, comment="Unique category code (e.g., 'RES', 'AGR')"),
        sa.Column('description', sa.Text(), nullable=True, comment='Description of land use category'),
        sa.Column('base_tax_rate', sa.Float(), server_default='0.0', nullable=False, comment='Base tax rate per square meter'),
        sa.Column('tax_rate_unit', sa.String(20), server_default='per_sqm', nullable=False, comment="Unit for tax rate (e.g., 'per_sqm', 'flat')"),
        sa.Column('requires_approval', sa.Boolean(), server_default=sa.text('false'), nullable=False, comment='Whether this land use requires special approval'),
        sa.Column('zoning_restrictions', sa.Text(), nullable=True, comment='Any zoning restrictions applicable'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_land_use_categories_name', 'land_use_categories', ['name'], unique=True)
    op.create_index('ix_land_use_categories_code', 'land_use_categories', ['code'], unique=True)

    # 4. Create parcels
    op.create_table(
        'parcels',
        sa.Column('id', sa.String(36), nullable=False, comment='UUID primary key'),
        sa.Column('parcel_number', sa.String(50), nullable=False, comment='Unique parcel identifier'),
        sa.Column('parish_id', sa.String(36), nullable=False, comment='Foreign key to parish'),
        sa.Column('land_use_category_id', sa.String(36), nullable=True, comment='Foreign key to land use category'),
        sa.Column('area_sqm', sa.Float(), nullable=False, comment='Area in square meters'),
        sa.Column('geometry_wkb', Geometry(geometry_type='POLYGON', srid=4326), nullable=True, comment='Spatial geometry (POLYGON) in WGS84'),
        sa.Column('title_deed_number', sa.String(100), nullable=True, comment='Official title deed reference'),
        sa.Column('owner_name', sa.String(500), nullable=False, comment='Name of land owner'),
        sa.Column('owner_contact', sa.String(500), nullable=True, comment='Contact information for owner'),
        sa.Column('location_description', sa.Text(), nullable=True, comment='Text description of location'),
        sa.Column('valuation', sa.Float(), nullable=True, comment='Current valuation amount'),
        sa.Column('valuation_date', sa.String(10), nullable=True, comment='Date of last valuation'),
        sa.Column('metadata', sa.JSON(), nullable=True, comment='JSON field for additional attributes'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
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

    # 5. Create users
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), nullable=False, comment='UUID primary key'),
        sa.Column('email', sa.String(255), nullable=False, comment='User email address'),
        sa.Column('username', sa.String(100), nullable=False, comment='Unique username'),
        sa.Column('hashed_password', sa.String(255), nullable=False, comment='Bcrypt hashed password'),
        sa.Column('full_name', sa.String(255), nullable=True, comment='Full name of user'),
        sa.Column('role', sa.String(20), server_default='viewer', nullable=False, comment='User role (admin, client, viewer)'),
        sa.Column('parish_id', sa.String(36), nullable=True, comment='For clients, links to their parish'),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False, comment='Whether user account is active'),
        sa.Column('is_verified', sa.Boolean(), server_default=sa.text('false'), nullable=False, comment='Whether email is verified'),
        sa.Column('last_login', sa.DateTime(), nullable=True, comment='Last successful login timestamp'),
        sa.Column('failed_login_attempts', sa.String(10), server_default='0', nullable=False, comment='Count of failed login attempts'),
        sa.Column('locked_until', sa.DateTime(), nullable=True, comment='Account locked until this timestamp'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

    # 6. Create audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), nullable=False, comment='UUID primary key'),
        sa.Column('table_name', sa.String(100), nullable=False, comment='Name of the table that was modified'),
        sa.Column('record_id', sa.String(36), nullable=False, comment='UUID of the record that was modified'),
        sa.Column('action', sa.String(20), nullable=False, comment='Type of action (CREATE, UPDATE, DELETE, SOFT_DELETE, RESTORE)'),
        sa.Column('old_value', sa.JSON(), nullable=True, comment='JSON representation of values before change'),
        sa.Column('new_value', sa.JSON(), nullable=True, comment='JSON representation of values after change'),
        sa.Column('performed_by', sa.String(36), nullable=False, comment='User ID who performed the action'),
        sa.Column('performed_at', sa.DateTime(), nullable=False, comment='Timestamp when action was performed'),
        sa.Column('ip_address', sa.String(45), nullable=True, comment='IP address of the client'),
        sa.Column('user_agent', sa.String(500), nullable=True, comment='User agent string from client'),
        sa.Column('correlation_id', sa.String(36), nullable=True, comment='Request correlation ID for tracing'),
        sa.Column('metadata', sa.JSON(), nullable=True, comment='JSON field for additional audit context'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
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

    # 7. Create documents
    op.create_table(
        'documents',
        sa.Column('id', sa.String(36), nullable=False, comment='UUID primary key'),
        sa.Column('parcel_id', sa.String(36), nullable=True, comment='Foreign key to parcel (optional)'),
        sa.Column('document_type_id', sa.String(36), nullable=False, comment='Foreign key to document type'),
        sa.Column('filename', sa.String(500), nullable=False, comment='Original filename'),
        sa.Column('file_path', sa.String(500), nullable=False, comment='Path to file on filesystem'),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False, comment='Size of file in bytes'),
        sa.Column('mime_type', sa.String(100), nullable=False, comment='MIME type of file'),
        sa.Column('description', sa.Text(), nullable=True, comment='Document description'),
        sa.Column('document_date', sa.Date(), nullable=True, comment='Document date (issue/recording date)'),
        sa.Column('reference_number', sa.String(200), nullable=True, comment='Official reference number'),
        sa.Column('page_count', sa.Integer(), nullable=True, comment='Number of pages (for PDF)'),
        sa.Column('checksum', sa.String(64), nullable=False, comment='SHA-256 checksum for integrity'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False, comment='Soft delete flag: True if record is active, False if deleted'),
        sa.ForeignKeyConstraint(['document_type_id'], ['document_types.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['parcel_id'], ['parcels.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('file_path')
    )
    op.create_index('idx_document_date', 'documents', ['document_date'], unique=False)
    op.create_index('idx_filename', 'documents', ['filename'], unique=False)
    op.create_index('idx_reference_number', 'documents', ['reference_number'], unique=False)
    op.create_index('ix_documents_document_type_id', 'documents', ['document_type_id'], unique=False)
    op.create_index('ix_documents_parcel_id', 'documents', ['parcel_id'], unique=False)
    op.create_index('ix_documents_reference_number', 'documents', ['reference_number'], unique=False)

    # 8. Create tax_records
    op.create_table(
        'tax_records',
        sa.Column('id', sa.String(36), nullable=False, comment='UUID primary key'),
        sa.Column('parcel_id', sa.String(36), nullable=False, comment='Foreign key to parcel'),
        sa.Column('assessment_year', sa.String(4), nullable=False, comment="Year of tax assessment (e.g., '2024')"),
        sa.Column('assessed_value', sa.Float(), server_default='0.0', nullable=False, comment='Assessed value of parcel for tax purposes'),
        sa.Column('tax_rate_applied', sa.Float(), server_default='0.0', nullable=False, comment='Tax rate applied for this assessment'),
        sa.Column('base_tax_amount', sa.Float(), server_default='0.0', nullable=False, comment='Base tax amount calculated'),
        sa.Column('penalties_amount', sa.Float(), server_default='0.0', nullable=False, comment='Penalties amount if any'),
        sa.Column('total_amount', sa.Float(), server_default='0.0', nullable=False, comment='Total tax amount due (base + penalties)'),
        sa.Column('status', sa.String(20), server_default='pending', nullable=False, comment='Status of tax record (pending, paid, overdue)'),
        sa.Column('due_date', sa.Date(), nullable=False, comment='Due date for payment'),
        sa.Column('paid_date', sa.Date(), nullable=True, comment='Date when fully paid (if applicable)'),
        sa.Column('payment_reference', sa.String(100), nullable=True, comment='Reference for full payment'),
        sa.Column('notes', sa.String(500), nullable=True, comment='Additional notes about tax assessment'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False, comment='Soft delete flag: True if record is active, False if deleted'),
        sa.ForeignKeyConstraint(['parcel_id'], ['parcels.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_assessment_year', 'tax_records', ['assessment_year'], unique=False)
    op.create_index('idx_due_date', 'tax_records', ['due_date'], unique=False)
    op.create_index('idx_status', 'tax_records', ['status'], unique=False)
    op.create_index('idx_unique_parcel_year', 'tax_records', ['parcel_id', 'assessment_year'], unique=True)
    op.create_index('ix_tax_records_assessment_year', 'tax_records', ['assessment_year'], unique=False)
    op.create_index('ix_tax_records_parcel_id', 'tax_records', ['parcel_id'], unique=False)
    op.create_index('ix_tax_records_status', 'tax_records', ['status'], unique=False)

    # 9. Create physical_locations
    op.create_table(
        'physical_locations',
        sa.Column('id', sa.String(36), nullable=False, comment='UUID primary key'),
        sa.Column('document_id', sa.String(36), nullable=True, comment='Foreign key to document (optional, for direct document location)'),
        sa.Column('name', sa.String(200), nullable=False, comment="Location name (e.g., 'Main Archive Room', 'Basement Storage')"),
        sa.Column('location_code', sa.String(50), nullable=False, comment="Unique location code (e.g., 'ARC-01', 'BSM-02')"),
        sa.Column('building', sa.String(100), nullable=True, comment='Building name or number'),
        sa.Column('floor', sa.String(50), nullable=True, comment='Floor level'),
        sa.Column('room_number', sa.String(50), nullable=True, comment='Room number or identifier'),
        sa.Column('description', sa.Text(), nullable=True, comment='Description of location and access instructions'),
        sa.Column('environmental_notes', sa.Text(), nullable=True, comment='Notes about environmental conditions (humidity, temperature)'),
        sa.Column('access_restrictions', sa.Text(), nullable=True, comment='Any access restrictions or security requirements'),
        sa.Column('contact_person', sa.String(200), nullable=True, comment='Person responsible for this location'),
        sa.Column('contact_phone', sa.String(50), nullable=True, comment='Contact phone number'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False, comment='Soft delete flag: True if record is active, False if deleted'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_building_floor', 'physical_locations', ['building', 'floor'], unique=False)
    op.create_index('idx_location_code', 'physical_locations', ['location_code'], unique=False)
    op.create_index('ix_physical_locations_document_id', 'physical_locations', ['document_id'], unique=True)
    op.create_index('ix_physical_locations_location_code', 'physical_locations', ['location_code'], unique=True)

    # 10. Create qr_code_registry
    op.create_table(
        'qr_code_registry',
        sa.Column('id', sa.String(36), nullable=False, comment='UUID primary key'),
        sa.Column('parcel_id', sa.String(36), nullable=True, comment='Foreign key to parcel (optional)'),
        sa.Column('document_id', sa.String(36), nullable=True, comment='Foreign key to document (optional)'),
        sa.Column('code', sa.String(255), nullable=False, comment='Unique QR code string'),
        sa.Column('code_type', sa.String(20), nullable=False, comment='Type of entity this QR code points to (parcel, document)'),
        sa.Column('file_path', sa.String(500), nullable=False, comment='Path to QR code image file'),
        sa.Column('data_payload', sa.JSON(), nullable=False, comment='JSON data encoded in QR code'),
        sa.Column('expires_at', sa.DateTime(), nullable=True, comment='Expiration timestamp (if temporary)'),
        sa.Column('last_accessed_at', sa.DateTime(), nullable=True, comment='Last time this QR was scanned'),
        sa.Column('access_count', sa.Integer(), server_default='0', nullable=False, comment='Number of times QR has been accessed'),
        sa.Column('is_revoked', sa.Boolean(), server_default=sa.text('false'), nullable=False, comment='Whether this QR code has been revoked'),
        sa.Column('metadata', sa.JSON(), nullable=True, comment='JSON field for additional attributes'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False, comment='Soft delete flag: True if record is active, False if deleted'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parcel_id'], ['parcels.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_code_type', 'qr_code_registry', ['code_type'], unique=False)
    op.create_index('idx_expires_at', 'qr_code_registry', ['expires_at'], unique=False)
    op.create_index('idx_is_revoked', 'qr_code_registry', ['is_revoked'], unique=False)
    op.create_index('ix_qr_code_registry_code', 'qr_code_registry', ['code'], unique=True)
    op.create_index('ix_qr_code_registry_code_type', 'qr_code_registry', ['code_type'], unique=False)
    op.create_index('ix_qr_code_registry_document_id', 'qr_code_registry', ['document_id'], unique=False)
    op.create_index('ix_qr_code_registry_expires_at', 'qr_code_registry', ['expires_at'], unique=False)
    op.create_index('ix_qr_code_registry_parcel_id', 'qr_code_registry', ['parcel_id'], unique=False)

    # 11. Create tax_payments
    op.create_table(
        'tax_payments',
        sa.Column('id', sa.String(36), nullable=False, comment='UUID primary key'),
        sa.Column('tax_record_id', sa.String(36), nullable=False, comment='Foreign key to tax record'),
        sa.Column('payment_amount', sa.Float(), nullable=False, comment='Amount paid in this transaction'),
        sa.Column('payment_date', sa.Date(), nullable=False, comment='Date of payment'),
        sa.Column('payment_method', sa.String(50), nullable=False, comment='Method of payment (cash, bank_transfer, check)'),
        sa.Column('payment_reference', sa.String(100), nullable=True, comment='External payment reference number'),
        sa.Column('receipt_number', sa.String(50), nullable=False, comment='Generated receipt number'),
        sa.Column('received_by', sa.String(200), nullable=False, comment='Name/ID of person who received payment'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Additional notes about payment'),
        sa.Column('is_reversal', sa.Boolean(), server_default=sa.text('false'), nullable=False, comment='Whether this is a reversal of a previous payment'),
        sa.Column('reversed_payment_id', sa.String(36), nullable=True, comment='Reference to reversed payment (if is_reversal=True)'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False, comment='Soft delete flag: True if record is active, False if deleted'),
        sa.ForeignKeyConstraint(['reversed_payment_id'], ['tax_payments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['tax_record_id'], ['tax_records.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_payment_date', 'tax_payments', ['payment_date'], unique=False)
    op.create_index('idx_payment_method', 'tax_payments', ['payment_method'], unique=False)
    op.create_index('idx_receipt_number', 'tax_payments', ['receipt_number'], unique=False)
    op.create_index('ix_tax_payments_payment_date', 'tax_payments', ['payment_date'], unique=False)
    op.create_index('ix_tax_payments_payment_reference', 'tax_payments', ['payment_reference'], unique=False)
    op.create_index('ix_tax_payments_receipt_number', 'tax_payments', ['receipt_number'], unique=True)
    op.create_index('ix_tax_payments_tax_record_id', 'tax_payments', ['tax_record_id'], unique=False)

    # 12. Create storage_cabinets
    op.create_table(
        'storage_cabinets',
        sa.Column('id', sa.String(36), nullable=False, comment='UUID primary key'),
        sa.Column('physical_location_id', sa.String(36), nullable=False, comment='Foreign key to physical location (room/building)'),
        sa.Column('cabinet_number', sa.String(50), nullable=False, comment="Cabinet identifier (e.g., 'CAB-001')"),
        sa.Column('cabinet_type', sa.String(50), server_default='filing', nullable=False, comment="Type of cabinet (e.g., 'filing', 'shelf', 'drawer')"),
        sa.Column('description', sa.Text(), nullable=True, comment='Description of cabinet contents/location'),
        sa.Column('row_number', sa.Integer(), nullable=True, comment='Row number within location (if applicable)'),
        sa.Column('column_number', sa.Integer(), nullable=True, comment='Column number within location (if applicable)'),
        sa.Column('max_capacity', sa.Integer(), nullable=True, comment='Maximum document capacity'),
        sa.Column('current_count', sa.Integer(), server_default='0', nullable=False, comment='Current number of documents stored'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was created'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Timestamp when record was last updated'),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False, comment='Soft delete flag: True if record is active, False if deleted'),
        sa.ForeignKeyConstraint(['physical_location_id'], ['physical_locations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_cabinet_number', 'storage_cabinets', ['cabinet_number'], unique=False)
    op.create_index('idx_cabinet_type', 'storage_cabinets', ['cabinet_type'], unique=False)
    op.create_index('idx_unique_cabinet_per_location', 'storage_cabinets', ['physical_location_id', 'cabinet_number'], unique=True)
    op.create_index('ix_storage_cabinets_cabinet_number', 'storage_cabinets', ['cabinet_number'], unique=False)
    op.create_index('ix_storage_cabinets_physical_location_id', 'storage_cabinets', ['physical_location_id'], unique=False)

    # 13. Create backup_jobs
    op.create_table(
        'backup_jobs',
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='PENDING', nullable=False),
        sa.Column('tier', sa.String(length=50), nullable=False),
        sa.Column('source_path', sa.String(length=1000), nullable=True),
        sa.Column('destination_path', sa.String(length=1000), nullable=True),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('file_count', sa.BigInteger(), nullable=True),
        sa.Column('checksum', sa.String(length=128), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('id', sa.String(36), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_backup_jobs_status', 'backup_jobs', ['status'], unique=False)
    op.create_index('ix_backup_jobs_tier', 'backup_jobs', ['tier'], unique=False)
    op.create_index('ix_backup_jobs_created_at', 'backup_jobs', ['created_at'], unique=False)

    # 14. Create backup_verifications
    op.create_table(
        'backup_verifications',
        sa.Column('backup_job_id', sa.String(36), nullable=False),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('verified_by', sa.String(200), nullable=True),
        sa.Column('status', sa.String(20), server_default='PENDING', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('id', sa.String(36), nullable=False),
        sa.ForeignKeyConstraint(['backup_job_id'], ['backup_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_backup_verifications_backup_job_id', 'backup_verifications', ['backup_job_id'], unique=False)
    op.create_index('ix_backup_verifications_status', 'backup_verifications', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_backup_verifications_status', table_name='backup_verifications')
    op.drop_index('ix_backup_verifications_backup_job_id', table_name='backup_verifications')
    op.drop_table('backup_verifications')

    op.drop_index('ix_backup_jobs_created_at', table_name='backup_jobs')
    op.drop_index('ix_backup_jobs_tier', table_name='backup_jobs')
    op.drop_index('ix_backup_jobs_status', table_name='backup_jobs')
    op.drop_table('backup_jobs')

    op.drop_index('ix_storage_cabinets_physical_location_id', table_name='storage_cabinets')
    op.drop_index('ix_storage_cabinets_cabinet_number', table_name='storage_cabinets')
    op.drop_index('idx_unique_cabinet_per_location', table_name='storage_cabinets')
    op.drop_index('idx_cabinet_type', table_name='storage_cabinets')
    op.drop_index('idx_cabinet_number', table_name='storage_cabinets')
    op.drop_table('storage_cabinets')

    op.drop_index('ix_tax_payments_tax_record_id', table_name='tax_payments')
    op.drop_index('ix_tax_payments_receipt_number', table_name='tax_payments')
    op.drop_index('ix_tax_payments_payment_reference', table_name='tax_payments')
    op.drop_index('ix_tax_payments_payment_date', table_name='tax_payments')
    op.drop_index('idx_receipt_number', table_name='tax_payments')
    op.drop_index('idx_payment_method', table_name='tax_payments')
    op.drop_index('idx_payment_date', table_name='tax_payments')
    op.drop_table('tax_payments')

    op.drop_index('ix_qr_code_registry_parcel_id', table_name='qr_code_registry')
    op.drop_index('ix_qr_code_registry_expires_at', table_name='qr_code_registry')
    op.drop_index('ix_qr_code_registry_document_id', table_name='qr_code_registry')
    op.drop_index('ix_qr_code_registry_code_type', table_name='qr_code_registry')
    op.drop_index('ix_qr_code_registry_code', table_name='qr_code_registry')
    op.drop_index('idx_is_revoked', table_name='qr_code_registry')
    op.drop_index('idx_expires_at', table_name='qr_code_registry')
    op.drop_index('idx_code_type', table_name='qr_code_registry')
    op.drop_table('qr_code_registry')

    op.drop_index('ix_physical_locations_location_code', table_name='physical_locations')
    op.drop_index('ix_physical_locations_document_id', table_name='physical_locations')
    op.drop_index('idx_location_code', table_name='physical_locations')
    op.drop_index('idx_building_floor', table_name='physical_locations')
    op.drop_table('physical_locations')

    op.drop_index('ix_tax_records_status', table_name='tax_records')
    op.drop_index('ix_tax_records_parcel_id', table_name='tax_records')
    op.drop_index('ix_tax_records_assessment_year', table_name='tax_records')
    op.drop_index('idx_unique_parcel_year', table_name='tax_records')
    op.drop_index('idx_status', table_name='tax_records')
    op.drop_index('idx_due_date', table_name='tax_records')
    op.drop_index('idx_assessment_year', table_name='tax_records')
    op.drop_table('tax_records')

    op.drop_index('ix_documents_reference_number', table_name='documents')
    op.drop_index('ix_documents_parcel_id', table_name='documents')
    op.drop_index('ix_documents_document_type_id', table_name='documents')
    op.drop_index('idx_reference_number', table_name='documents')
    op.drop_index('idx_filename', table_name='documents')
    op.drop_index('idx_document_date', table_name='documents')
    op.drop_table('documents')

    op.drop_index('ix_audit_logs_table_name', table_name='audit_logs')
    op.drop_index('ix_audit_logs_record_id', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_index('ix_audit_logs_performed_by', table_name='audit_logs')
    op.drop_index('ix_audit_logs_performed_at', table_name='audit_logs')
    op.drop_index('idx_audit_table_record', table_name='audit_logs')
    op.drop_index('idx_audit_performed_by_date', table_name='audit_logs')
    op.drop_index('idx_audit_action_date', table_name='audit_logs')
    op.drop_index('idx_audit_correlation', table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')

    op.drop_index('ix_parcels_land_use_category_id', table_name='parcels')
    op.drop_index('ix_parcels_parish_id', table_name='parcels')
    op.drop_index('idx_title_deed', table_name='parcels')
    op.drop_index('idx_owner_name', table_name='parcels')
    op.drop_index('idx_parcel_number', table_name='parcels')
    op.drop_table('parcels')

    op.drop_index('ix_land_use_categories_code', table_name='land_use_categories')
    op.drop_index('ix_land_use_categories_name', table_name='land_use_categories')
    op.drop_table('land_use_categories')

    op.drop_index('ix_parishes_code', table_name='parishes')
    op.drop_index('ix_parishes_name', table_name='parishes')
    op.drop_table('parishes')

    op.drop_index('ix_document_types_code', table_name='document_types')
    op.drop_index('ix_document_types_name', table_name='document_types')
    op.drop_table('document_types')
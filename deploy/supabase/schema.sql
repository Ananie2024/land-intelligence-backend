BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> a1b2c3d4e5f6

CREATE TABLE document_types (
    id VARCHAR(36) NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    code VARCHAR(20) NOT NULL, 
    description TEXT, 
    requires_verification BOOLEAN DEFAULT false NOT NULL, 
    retention_years VARCHAR(10) DEFAULT 'PERMANENT' NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (name), 
    UNIQUE (code)
);

COMMENT ON COLUMN document_types.id IS 'UUID primary key';

COMMENT ON COLUMN document_types.name IS 'Type name (e.g., ''Title Deed'', ''Survey Map'')';

COMMENT ON COLUMN document_types.code IS 'Unique type code (e.g., ''TITLE'', ''MAP'')';

COMMENT ON COLUMN document_types.description IS 'Description of document type';

COMMENT ON COLUMN document_types.requires_verification IS 'Whether documents of this type require verification';

COMMENT ON COLUMN document_types.retention_years IS 'Retention period in years or ''PERMANENT''';

CREATE UNIQUE INDEX ix_document_types_name ON document_types (name);

CREATE UNIQUE INDEX ix_document_types_code ON document_types (code);

CREATE TABLE parishes (
    id VARCHAR(36) NOT NULL, 
    name VARCHAR(200) NOT NULL, 
    code VARCHAR(20) NOT NULL, 
    description TEXT, 
    address VARCHAR(500), 
    contact_person VARCHAR(200), 
    contact_phone VARCHAR(50), 
    contact_email VARCHAR(200), 
    parcel_count INTEGER DEFAULT '0' NOT NULL, 
    boundary_wkb geometry(MULTIPOLYGON,4326), 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (code)
);

CREATE INDEX idx_parishes_boundary_wkb ON parishes USING gist (boundary_wkb);

COMMENT ON COLUMN parishes.id IS 'UUID primary key';

COMMENT ON COLUMN parishes.name IS 'Official parish name';

COMMENT ON COLUMN parishes.code IS 'Unique parish code (e.g., PAR-001)';

COMMENT ON COLUMN parishes.description IS 'Description of parish boundaries and history';

COMMENT ON COLUMN parishes.address IS 'Physical address of parish office';

COMMENT ON COLUMN parishes.contact_person IS 'Name of primary contact person';

COMMENT ON COLUMN parishes.contact_phone IS 'Phone number for parish office';

COMMENT ON COLUMN parishes.contact_email IS 'Email address for parish office';

COMMENT ON COLUMN parishes.parcel_count IS 'Cached count of active parcels in this parish';

COMMENT ON COLUMN parishes.boundary_wkb IS 'Spatial boundary of the parish (MULTIPOLYGON) in WGS84';

CREATE INDEX ix_parishes_name ON parishes (name);

CREATE UNIQUE INDEX ix_parishes_code ON parishes (code);

CREATE TABLE land_use_categories (
    id VARCHAR(36) NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    code VARCHAR(20) NOT NULL, 
    description TEXT, 
    base_tax_rate FLOAT DEFAULT '0.0' NOT NULL, 
    tax_rate_unit VARCHAR(20) DEFAULT 'per_sqm' NOT NULL, 
    requires_approval BOOLEAN DEFAULT false NOT NULL, 
    zoning_restrictions TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (name), 
    UNIQUE (code)
);

COMMENT ON COLUMN land_use_categories.id IS 'UUID primary key';

COMMENT ON COLUMN land_use_categories.name IS 'Category name (e.g., ''Residential'', ''Agricultural'')';

COMMENT ON COLUMN land_use_categories.code IS 'Unique category code (e.g., ''RES'', ''AGR'')';

COMMENT ON COLUMN land_use_categories.description IS 'Description of land use category';

COMMENT ON COLUMN land_use_categories.base_tax_rate IS 'Base tax rate per square meter';

COMMENT ON COLUMN land_use_categories.tax_rate_unit IS 'Unit for tax rate (e.g., ''per_sqm'', ''flat'')';

COMMENT ON COLUMN land_use_categories.requires_approval IS 'Whether this land use requires special approval';

COMMENT ON COLUMN land_use_categories.zoning_restrictions IS 'Any zoning restrictions applicable';

CREATE UNIQUE INDEX ix_land_use_categories_name ON land_use_categories (name);

CREATE UNIQUE INDEX ix_land_use_categories_code ON land_use_categories (code);

CREATE TABLE parcels (
    id VARCHAR(36) NOT NULL, 
    parcel_number VARCHAR(50) NOT NULL, 
    parish_id VARCHAR(36) NOT NULL, 
    land_use_category_id VARCHAR(36), 
    area_sqm FLOAT NOT NULL, 
    geometry_wkb geometry(POLYGON,4326), 
    title_deed_number VARCHAR(100), 
    owner_name VARCHAR(500) NOT NULL, 
    owner_contact VARCHAR(500), 
    location_description TEXT, 
    valuation FLOAT, 
    valuation_date VARCHAR(10), 
    metadata JSON, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(land_use_category_id) REFERENCES land_use_categories (id) ON DELETE RESTRICT, 
    FOREIGN KEY(parish_id) REFERENCES parishes (id) ON DELETE RESTRICT, 
    UNIQUE (parcel_number)
);

CREATE INDEX idx_parcels_geometry_wkb ON parcels USING gist (geometry_wkb);

COMMENT ON COLUMN parcels.id IS 'UUID primary key';

COMMENT ON COLUMN parcels.parcel_number IS 'Unique parcel identifier';

COMMENT ON COLUMN parcels.parish_id IS 'Foreign key to parish';

COMMENT ON COLUMN parcels.land_use_category_id IS 'Foreign key to land use category';

COMMENT ON COLUMN parcels.area_sqm IS 'Area in square meters';

COMMENT ON COLUMN parcels.geometry_wkb IS 'Spatial geometry (POLYGON) in WGS84';

COMMENT ON COLUMN parcels.title_deed_number IS 'Official title deed reference';

COMMENT ON COLUMN parcels.owner_name IS 'Name of land owner';

COMMENT ON COLUMN parcels.owner_contact IS 'Contact information for owner';

COMMENT ON COLUMN parcels.location_description IS 'Text description of location';

COMMENT ON COLUMN parcels.valuation IS 'Current valuation amount';

COMMENT ON COLUMN parcels.valuation_date IS 'Date of last valuation';

COMMENT ON COLUMN parcels.metadata IS 'JSON field for additional attributes';

CREATE UNIQUE INDEX idx_parcel_number ON parcels (parcel_number);

CREATE INDEX idx_owner_name ON parcels (owner_name);

CREATE INDEX idx_title_deed ON parcels (title_deed_number);

CREATE INDEX ix_parcels_parish_id ON parcels (parish_id);

CREATE INDEX ix_parcels_land_use_category_id ON parcels (land_use_category_id);

CREATE TABLE users (
    id VARCHAR(36) NOT NULL, 
    email VARCHAR(255) NOT NULL, 
    username VARCHAR(100) NOT NULL, 
    hashed_password VARCHAR(255) NOT NULL, 
    full_name VARCHAR(255), 
    role VARCHAR(20) DEFAULT 'viewer' NOT NULL, 
    parish_id VARCHAR(36), 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    is_verified BOOLEAN DEFAULT false NOT NULL, 
    last_login TIMESTAMP WITH TIME ZONE, 
    failed_login_attempts VARCHAR(10) DEFAULT '0' NOT NULL, 
    locked_until TIMESTAMP WITH TIME ZONE, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (email), 
    UNIQUE (username)
);

COMMENT ON COLUMN users.id IS 'UUID primary key';

COMMENT ON COLUMN users.email IS 'User email address';

COMMENT ON COLUMN users.username IS 'Unique username';

COMMENT ON COLUMN users.hashed_password IS 'Argon2 hashed password';

COMMENT ON COLUMN users.full_name IS 'Full name of user';

COMMENT ON COLUMN users.role IS 'User role (admin, client, viewer)';

COMMENT ON COLUMN users.parish_id IS 'For clients, links to their parish';

COMMENT ON COLUMN users.is_active IS 'Whether user account is active';

COMMENT ON COLUMN users.is_verified IS 'Whether email is verified';

COMMENT ON COLUMN users.last_login IS 'Last successful login timestamp';

COMMENT ON COLUMN users.failed_login_attempts IS 'Count of failed login attempts';

COMMENT ON COLUMN users.locked_until IS 'Account locked until this timestamp';

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE UNIQUE INDEX ix_users_username ON users (username);

CREATE TABLE audit_logs (
    id VARCHAR(36) NOT NULL, 
    table_name VARCHAR(100) NOT NULL, 
    record_id VARCHAR(36) NOT NULL, 
    action VARCHAR(20) NOT NULL, 
    old_value JSON, 
    new_value JSON, 
    performed_by VARCHAR(36) NOT NULL, 
    performed_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    ip_address VARCHAR(45), 
    user_agent VARCHAR(500), 
    correlation_id VARCHAR(36), 
    metadata JSON, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    PRIMARY KEY (id)
);

COMMENT ON COLUMN audit_logs.id IS 'UUID primary key';

COMMENT ON COLUMN audit_logs.table_name IS 'Name of the table that was modified';

COMMENT ON COLUMN audit_logs.record_id IS 'UUID of the record that was modified';

COMMENT ON COLUMN audit_logs.action IS 'Type of action (CREATE, UPDATE, DELETE, SOFT_DELETE, RESTORE)';

COMMENT ON COLUMN audit_logs.old_value IS 'JSON representation of values before change';

COMMENT ON COLUMN audit_logs.new_value IS 'JSON representation of values after change';

COMMENT ON COLUMN audit_logs.performed_by IS 'User ID who performed the action';

COMMENT ON COLUMN audit_logs.performed_at IS 'Timestamp when action was performed';

COMMENT ON COLUMN audit_logs.ip_address IS 'IP address of the client';

COMMENT ON COLUMN audit_logs.user_agent IS 'User agent string from client';

COMMENT ON COLUMN audit_logs.correlation_id IS 'Request correlation ID for tracing';

COMMENT ON COLUMN audit_logs.metadata IS 'JSON field for additional audit context';

CREATE INDEX ix_audit_logs_table_name ON audit_logs (table_name);

CREATE INDEX ix_audit_logs_record_id ON audit_logs (record_id);

CREATE INDEX ix_audit_logs_action ON audit_logs (action);

CREATE INDEX ix_audit_logs_performed_by ON audit_logs (performed_by);

CREATE INDEX ix_audit_logs_performed_at ON audit_logs (performed_at);

CREATE INDEX idx_audit_table_record ON audit_logs (table_name, record_id);

CREATE INDEX idx_audit_performed_by_date ON audit_logs (performed_by, performed_at);

CREATE INDEX idx_audit_action_date ON audit_logs (action, performed_at);

CREATE INDEX idx_audit_correlation ON audit_logs (correlation_id);

CREATE TABLE documents (
    id VARCHAR(36) NOT NULL, 
    parcel_id VARCHAR(36), 
    document_type_id VARCHAR(36) NOT NULL, 
    filename VARCHAR(500) NOT NULL, 
    file_path VARCHAR(500) NOT NULL, 
    file_size_bytes INTEGER NOT NULL, 
    mime_type VARCHAR(100) NOT NULL, 
    description TEXT, 
    document_date DATE, 
    reference_number VARCHAR(200), 
    page_count INTEGER, 
    checksum VARCHAR(64) NOT NULL, 
    metadata JSON, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(document_type_id) REFERENCES document_types (id) ON DELETE RESTRICT, 
    FOREIGN KEY(parcel_id) REFERENCES parcels (id) ON DELETE SET NULL, 
    UNIQUE (file_path)
);

COMMENT ON COLUMN documents.id IS 'UUID primary key';

COMMENT ON COLUMN documents.parcel_id IS 'Foreign key to parcel (optional)';

COMMENT ON COLUMN documents.document_type_id IS 'Foreign key to document type';

COMMENT ON COLUMN documents.filename IS 'Original filename';

COMMENT ON COLUMN documents.file_path IS 'Path to file on filesystem';

COMMENT ON COLUMN documents.file_size_bytes IS 'Size of file in bytes';

COMMENT ON COLUMN documents.mime_type IS 'MIME type of file';

COMMENT ON COLUMN documents.description IS 'Document description';

COMMENT ON COLUMN documents.document_date IS 'Document date (issue/recording date)';

COMMENT ON COLUMN documents.reference_number IS 'Official reference number';

COMMENT ON COLUMN documents.page_count IS 'Number of pages (for PDF)';

COMMENT ON COLUMN documents.checksum IS 'SHA-256 checksum for integrity';

COMMENT ON COLUMN documents.metadata IS 'JSON field for additional attributes';

COMMENT ON COLUMN documents.created_at IS 'Timestamp when record was created';

COMMENT ON COLUMN documents.updated_at IS 'Timestamp when record was last updated';

COMMENT ON COLUMN documents.is_active IS 'Soft delete flag: True if record is active, False if deleted';

CREATE INDEX idx_document_date ON documents (document_date);

CREATE INDEX idx_filename ON documents (filename);

CREATE INDEX idx_reference_number ON documents (reference_number);

CREATE INDEX ix_documents_document_type_id ON documents (document_type_id);

CREATE INDEX ix_documents_parcel_id ON documents (parcel_id);

CREATE INDEX ix_documents_reference_number ON documents (reference_number);

CREATE TABLE tax_records (
    id VARCHAR(36) NOT NULL, 
    parcel_id VARCHAR(36) NOT NULL, 
    assessment_year VARCHAR(4) NOT NULL, 
    assessed_value FLOAT DEFAULT '0.0' NOT NULL, 
    tax_rate_applied FLOAT DEFAULT '0.0' NOT NULL, 
    base_tax_amount FLOAT DEFAULT '0.0' NOT NULL, 
    penalties_amount FLOAT DEFAULT '0.0' NOT NULL, 
    total_amount FLOAT DEFAULT '0.0' NOT NULL, 
    status VARCHAR(20) DEFAULT 'pending' NOT NULL, 
    due_date DATE NOT NULL, 
    paid_date DATE, 
    payment_reference VARCHAR(100), 
    notes VARCHAR(500), 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(parcel_id) REFERENCES parcels (id) ON DELETE CASCADE
);

COMMENT ON COLUMN tax_records.id IS 'UUID primary key';

COMMENT ON COLUMN tax_records.parcel_id IS 'Foreign key to parcel';

COMMENT ON COLUMN tax_records.assessment_year IS 'Year of tax assessment (e.g., ''2024'')';

COMMENT ON COLUMN tax_records.assessed_value IS 'Assessed value of parcel for tax purposes';

COMMENT ON COLUMN tax_records.tax_rate_applied IS 'Tax rate applied for this assessment';

COMMENT ON COLUMN tax_records.base_tax_amount IS 'Base tax amount calculated';

COMMENT ON COLUMN tax_records.penalties_amount IS 'Penalties amount if any';

COMMENT ON COLUMN tax_records.total_amount IS 'Total tax amount due (base + penalties)';

COMMENT ON COLUMN tax_records.status IS 'Status of tax record (pending, paid, overdue)';

COMMENT ON COLUMN tax_records.due_date IS 'Due date for payment';

COMMENT ON COLUMN tax_records.paid_date IS 'Date when fully paid (if applicable)';

COMMENT ON COLUMN tax_records.payment_reference IS 'Reference for full payment';

COMMENT ON COLUMN tax_records.notes IS 'Additional notes about tax assessment';

COMMENT ON COLUMN tax_records.created_at IS 'Timestamp when record was created';

COMMENT ON COLUMN tax_records.updated_at IS 'Timestamp when record was last updated';

COMMENT ON COLUMN tax_records.is_active IS 'Soft delete flag: True if record is active, False if deleted';

CREATE INDEX idx_assessment_year ON tax_records (assessment_year);

CREATE INDEX idx_due_date ON tax_records (due_date);

CREATE INDEX idx_status ON tax_records (status);

CREATE UNIQUE INDEX idx_unique_parcel_year ON tax_records (parcel_id, assessment_year);

CREATE INDEX ix_tax_records_assessment_year ON tax_records (assessment_year);

CREATE INDEX ix_tax_records_parcel_id ON tax_records (parcel_id);

CREATE INDEX ix_tax_records_status ON tax_records (status);

CREATE TABLE physical_locations (
    id VARCHAR(36) NOT NULL, 
    document_id VARCHAR(36), 
    name VARCHAR(200) NOT NULL, 
    location_code VARCHAR(50) NOT NULL, 
    building VARCHAR(100), 
    floor VARCHAR(50), 
    room_number VARCHAR(50), 
    description TEXT, 
    environmental_notes TEXT, 
    access_restrictions TEXT, 
    contact_person VARCHAR(200), 
    contact_phone VARCHAR(50), 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(document_id) REFERENCES documents (id) ON DELETE SET NULL
);

COMMENT ON COLUMN physical_locations.id IS 'UUID primary key';

COMMENT ON COLUMN physical_locations.document_id IS 'Foreign key to document (optional, for direct document location)';

COMMENT ON COLUMN physical_locations.name IS 'Location name (e.g., ''Main Archive Room'', ''Basement Storage'')';

COMMENT ON COLUMN physical_locations.location_code IS 'Unique location code (e.g., ''ARC-01'', ''BSM-02'')';

COMMENT ON COLUMN physical_locations.building IS 'Building name or number';

COMMENT ON COLUMN physical_locations.floor IS 'Floor level';

COMMENT ON COLUMN physical_locations.room_number IS 'Room number or identifier';

COMMENT ON COLUMN physical_locations.description IS 'Description of location and access instructions';

COMMENT ON COLUMN physical_locations.environmental_notes IS 'Notes about environmental conditions (humidity, temperature)';

COMMENT ON COLUMN physical_locations.access_restrictions IS 'Any access restrictions or security requirements';

COMMENT ON COLUMN physical_locations.contact_person IS 'Person responsible for this location';

COMMENT ON COLUMN physical_locations.contact_phone IS 'Contact phone number';

COMMENT ON COLUMN physical_locations.created_at IS 'Timestamp when record was created';

COMMENT ON COLUMN physical_locations.updated_at IS 'Timestamp when record was last updated';

COMMENT ON COLUMN physical_locations.is_active IS 'Soft delete flag: True if record is active, False if deleted';

CREATE INDEX idx_building_floor ON physical_locations (building, floor);

CREATE INDEX idx_location_code ON physical_locations (location_code);

CREATE UNIQUE INDEX ix_physical_locations_document_id ON physical_locations (document_id);

CREATE UNIQUE INDEX ix_physical_locations_location_code ON physical_locations (location_code);

CREATE TABLE qr_code_registry (
    id VARCHAR(36) NOT NULL, 
    parcel_id VARCHAR(36), 
    document_id VARCHAR(36), 
    code VARCHAR(255) NOT NULL, 
    code_type VARCHAR(20) NOT NULL, 
    file_path VARCHAR(500) NOT NULL, 
    data_payload JSON NOT NULL, 
    expires_at TIMESTAMP WITH TIME ZONE, 
    last_accessed_at TIMESTAMP WITH TIME ZONE, 
    access_count INTEGER DEFAULT '0' NOT NULL, 
    is_revoked BOOLEAN DEFAULT false NOT NULL, 
    metadata JSON, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(document_id) REFERENCES documents (id) ON DELETE CASCADE, 
    FOREIGN KEY(parcel_id) REFERENCES parcels (id) ON DELETE CASCADE
);

COMMENT ON COLUMN qr_code_registry.id IS 'UUID primary key';

COMMENT ON COLUMN qr_code_registry.parcel_id IS 'Foreign key to parcel (optional)';

COMMENT ON COLUMN qr_code_registry.document_id IS 'Foreign key to document (optional)';

COMMENT ON COLUMN qr_code_registry.code IS 'Unique QR code string';

COMMENT ON COLUMN qr_code_registry.code_type IS 'Type of entity this QR code points to (parcel, document)';

COMMENT ON COLUMN qr_code_registry.file_path IS 'Path to QR code image file';

COMMENT ON COLUMN qr_code_registry.data_payload IS 'JSON data encoded in QR code';

COMMENT ON COLUMN qr_code_registry.expires_at IS 'Expiration timestamp (if temporary)';

COMMENT ON COLUMN qr_code_registry.last_accessed_at IS 'Last time this QR was scanned';

COMMENT ON COLUMN qr_code_registry.access_count IS 'Number of times QR has been accessed';

COMMENT ON COLUMN qr_code_registry.is_revoked IS 'Whether this QR code has been revoked';

COMMENT ON COLUMN qr_code_registry.metadata IS 'JSON field for additional attributes';

COMMENT ON COLUMN qr_code_registry.created_at IS 'Timestamp when record was created';

COMMENT ON COLUMN qr_code_registry.updated_at IS 'Timestamp when record was last updated';

COMMENT ON COLUMN qr_code_registry.is_active IS 'Soft delete flag: True if record is active, False if deleted';

CREATE INDEX idx_code_type ON qr_code_registry (code_type);

CREATE INDEX idx_expires_at ON qr_code_registry (expires_at);

CREATE INDEX idx_is_revoked ON qr_code_registry (is_revoked);

CREATE UNIQUE INDEX ix_qr_code_registry_code ON qr_code_registry (code);

CREATE INDEX ix_qr_code_registry_code_type ON qr_code_registry (code_type);

CREATE INDEX ix_qr_code_registry_document_id ON qr_code_registry (document_id);

CREATE INDEX ix_qr_code_registry_expires_at ON qr_code_registry (expires_at);

CREATE INDEX ix_qr_code_registry_parcel_id ON qr_code_registry (parcel_id);

CREATE TABLE tax_payments (
    id VARCHAR(36) NOT NULL, 
    tax_record_id VARCHAR(36) NOT NULL, 
    payment_amount FLOAT NOT NULL, 
    payment_date DATE NOT NULL, 
    payment_method VARCHAR(50) NOT NULL, 
    payment_reference VARCHAR(100), 
    receipt_number VARCHAR(50) NOT NULL, 
    received_by VARCHAR(200) NOT NULL, 
    notes TEXT, 
    is_reversal BOOLEAN DEFAULT false NOT NULL, 
    reversed_payment_id VARCHAR(36), 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(reversed_payment_id) REFERENCES tax_payments (id) ON DELETE SET NULL, 
    FOREIGN KEY(tax_record_id) REFERENCES tax_records (id) ON DELETE CASCADE
);

COMMENT ON COLUMN tax_payments.id IS 'UUID primary key';

COMMENT ON COLUMN tax_payments.tax_record_id IS 'Foreign key to tax record';

COMMENT ON COLUMN tax_payments.payment_amount IS 'Amount paid in this transaction';

COMMENT ON COLUMN tax_payments.payment_date IS 'Date of payment';

COMMENT ON COLUMN tax_payments.payment_method IS 'Method of payment (cash, bank_transfer, check)';

COMMENT ON COLUMN tax_payments.payment_reference IS 'External payment reference number';

COMMENT ON COLUMN tax_payments.receipt_number IS 'Generated receipt number';

COMMENT ON COLUMN tax_payments.received_by IS 'Name/ID of person who received payment';

COMMENT ON COLUMN tax_payments.notes IS 'Additional notes about payment';

COMMENT ON COLUMN tax_payments.is_reversal IS 'Whether this is a reversal of a previous payment';

COMMENT ON COLUMN tax_payments.reversed_payment_id IS 'Reference to reversed payment (if is_reversal=True)';

COMMENT ON COLUMN tax_payments.created_at IS 'Timestamp when record was created';

COMMENT ON COLUMN tax_payments.updated_at IS 'Timestamp when record was last updated';

COMMENT ON COLUMN tax_payments.is_active IS 'Soft delete flag: True if record is active, False if deleted';

CREATE INDEX idx_payment_date ON tax_payments (payment_date);

CREATE INDEX idx_payment_method ON tax_payments (payment_method);

CREATE INDEX idx_receipt_number ON tax_payments (receipt_number);

CREATE INDEX ix_tax_payments_payment_date ON tax_payments (payment_date);

CREATE INDEX ix_tax_payments_payment_reference ON tax_payments (payment_reference);

CREATE UNIQUE INDEX ix_tax_payments_receipt_number ON tax_payments (receipt_number);

CREATE INDEX ix_tax_payments_tax_record_id ON tax_payments (tax_record_id);

CREATE TABLE storage_cabinets (
    id VARCHAR(36) NOT NULL, 
    physical_location_id VARCHAR(36) NOT NULL, 
    cabinet_number VARCHAR(50) NOT NULL, 
    cabinet_type VARCHAR(50) DEFAULT 'filing' NOT NULL, 
    description TEXT, 
    row_number INTEGER, 
    column_number INTEGER, 
    max_capacity INTEGER, 
    current_count INTEGER DEFAULT '0' NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(physical_location_id) REFERENCES physical_locations (id) ON DELETE CASCADE
);

COMMENT ON COLUMN storage_cabinets.id IS 'UUID primary key';

COMMENT ON COLUMN storage_cabinets.physical_location_id IS 'Foreign key to physical location (room/building)';

COMMENT ON COLUMN storage_cabinets.cabinet_number IS 'Cabinet identifier (e.g., ''CAB-001'')';

COMMENT ON COLUMN storage_cabinets.cabinet_type IS 'Type of cabinet (e.g., ''filing'', ''shelf'', ''drawer'')';

COMMENT ON COLUMN storage_cabinets.description IS 'Description of cabinet contents/location';

COMMENT ON COLUMN storage_cabinets.row_number IS 'Row number within location (if applicable)';

COMMENT ON COLUMN storage_cabinets.column_number IS 'Column number within location (if applicable)';

COMMENT ON COLUMN storage_cabinets.max_capacity IS 'Maximum document capacity';

COMMENT ON COLUMN storage_cabinets.current_count IS 'Current number of documents stored';

COMMENT ON COLUMN storage_cabinets.created_at IS 'Timestamp when record was created';

COMMENT ON COLUMN storage_cabinets.updated_at IS 'Timestamp when record was last updated';

COMMENT ON COLUMN storage_cabinets.is_active IS 'Soft delete flag: True if record is active, False if deleted';

CREATE INDEX idx_cabinet_number ON storage_cabinets (cabinet_number);

CREATE INDEX idx_cabinet_type ON storage_cabinets (cabinet_type);

CREATE UNIQUE INDEX idx_unique_cabinet_per_location ON storage_cabinets (physical_location_id, cabinet_number);

CREATE INDEX ix_storage_cabinets_cabinet_number ON storage_cabinets (cabinet_number);

CREATE INDEX ix_storage_cabinets_physical_location_id ON storage_cabinets (physical_location_id);

CREATE TABLE backup_jobs (
    job_type VARCHAR(50) NOT NULL, 
    status VARCHAR(20) DEFAULT 'PENDING' NOT NULL, 
    tier VARCHAR(50) NOT NULL, 
    source_path VARCHAR(1000), 
    destination_path VARCHAR(1000), 
    file_size_bytes BIGINT, 
    file_count BIGINT, 
    checksum VARCHAR(128), 
    error_message TEXT, 
    started_at TIMESTAMP WITH TIME ZONE, 
    completed_at TIMESTAMP WITH TIME ZONE, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    id UUID NOT NULL, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_backup_jobs_status ON backup_jobs (status);

CREATE INDEX ix_backup_jobs_tier ON backup_jobs (tier);

CREATE INDEX ix_backup_jobs_created_at ON backup_jobs (created_at);

CREATE TABLE backup_verifications (
    backup_job_id UUID NOT NULL, 
    verified_at TIMESTAMP WITH TIME ZONE, 
    verified_by VARCHAR(200), 
    status VARCHAR(20) DEFAULT 'PENDING' NOT NULL, 
    notes TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    id UUID NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(backup_job_id) REFERENCES backup_jobs (id) ON DELETE CASCADE
);

CREATE INDEX ix_backup_verifications_backup_job_id ON backup_verifications (backup_job_id);

CREATE INDEX ix_backup_verifications_status ON backup_verifications (status);

INSERT INTO alembic_version (version_num) VALUES ('a1b2c3d4e5f6') RETURNING alembic_version.version_num;

-- Running upgrade a1b2c3d4e5f6 -> b2c3d4e5f6a7

ALTER TABLE parcels RENAME parcel_number TO upi;

DROP INDEX idx_parcel_number;

CREATE UNIQUE INDEX idx_parcel_upi ON parcels (upi);

UPDATE alembic_version SET version_num='b2c3d4e5f6a7' WHERE alembic_version.version_num = 'a1b2c3d4e5f6';

-- Running upgrade a1b2c3d4e5f6 -> a1b2c3d4e5f7

ALTER TABLE tax_payments ADD CONSTRAINT tax_payments_payment_reference_key UNIQUE (payment_reference);

INSERT INTO alembic_version (version_num) VALUES ('a1b2c3d4e5f7') RETURNING alembic_version.version_num;

-- Running upgrade b2c3d4e5f6a7 -> remove_title_deed_number

DROP INDEX idx_title_deed;

ALTER TABLE parcels DROP COLUMN title_deed_number;

UPDATE alembic_version SET version_num='remove_title_deed_number' WHERE alembic_version.version_num = 'b2c3d4e5f6a7';

-- Running upgrade a1b2c3d4e5f6 -> 63dbbad0300d

ALTER TABLE users ALTER COLUMN failed_login_attempts DROP DEFAULT;

ALTER TABLE users ALTER COLUMN failed_login_attempts TYPE INTEGER USING failed_login_attempts::integer;

ALTER TABLE users ALTER COLUMN failed_login_attempts TYPE INTEGER;

ALTER TABLE tax_records ALTER COLUMN assessed_value TYPE NUMERIC(15, 2);

ALTER TABLE tax_records ALTER COLUMN tax_rate_applied TYPE NUMERIC(15, 2);

ALTER TABLE tax_records ALTER COLUMN base_tax_amount TYPE NUMERIC(15, 2);

ALTER TABLE tax_records ALTER COLUMN penalties_amount TYPE NUMERIC(15, 2);

ALTER TABLE tax_records ALTER COLUMN total_amount TYPE NUMERIC(15, 2);

ALTER TABLE tax_payments ALTER COLUMN payment_amount TYPE NUMERIC(15, 2);

INSERT INTO alembic_version (version_num) VALUES ('63dbbad0300d') RETURNING alembic_version.version_num;

-- Running upgrade 63dbbad0300d -> ac60d369ef05

ALTER TABLE parcels ALTER COLUMN valuation_date TYPE DATE USING valuation_date::date;

ALTER TABLE parcels ALTER COLUMN valuation_date TYPE DATE;

UPDATE alembic_version SET version_num='ac60d369ef05' WHERE alembic_version.version_num = '63dbbad0300d';

-- Running upgrade ac60d369ef05 -> a3bfa1088a59

DROP INDEX ix_users_email;

DROP INDEX ix_users_username;

DROP TABLE users;

ALTER TABLE audit_logs ALTER COLUMN record_id TYPE UUID USING record_id::uuid;

ALTER TABLE audit_logs ALTER COLUMN performed_by TYPE UUID USING performed_by::uuid;

ALTER TABLE backup_jobs ALTER COLUMN error_message TYPE VARCHAR;

ALTER TABLE backup_jobs ALTER COLUMN started_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE backup_jobs ALTER COLUMN completed_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE backup_jobs ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN backup_jobs.created_at IS 'Timestamp when record was created';

ALTER TABLE backup_jobs ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN backup_jobs.updated_at IS 'Timestamp when record was last updated';

COMMENT ON COLUMN backup_jobs.is_active IS 'Soft delete flag: True if record is active, False if deleted';

DO $$ 
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'backup_verifications_backup_job_id_fkey') THEN
                ALTER TABLE backup_verifications DROP CONSTRAINT backup_verifications_backup_job_id_fkey;
            END IF;
        END $$;;

ALTER TABLE backup_jobs ALTER COLUMN id TYPE UUID USING id::uuid;

ALTER TABLE backup_verifications ALTER COLUMN backup_job_id TYPE UUID USING backup_job_id::uuid;

DROP INDEX ix_backup_jobs_created_at;

DROP INDEX ix_backup_jobs_status;

DROP INDEX ix_backup_jobs_tier;

ALTER TABLE backup_verifications ALTER COLUMN verified_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE backup_verifications ALTER COLUMN notes TYPE VARCHAR;

ALTER TABLE backup_verifications ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN backup_verifications.created_at IS 'Timestamp when record was created';

ALTER TABLE backup_verifications ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN backup_verifications.updated_at IS 'Timestamp when record was last updated';

COMMENT ON COLUMN backup_verifications.is_active IS 'Soft delete flag: True if record is active, False if deleted';

ALTER TABLE backup_verifications ALTER COLUMN id TYPE UUID USING id::uuid;

DROP INDEX ix_backup_verifications_status;

DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'parcels_land_use_category_id_fkey') THEN ALTER TABLE parcels DROP CONSTRAINT parcels_land_use_category_id_fkey; END IF; END $$;;

ALTER TABLE land_use_categories ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN land_use_categories.created_at IS 'Timestamp when record was created';

ALTER TABLE land_use_categories ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN land_use_categories.updated_at IS 'Timestamp when record was last updated';

COMMENT ON COLUMN land_use_categories.is_active IS 'Soft delete flag: True if record is active, False if deleted';

ALTER TABLE land_use_categories ALTER COLUMN id TYPE UUID USING id::uuid;

ALTER TABLE land_use_categories DROP CONSTRAINT land_use_categories_code_key;

ALTER TABLE land_use_categories DROP CONSTRAINT land_use_categories_name_key;

DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'parcels_parish_id_fkey') THEN ALTER TABLE parcels DROP CONSTRAINT parcels_parish_id_fkey; END IF; END $$;;

DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tax_records_parcel_id_fkey') THEN ALTER TABLE tax_records DROP CONSTRAINT tax_records_parcel_id_fkey; END IF; END $$;;

DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tax_payments_tax_record_id_fkey') THEN ALTER TABLE tax_payments DROP CONSTRAINT tax_payments_tax_record_id_fkey; END IF; END $$;;

DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'tax_payments_reversed_payment_id_fkey') THEN ALTER TABLE tax_payments DROP CONSTRAINT tax_payments_reversed_payment_id_fkey; END IF; END $$;;

DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'documents_parcel_id_fkey') THEN ALTER TABLE documents DROP CONSTRAINT documents_parcel_id_fkey; END IF; END $$;;

DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'documents_document_type_id_fkey') THEN ALTER TABLE documents DROP CONSTRAINT documents_document_type_id_fkey; END IF; END $$;;

DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'qr_code_registry_parcel_id_fkey') THEN ALTER TABLE qr_code_registry DROP CONSTRAINT qr_code_registry_parcel_id_fkey; END IF; END $$;;

DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'qr_code_registry_document_id_fkey') THEN ALTER TABLE qr_code_registry DROP CONSTRAINT qr_code_registry_document_id_fkey; END IF; END $$;;

DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'physical_locations_document_id_fkey') THEN ALTER TABLE physical_locations DROP CONSTRAINT physical_locations_document_id_fkey; END IF; END $$;;

DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'storage_cabinets_physical_location_id_fkey') THEN ALTER TABLE storage_cabinets DROP CONSTRAINT storage_cabinets_physical_location_id_fkey; END IF; END $$;;

ALTER TABLE parcels ALTER COLUMN parish_id TYPE UUID USING parish_id::uuid;

ALTER TABLE parcels ALTER COLUMN land_use_category_id TYPE UUID USING land_use_category_id::uuid;

ALTER TABLE parcels ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN parcels.created_at IS 'Timestamp when record was created';

ALTER TABLE parcels ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN parcels.updated_at IS 'Timestamp when record was last updated';

COMMENT ON COLUMN parcels.is_active IS 'Soft delete flag: True if record is active, False if deleted';

ALTER TABLE parcels ALTER COLUMN id TYPE UUID USING id::uuid;

ALTER TABLE parcels DROP CONSTRAINT parcels_parcel_number_key;

DROP INDEX idx_parcel_number;

CREATE INDEX idx_parcel_number ON parcels (parcel_number);

CREATE INDEX ix_parcels_parcel_number ON parcels (parcel_number);

CREATE INDEX ix_parcels_title_deed_number ON parcels (title_deed_number);

CREATE INDEX idx_parcels_geometry ON parcels USING gist(geometry_wkb);

ALTER TABLE document_types ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN document_types.created_at IS 'Timestamp when record was created';

ALTER TABLE document_types ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN document_types.updated_at IS 'Timestamp when record was last updated';

COMMENT ON COLUMN document_types.is_active IS 'Soft delete flag: True if record is active, False if deleted';

ALTER TABLE document_types ALTER COLUMN id TYPE UUID USING id::uuid;

ALTER TABLE document_types DROP CONSTRAINT document_types_code_key;

ALTER TABLE document_types DROP CONSTRAINT document_types_name_key;

ALTER TABLE documents ALTER COLUMN parcel_id TYPE UUID USING parcel_id::uuid;

ALTER TABLE documents ALTER COLUMN document_type_id TYPE UUID USING document_type_id::uuid;

ALTER TABLE documents ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE documents ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE documents ALTER COLUMN id TYPE UUID USING id::uuid;

ALTER TABLE tax_records ALTER COLUMN status TYPE VARCHAR(20);

ALTER TABLE tax_records ALTER COLUMN status DROP DEFAULT;

CREATE TYPE taxrecordstatus AS ENUM ('pending', 'paid', 'overdue', 'cancelled');

ALTER TABLE tax_records ALTER COLUMN status TYPE taxrecordstatus USING status::taxrecordstatus;

ALTER TABLE tax_records ALTER COLUMN status SET DEFAULT 'pending'::taxrecordstatus;

ALTER TABLE tax_records ALTER COLUMN assessment_year TYPE INTEGER USING assessment_year::INTEGER;

ALTER TABLE tax_records ALTER COLUMN parcel_id TYPE UUID USING parcel_id::uuid;

ALTER TABLE tax_records ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE tax_records ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE tax_records ALTER COLUMN id TYPE UUID USING id::uuid;

CREATE TABLE parcel_ownership_history (
    parcel_id UUID NOT NULL, 
    owner_name VARCHAR(500) NOT NULL, 
    owner_contact VARCHAR(500), 
    transfer_date DATE NOT NULL, 
    document_reference VARCHAR(255), 
    notes TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    id UUID DEFAULT gen_random_uuid() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(parcel_id) REFERENCES parcels (id) ON DELETE CASCADE
);

COMMENT ON COLUMN parcel_ownership_history.parcel_id IS 'Foreign key to parcel';

COMMENT ON COLUMN parcel_ownership_history.owner_name IS 'Name of the owner at this point in time';

COMMENT ON COLUMN parcel_ownership_history.owner_contact IS 'Contact information for the owner';

COMMENT ON COLUMN parcel_ownership_history.transfer_date IS 'Date when ownership was transferred';

COMMENT ON COLUMN parcel_ownership_history.document_reference IS 'Reference to supporting document (title deed, sale agreement, etc.)';

COMMENT ON COLUMN parcel_ownership_history.notes IS 'Additional notes about the ownership transfer';

COMMENT ON COLUMN parcel_ownership_history.created_at IS 'Timestamp when record was created';

COMMENT ON COLUMN parcel_ownership_history.updated_at IS 'Timestamp when record was last updated';

COMMENT ON COLUMN parcel_ownership_history.is_active IS 'Soft delete flag: True if record is active, False if deleted';

COMMENT ON COLUMN parcel_ownership_history.id IS 'UUID primary key';

CREATE INDEX idx_parcel_transfer_date ON parcel_ownership_history (parcel_id, transfer_date);

CREATE INDEX ix_parcel_ownership_history_parcel_id ON parcel_ownership_history (parcel_id);

ALTER TABLE parishes ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN parishes.created_at IS 'Timestamp when record was created';

ALTER TABLE parishes ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN parishes.updated_at IS 'Timestamp when record was last updated';

COMMENT ON COLUMN parishes.is_active IS 'Soft delete flag: True if record is active, False if deleted';

ALTER TABLE parishes ALTER COLUMN id TYPE UUID USING id::uuid;

ALTER TABLE parishes DROP CONSTRAINT parishes_code_key;

ALTER TABLE physical_locations ALTER COLUMN document_id TYPE UUID USING document_id::uuid;

ALTER TABLE physical_locations ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE physical_locations ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE physical_locations ALTER COLUMN id TYPE UUID USING id::uuid;

ALTER TABLE qr_code_registry ALTER COLUMN parcel_id TYPE UUID USING parcel_id::uuid;

ALTER TABLE qr_code_registry ALTER COLUMN document_id TYPE UUID USING document_id::uuid;

ALTER TABLE qr_code_registry ALTER COLUMN expires_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE qr_code_registry ALTER COLUMN last_accessed_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE qr_code_registry ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE qr_code_registry ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE qr_code_registry ALTER COLUMN id TYPE UUID USING id::uuid;

ALTER TABLE storage_cabinets ALTER COLUMN physical_location_id TYPE UUID USING physical_location_id::uuid;

ALTER TABLE storage_cabinets ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE storage_cabinets ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE storage_cabinets ALTER COLUMN id TYPE UUID USING id::uuid;

ALTER TABLE tax_payments ALTER COLUMN tax_record_id TYPE UUID USING tax_record_id::uuid;

ALTER TABLE tax_payments ALTER COLUMN reversed_payment_id TYPE UUID USING reversed_payment_id::uuid;

ALTER TABLE tax_payments ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE tax_payments ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;

ALTER TABLE tax_payments ALTER COLUMN id TYPE UUID USING id::uuid;

CREATE INDEX ix_audit_logs_correlation_id ON audit_logs (correlation_id);

UPDATE alembic_version SET version_num='a3bfa1088a59' WHERE alembic_version.version_num = 'ac60d369ef05';

-- Running upgrade a3bfa1088a59 -> 8a7b6c5d4e3f

CREATE TYPE IF NOT EXISTS userrole AS ENUM ('admin', 'client', 'viewer');

CREATE TYPE userrole AS ENUM ('admin', 'client', 'viewer');

CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() NOT NULL, 
    email VARCHAR(255) NOT NULL, 
    username VARCHAR(100) NOT NULL, 
    hashed_password VARCHAR(255) NOT NULL, 
    full_name VARCHAR(255), 
    role userrole DEFAULT 'viewer' NOT NULL, 
    parish_id UUID, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    is_verified BOOLEAN DEFAULT false NOT NULL, 
    last_login TIMESTAMP WITH TIME ZONE, 
    failed_login_attempts INTEGER DEFAULT 0 NOT NULL, 
    locked_until TIMESTAMP WITH TIME ZONE, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (email), 
    UNIQUE (username)
);

COMMENT ON COLUMN users.id IS 'UUID primary key';

COMMENT ON COLUMN users.email IS 'User email address';

COMMENT ON COLUMN users.username IS 'Unique username';

COMMENT ON COLUMN users.hashed_password IS 'Bcrypt hashed password';

COMMENT ON COLUMN users.full_name IS 'Full name of user';

COMMENT ON COLUMN users.role IS 'User role (admin, client, viewer)';

COMMENT ON COLUMN users.parish_id IS 'For clients, links to their parish';

COMMENT ON COLUMN users.is_active IS 'Whether user account is active';

COMMENT ON COLUMN users.is_verified IS 'Whether email is verified';

COMMENT ON COLUMN users.last_login IS 'Last successful login timestamp';

COMMENT ON COLUMN users.failed_login_attempts IS 'Count of failed login attempts';

COMMENT ON COLUMN users.locked_until IS 'Account locked until this timestamp';

COMMENT ON COLUMN users.created_at IS 'Timestamp when record was created';

COMMENT ON COLUMN users.updated_at IS 'Timestamp when record was last updated';

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE UNIQUE INDEX ix_users_username ON users (username);

UPDATE alembic_version SET version_num='8a7b6c5d4e3f' WHERE alembic_version.version_num = 'a3bfa1088a59';

-- Running upgrade 8a7b6c5d4e3f, a1b2c3d4e5f7, b2c3d4e5f6a7 -> 032eaed0a76e

DELETE FROM alembic_version WHERE alembic_version.version_num = 'a1b2c3d4e5f7';

UPDATE alembic_version SET version_num='032eaed0a76e' WHERE alembic_version.version_num = '8a7b6c5d4e3f';

-- Running upgrade 032eaed0a76e -> simplify_parish_entity_20260716

ALTER TABLE parishes DROP COLUMN contact_email;

ALTER TABLE parishes DROP COLUMN contact_phone;

ALTER TABLE parishes DROP COLUMN contact_person;

ALTER TABLE parishes DROP COLUMN address;

ALTER TABLE parishes DROP COLUMN description;

ALTER TABLE parishes DROP COLUMN code;

ALTER TABLE parishes DROP COLUMN parcel_count;

ALTER TABLE parishes DROP COLUMN boundary_wkb;

UPDATE alembic_version SET version_num='simplify_parish_entity_20260716' WHERE alembic_version.version_num = '032eaed0a76e';

-- Running upgrade simplify_parish_entity_20260716 -> e8f7a6b5c4d3

ALTER TABLE documents ADD COLUMN metadata JSON;

COMMENT ON COLUMN documents.metadata IS 'JSON field for additional attributes';

UPDATE alembic_version SET version_num='e8f7a6b5c4d3' WHERE alembic_version.version_num = 'simplify_parish_entity_20260716';

-- Running upgrade e8f7a6b5c4d3, remove_title_deed_number -> 73e159f607a7

DELETE FROM alembic_version WHERE alembic_version.version_num = 'e8f7a6b5c4d3';

UPDATE alembic_version SET version_num='73e159f607a7' WHERE alembic_version.version_num = 'remove_title_deed_number';

COMMIT;


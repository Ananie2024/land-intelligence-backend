// Document Types
// Land Intelligence System

import { BaseEntity, QueryFilters } from './common';

export interface DocumentType extends BaseEntity {
  name: string;
  code: string;
  description?: string | null;
  requires_parcel?: boolean;
  requires_reference?: boolean;
  document_count: number;
}

export interface Document extends BaseEntity {
  parcel_upi?: string | null;
  document_type_id: string;
  filename: string;
  file_path: string;
  file_size_bytes: number;
  mime_type: string;
  checksum: string;
  description?: string | null;
  document_date?: string | null;
  reference_number?: string | null;
  page_count?: number | null;
  metadata?: Record<string, any> | null;
  is_active: boolean;
  // Nested data
  document_type_name?: string | null;
  upi?: string | null;
  qr_code_count?: number;
}

export interface DocumentCreate {
  parcel_upi?: string | null;
  document_type_id: string;
  description?: string | null;
  document_date?: string | null;
  reference_number?: string | null;
}

export interface DocumentUpdate {
  parcel_upi?: string | null;
  document_type_id?: string;
  description?: string | null;
  document_date?: string | null;
  reference_number?: string | null;
  is_active?: boolean;
}

export interface DocumentFilters extends QueryFilters {
  parcel_upi?: string;
  document_type_id?: string;
  filename?: string;
  reference_number?: string;
}
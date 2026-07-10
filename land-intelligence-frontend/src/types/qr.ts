// QR Types
// Land Intelligence System

export interface QrCode {
  id: string;
  parcel_id?: string | null;
  document_id?: string | null;
  code: string;
  code_type: string;
  data_payload: Record<string, any>;
  file_path: string;
  expires_at?: string | null;
  last_accessed_at?: string | null;
  access_count: number;
  is_revoked: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  parcel_number?: string | null;
  document_filename?: string | null;
}

export interface QrCodeGenerateResponse {
  id: string;
  code: string;
  qr_image_base64?: string;
  expires_at?: string | null;
}

export interface QrCodeVerifyResponse {
  is_valid: boolean;
  code: string;
  code_type: string;
  parcel_id?: string | null;
  document_id?: string | null;
  expires_at?: string | null;
  is_revoked: boolean;
  data_payload?: Record<string, any> | null;
  message: string;
}
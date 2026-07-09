// QR Types
// Land Intelligence System

export interface QrCode {
  id: string;
  parcel_id: string;
  token: string;
  qr_image_url: string;
  expires_at: string;
  is_active: boolean;
  created_at: string;
}

export interface QrCodeGenerateResponse {
  qr_code_id: string;
  token: string;
  qr_image_base64: string;
  expires_at: string;
}
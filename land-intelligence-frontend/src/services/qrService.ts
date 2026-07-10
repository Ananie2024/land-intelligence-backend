// QR Services
// Land Intelligence System

import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { QrCode, QrCodeGenerateResponse } from '@/types/qr';
import { APIResponse } from '@/types/api';

export const qrService = {
  generateQrCode: async (parcelId: string, expiresDays?: number): Promise<APIResponse<QrCodeGenerateResponse>> => {
    return apiClient.post<QrCodeGenerateResponse>(ENDPOINTS.QR.GENERATE_PARCEL(parcelId), { expires_days: expiresDays });
  },

  generateDocumentQr: async (documentId: string): Promise<APIResponse<QrCodeGenerateResponse>> => {
    return apiClient.post<QrCodeGenerateResponse>(ENDPOINTS.QR.GENERATE_DOCUMENT(documentId));
  },

  verifyQrCode: async (code: string): Promise<APIResponse<{ valid: boolean; code: string; code_type: string; parcel_id?: string; document_id?: string; message: string }>> => {
    return apiClient.post(ENDPOINTS.QR.VERIFY, { code });
  },

  getQrCodeById: async (id: string): Promise<APIResponse<QrCode>> => {
    return apiClient.get<QrCode>(ENDPOINTS.QR.BY_ID(id));
  },

  revokeQrCode: async (id: string): Promise<APIResponse<{ message: string }>> => {
    return apiClient.delete<{ message: string }>(ENDPOINTS.QR.REVOKE(id));
  },
};

export default qrService;
// QR Services
// Land Intelligence System

import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { QrCode, QrCodeGenerateResponse, QrCodeVerifyResponse } from '@/types/qr';
import { APIResponse } from '@/types/api';

export const qrService = {
  generateQrCode: async (parcelId: string, expiresDays?: number): Promise<APIResponse<QrCodeGenerateResponse>> => {
    return apiClient.post<QrCodeGenerateResponse>(ENDPOINTS.QR.GENERATE_PARCEL(parcelId), { expires_days: expiresDays });
  },

  generateDocumentQr: async (documentId: string): Promise<APIResponse<QrCodeGenerateResponse>> => {
    return apiClient.post<QrCodeGenerateResponse>(ENDPOINTS.QR.GENERATE_DOCUMENT(documentId));
  },

  verifyQrCode: async (code: string): Promise<APIResponse<QrCodeVerifyResponse>> => {
    return apiClient.post(ENDPOINTS.QR.VERIFY, { code });
  },

  getQrCodeById: async (id: string): Promise<APIResponse<QrCode>> => {
    return apiClient.get<QrCode>(ENDPOINTS.QR.BY_ID(id));
  },

  revokeQrCode: async (id: string): Promise<APIResponse<{ message: string }>> => {
    return apiClient.delete<{ message: string }>(ENDPOINTS.QR.REVOKE(id));
  },
};

export const documentQrService = {
  /**
   * Generate a QR code for a document (supports all document types)
   */
  generateQrCode: async (documentId: string): Promise<APIResponse<QrCodeGenerateResponse>> => {
    return apiClient.post<QrCodeGenerateResponse>(ENDPOINTS.DOCUMENT_QR.GENERATE(documentId));
  },

  /**
   * Get the QR code for a document if one exists
   */
  getQrCode: async (documentId: string): Promise<APIResponse<QrCode>> => {
    return apiClient.get<QrCode>(ENDPOINTS.DOCUMENT_QR.GET(documentId));
  },
};

export default qrService;

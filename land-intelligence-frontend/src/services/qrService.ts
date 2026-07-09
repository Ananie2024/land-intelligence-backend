// QR Services
// Land Intelligence System

import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { QrCode, QrCodeGenerateResponse } from '@/types/qr';
import { APIResponse } from '@/types/api';

export const qrService = {
  generateQrCode: async (parcelId: string): Promise<APIResponse<QrCodeGenerateResponse>> => {
    return apiClient.post<QrCodeGenerateResponse>(ENDPOINTS.QR.GENERATE(parcelId));
  },

  verifyQrCode: async (token: string): Promise<APIResponse<{ valid: boolean; parcel_id?: string; parcel_number?: string }>> => {
    return apiClient.get<{ valid: boolean; parcel_id?: string; parcel_number?: string }>(ENDPOINTS.QR.VERIFY(token));
  },

  getQrCodeById: async (id: string): Promise<APIResponse<QrCode>> => {
    return apiClient.get<QrCode>(`${ENDPOINTS.QR.BASE}/${id}`);
  },
};

export default qrService;
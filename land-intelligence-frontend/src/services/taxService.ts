import { apiClient, PaginatedEnvelope } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';

export const taxService = {
  searchParcels: async (query: string, size: number = 10) => {
    return apiClient.get<PaginatedEnvelope<{ id: string; upi: string }>>(ENDPOINTS.PARCELS.BASE, {
      search: query,
      size,
    });
  },

  createAssessment: async (payload: {
    parcel_upi: string;
    assessment_year: string;
    land_use_category_id?: string | null;
    include_penalties?: boolean;
  }) => {
    return apiClient.post(ENDPOINTS.TAX.ASSESS, {
      parcel_upi: payload.parcel_upi,
      assessment_year: payload.assessment_year,
      land_use_category_id: payload.land_use_category_id ?? null,
      include_penalties: payload.include_penalties ?? true,
    });
  },

  recordPayment: async (payload: {
    tax_record_id: string;
    payment_amount: number;
    payment_method: string;
    payment_reference?: string;
    payment_date?: string;
  }) => {
    return apiClient.post(ENDPOINTS.TAX.PAYMENTS, {
      tax_record_id: payload.tax_record_id,
      payment_amount: payload.payment_amount,
      payment_method: payload.payment_method,
      payment_reference: payload.payment_reference || undefined,
      payment_date: payload.payment_date || new Date().toISOString().split('T')[0],
    });
  },
};

export default taxService;
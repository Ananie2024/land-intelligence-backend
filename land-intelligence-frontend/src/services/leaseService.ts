// Lease Service
// Land Intelligence System

import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import {
  LeaseAgreement,
  LeaseAgreementCreate,
  LeaseAgreementUpdate,
  LeaseListResponse,
  LeasePaymentRecordRequest,
  LeasePaymentSchedule,
  LeaseSummaryStats,
  LeaseStatus,
} from '@/types/lease';
import { APIResponse } from '@/types/api';

export const leaseService = {
  getLeases: async (params?: {
    parcel_id?: string;
    tenant?: string;
    status?: LeaseStatus;
    page?: number;
    page_size?: number;
  }): Promise<APIResponse<LeaseListResponse>> => {
    return apiClient.get<LeaseListResponse>(ENDPOINTS.LEASES.BASE, { params });
  },

  getLeaseById: async (id: string): Promise<APIResponse<LeaseAgreement>> => {
    return apiClient.get<LeaseAgreement>(ENDPOINTS.LEASES.BY_ID(id));
  },

  createLease: async (data: LeaseAgreementCreate): Promise<APIResponse<LeaseAgreement>> => {
    return apiClient.post<LeaseAgreement>(ENDPOINTS.LEASES.BASE, data);
  },

  updateLease: async (id: string, data: LeaseAgreementUpdate): Promise<APIResponse<LeaseAgreement>> => {
    return apiClient.put<LeaseAgreement>(ENDPOINTS.LEASES.BY_ID(id), data);
  },

  deleteLease: async (id: string): Promise<APIResponse<void>> => {
    return apiClient.delete<void>(ENDPOINTS.LEASES.BY_ID(id));
  },

  getStats: async (): Promise<APIResponse<LeaseSummaryStats>> => {
    return apiClient.get<LeaseSummaryStats>(ENDPOINTS.LEASES.STATS);
  },

  recordPayment: async (
    leaseId: string,
    scheduleId: string,
    data: LeasePaymentRecordRequest
  ): Promise<APIResponse<LeasePaymentSchedule>> => {
    return apiClient.post<LeasePaymentSchedule>(ENDPOINTS.LEASES.PAY(leaseId, scheduleId), data);
  },
};

export default leaseService;

import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { Parish, ParishCreate, Parcel, ParcelCreate, ParcelFilters, ParcelOwnershipHistory } from '@/types/land';
import { APIResponse } from '@/types/api';

export const landService = {
  // Parishes Services
  getParishes: async (params?: { page?: number; size?: number; search?: string }): Promise<APIResponse<Parish[]>> => {
    const response = await apiClient.get<{ items: Parish[]; total: number; page: number; size: number; pages: number }>(ENDPOINTS.PARISHES.BASE, params);
    // Transform wrapped paginated response to expected format
    return {
      ...response,
      data: response.data?.items ?? null,
    };
  },

  getParishById: async (id: string): Promise<APIResponse<Parish>> => {
    return apiClient.get<Parish>(ENDPOINTS.PARISHES.BY_ID(id));
  },

  createParish: async (parish: ParishCreate): Promise<APIResponse<Parish>> => {
    return apiClient.post<Parish>(ENDPOINTS.PARISHES.BASE, parish);
  },

  updateParish: async (id: string, parish: Partial<Parish>): Promise<APIResponse<Parish>> => {
    return apiClient.patch<Parish>(ENDPOINTS.PARISHES.BY_ID(id), parish);
  },

  deleteParish: async (id: string): Promise<APIResponse<{ message: string }>> => {
    return apiClient.delete<{ message: string }>(ENDPOINTS.PARISHES.BY_ID(id));
  },

  refreshParishCount: async (id: string): Promise<APIResponse<Parish>> => {
    return apiClient.post<Parish>(ENDPOINTS.PARISHES.REFRESH_COUNT(id));
  },

// Parcels Services
   getParcels: async (filters?: ParcelFilters): Promise<APIResponse<Parcel[]>> => {
     const response = await apiClient.get<{ items: Parcel[]; total: number; page: number; size: number; pages: number }>(ENDPOINTS.PARCELS.BASE, filters);
     // Transform wrapped paginated response to expected format
     return {
       ...response,
       data: response.data?.items ?? null,
     };
   },

  getParcelById: async (id: string): Promise<APIResponse<Parcel>> => {
    return apiClient.get<Parcel>(ENDPOINTS.PARCELS.BY_ID(id));
  },

  getParcelByNumber: async (parcelNumber: string): Promise<APIResponse<Parcel>> => {
    return apiClient.get<Parcel>(ENDPOINTS.PARCELS.BY_NUMBER(parcelNumber));
  },

  getParcelByDeed: async (titleDeedNumber: string): Promise<APIResponse<Parcel>> => {
    return apiClient.get<Parcel>(ENDPOINTS.PARCELS.BY_DEED(titleDeedNumber));
  },

  getParcelsByParish: async (
    parishId: string, 
    params?: { page?: number; size?: number }
  ): Promise<APIResponse<Parcel[]>> => {
    const response = await apiClient.get<{ items: Parcel[]; total: number; page: number; size: number; pages: number }>(ENDPOINTS.PARCELS.BY_PARISH(parishId), params);
    // Transform wrapped paginated response to expected format
    return {
      ...response,
      data: response.data?.items ?? null,
    };
  },

  createParcel: async (parcel: ParcelCreate): Promise<APIResponse<Parcel>> => {
    return apiClient.post<Parcel>(ENDPOINTS.PARCELS.BASE, parcel);
  },

  updateParcel: async (id: string, parcel: Partial<Parcel>): Promise<APIResponse<Parcel>> => {
    return apiClient.patch<Parcel>(ENDPOINTS.PARCELS.BY_ID(id), parcel);
  },

  deleteParcel: async (id: string): Promise<APIResponse<{ message: string }>> => {
    return apiClient.delete<{ message: string }>(ENDPOINTS.PARCELS.BY_ID(id));
  },

  getParcelOwnershipHistory: async (id: string): Promise<APIResponse<ParcelOwnershipHistory[]>> => {
    return apiClient.get<ParcelOwnershipHistory[]>(ENDPOINTS.PARCELS.OWNERSHIP_HISTORY(id));
  },

  getParcelsForMap: async (): Promise<APIResponse<Parcel[]>> => {
    return apiClient.get<Parcel[]>(ENDPOINTS.PARCELS.FOR_MAP);
  },
};

export default landService;
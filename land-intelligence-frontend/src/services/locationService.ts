// Location Service
// Land Intelligence System

import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { APIResponse } from '@/types/api';

export interface PhysicalLocation {
  id: string;
  location_type: string;
  name: string;
  address?: string | null;
  building?: string | null;
  floor?: string | null;
  room?: string | null;
  notes?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface StorageCabinet {
  id: string;
  location_id: string;
  cabinet_number: string;
  capacity: number;
  location_code?: string | null;
  row?: string | null;
  column?: string | null;
  notes?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const locationService = {
  getLocations: async (params?: { skip?: number; limit?: number }): Promise<APIResponse<PhysicalLocation[]>> => {
    return apiClient.get<PhysicalLocation[]>(ENDPOINTS.LOCATIONS.BASE, params);
  },

  getLocationById: async (id: string): Promise<APIResponse<PhysicalLocation>> => {
    return apiClient.get<PhysicalLocation>(ENDPOINTS.LOCATIONS.BY_ID(id));
  },

  createLocation: async (location: {
    location_type: string;
    name: string;
    address?: string;
    building?: string;
    floor?: string;
    room?: string;
    notes?: string;
  }): Promise<APIResponse<PhysicalLocation>> => {
    return apiClient.post<PhysicalLocation>(ENDPOINTS.LOCATIONS.BASE, location);
  },

  updateLocation: async (id: string, location: Partial<PhysicalLocation>): Promise<APIResponse<PhysicalLocation>> => {
    return apiClient.patch<PhysicalLocation>(ENDPOINTS.LOCATIONS.BY_ID(id), location);
  },

  deleteLocation: async (id: string): Promise<APIResponse<{ message: string }>> => {
    return apiClient.delete<{ message: string }>(ENDPOINTS.LOCATIONS.BY_ID(id));
  },

  findDocument: async (payload: {
    document_id?: string;
    parcel_id?: string;
  }): Promise<APIResponse<any>> => {
    return apiClient.post(ENDPOINTS.LOCATIONS.FIND, payload);
  },

  getCabinet: async (id: string): Promise<APIResponse<StorageCabinet>> => {
    return apiClient.get<StorageCabinet>(ENDPOINTS.LOCATIONS.CABINETS_BY_ID(id));
  },

  createCabinet: async (cabinet: {
    location_id: string;
    cabinet_number: string;
    capacity: number;
    location_code?: string;
    row?: string;
    column?: string;
    notes?: string;
  }): Promise<APIResponse<StorageCabinet>> => {
    return apiClient.post<StorageCabinet>(ENDPOINTS.LOCATIONS.CABINETS, cabinet);
  },

  updateCabinet: async (id: string, cabinet: Partial<StorageCabinet>): Promise<APIResponse<StorageCabinet>> => {
    return apiClient.patch<StorageCabinet>(ENDPOINTS.LOCATIONS.CABINETS_BY_ID(id), cabinet);
  },

  getLocationGrid: async (locationId: string): Promise<APIResponse<any>> => {
    return apiClient.get(ENDPOINTS.LOCATIONS.GRID(locationId));
  },
};

export default locationService;
// Dashboard Service
// Land Intelligence System

import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { SystemStats, ParishStats, ParcelStats, UserStats } from '@/types/dashboard';
import { APIResponse } from '@/types/api';

export const dashboardService = {
  // Get system statistics
  getSystemStats: async (): Promise<APIResponse<SystemStats>> => {
    return apiClient.get<SystemStats>(ENDPOINTS.DASHBOARD.STATS);
  },

  getParishStats: async (): Promise<APIResponse<ParishStats>> => {
    return apiClient.get<ParishStats>(ENDPOINTS.DASHBOARD.STATS_PARISHES);
  },

  getParcelStats: async (): Promise<APIResponse<ParcelStats>> => {
    return apiClient.get<ParcelStats>(ENDPOINTS.DASHBOARD.STATS_PARCELS);
  },

  getUserStats: async (): Promise<APIResponse<UserStats>> => {
    return apiClient.get<UserStats>(ENDPOINTS.DASHBOARD.STATS_USERS);
  },
};

export default dashboardService;
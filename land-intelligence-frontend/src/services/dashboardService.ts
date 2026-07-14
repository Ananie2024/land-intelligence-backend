// Dashboard Service
// Land Intelligence System

import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { SystemStats, ParishStats, ParcelStats, UserStats } from '@/types/dashboard';
import { APIResponse } from '@/types/api';
import type { SystemLog } from '@/types/settings';

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

  // Get system logs for the System Log Status card
  getSystemLogs: async (limit: number = 5): Promise<APIResponse<SystemLog[]>> => {
    return apiClient.get<SystemLog[]>(ENDPOINTS.SETTINGS.LOGS, { limit });
  },
};

export default dashboardService;

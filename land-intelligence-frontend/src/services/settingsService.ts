/**
 * Settings Service
 * Land Intelligence System
 */

import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { APIResponse } from '@/types/api';
import type { SystemSettings, SystemLog } from '@/types/settings';

export const settingsService = {
  getSettings: async (): Promise<APIResponse<SystemSettings>> => {
    return apiClient.get<SystemSettings>(ENDPOINTS.SETTINGS.GET);
  },

  updateSettings: async (settings: Partial<SystemSettings>): Promise<APIResponse<SystemSettings>> => {
    return apiClient.patch<SystemSettings>(ENDPOINTS.SETTINGS.UPDATE, settings);
  },

  getSystemLogs: async (limit: number = 10): Promise<APIResponse<SystemLog[]>> => {
    return apiClient.get<SystemLog[]>(ENDPOINTS.SETTINGS.LOGS, { limit });
  },
};

export default settingsService;
// Backup Service
// Land Intelligence System

import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { Backup, BackupVerifyResponse } from '@/types/backup';
import { APIResponse } from '@/types/api';

export const backupService = {
  getBackups: async (): Promise<APIResponse<Backup[]>> => {
    return apiClient.get<Backup[]>(ENDPOINTS.BACKUPS.BASE);
  },

  verifyBackups: async (): Promise<APIResponse<BackupVerifyResponse>> => {
    return apiClient.get<BackupVerifyResponse>(ENDPOINTS.BACKUPS.VERIFY);
  },

  createBackup: async (): Promise<APIResponse<Backup>> => {
    return apiClient.post<Backup>(ENDPOINTS.BACKUPS.BASE);
  },
};

export default backupService;
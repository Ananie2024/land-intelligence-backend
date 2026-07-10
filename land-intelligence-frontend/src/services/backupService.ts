// Backup Service
// Land Intelligence System

import { api } from '@/api/axios';
import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { Backup, BackupVerifyResponse } from '@/types/backup';
import { APIResponse } from '@/types/api';

export const backupService = {
  getBackups: async (params?: { status?: string; page?: number; size?: number }): Promise<APIResponse<Backup[]>> => {
    return apiClient.get<Backup[]>(ENDPOINTS.BACKUPS.BASE, params);
  },

  triggerBackup: async (options?: { 
    jobType?: string; 
    tier?: string; 
    sourcePath?: string 
  }): Promise<APIResponse<any>> => {
    // Use api directly for query params support
    const response = await api.post(ENDPOINTS.BACKUPS.TRIGGER, null, {
      params: {
        job_type: options?.jobType,
        tier: options?.tier,
        source_path: options?.sourcePath,
      }
    });
    return response.data;
  },

  getBackupJob: async (jobId: string): Promise<APIResponse<any>> => {
    return apiClient.get<any>(ENDPOINTS.BACKUPS.BY_JOB_ID(jobId));
  },

  triggerRestore: async (backupJobId: string): Promise<APIResponse<any>> => {
    // Use api directly for query params support
    const response = await api.post(ENDPOINTS.BACKUPS.RESTORE, null, {
      params: { backup_job_id: backupJobId }
    });
    return response.data;
  },

getRestoreJob: async (jobId: string): Promise<APIResponse<any>> => {
    return apiClient.get<any>(ENDPOINTS.BACKUPS.RESTORE_BY_ID(jobId));
  },

  verifyBackups: async (): Promise<APIResponse<any>> => {
    return apiClient.post<any>(ENDPOINTS.BACKUPS.VERIFY);
  },

  createBackup: async (options?: { 
    jobType?: string; 
    tier?: string; 
    sourcePath?: string 
  }): Promise<APIResponse<any>> => {
    return apiClient.post<any>(ENDPOINTS.BACKUPS.BASE, options);
  },
};

export default backupService;
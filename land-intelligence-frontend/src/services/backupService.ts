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
  }): Promise<APIResponse<unknown>> => {
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

  getBackupJob: async (jobId: string): Promise<APIResponse<unknown>> => {
    return apiClient.get<unknown>(ENDPOINTS.BACKUPS.BY_JOB_ID(jobId));
  },

  triggerRestore: async (backupJobId: string): Promise<APIResponse<unknown>> => {
    // Use api directly for query params support
    const response = await api.post(ENDPOINTS.BACKUPS.RESTORE, null, {
      params: { backup_job_id: backupJobId }
    });
    return response.data;
  },

  getRestoreJob: async (jobId: string): Promise<APIResponse<unknown>> => {
    return apiClient.get<unknown>(ENDPOINTS.BACKUPS.RESTORE_BY_ID(jobId));
  },

  verifyBackups: async (): Promise<APIResponse<BackupVerifyResponse>> => {
    return apiClient.post<BackupVerifyResponse>(ENDPOINTS.BACKUPS.VERIFY);
  },

  downloadBackup: async (jobId: string): Promise<Blob> => {
    const response = await api.get(ENDPOINTS.BACKUPS.DOWNLOAD(jobId), {
      responseType: 'blob'
    });
    return response.data as Blob;
  },
};

export default backupService;
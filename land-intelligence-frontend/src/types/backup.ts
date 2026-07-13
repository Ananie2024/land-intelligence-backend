// Backup Types
// Land Intelligence System

import { BaseEntity } from './common';

// Backend status values (uppercase)
export type BackendBackupStatus = 'COMPLETED' | 'FAILED' | 'PENDING' | 'IN_PROGRESS' | 'CANCELLED';

// Frontend status values (lowercase) - used for UI display
export type BackupStatus = 'completed' | 'failed' | 'pending' | 'in_progress' | 'cancelled';

export interface Backup extends BaseEntity {
  filename?: string;
  destination_path?: string;
  storage_path?: string;
  file_size_bytes?: number;
  file_count?: number;
  checksum?: string;
  status: BackendBackupStatus | BackupStatus;
  job_type?: string;
  tier?: string;
  backup_type?: 'daily' | 'weekly' | 'monthly' | 'manual';
  error_message?: string;
}

export interface BackupVerifyResponse {
  status: string;
  message: string;
  backup_count: number;
  total_size_mb: number;
}
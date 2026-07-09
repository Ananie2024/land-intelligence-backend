// Backup Types
// Land Intelligence System

import { BaseEntity } from './common';

export interface Backup extends BaseEntity {
  filename: string;
  file_size_bytes: number;
  storage_path: string;
  status: 'successful' | 'failed' | 'in_progress';
  backup_type: 'daily' | 'weekly' | 'monthly' | 'manual';
  metadata?: Record<string, any>;
}

export interface BackupVerifyResponse {
  status: string;
  message: string;
  backup_count: number;
  total_size_mb: number;
}
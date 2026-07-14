/**
 * Settings Types
 * Land Intelligence System
 */

export interface SystemSettings {
  api_url?: string;
  app_url?: string;
  debug_mode?: boolean;
}

export interface SystemLog {
  id: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: string;
  metadata?: Record<string, unknown>;
}
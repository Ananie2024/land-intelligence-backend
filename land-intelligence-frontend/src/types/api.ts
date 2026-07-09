import { PaginationMeta } from './common';

export interface ErrorDetail {
  field?: string;
  message: string;
  code?: string;
}

export interface APIResponse<T = any> {
  success: boolean;
  data: T | null;
  message: string | null;
  errors: ErrorDetail[] | null;
  meta: PaginationMeta | null;
  timestamp: string;
}

export interface PaginatedResponse<T> extends APIResponse<T[]> {
  data: T[];
  meta: PaginationMeta;
}

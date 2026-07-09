/**
 * Common TypeScript Types
 * Land Intelligence System
 */

export interface BaseEntity {
  id: string;
  created_at: string;
  updated_at: string;
  is_active?: boolean;
}

export interface QueryFilters {
  page?: number;
  size?: number;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginationMeta {
  page: number;
  size: number;
  total: number;
  pages: number;
}

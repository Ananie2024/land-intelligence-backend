import { api } from './axios';
import { APIResponse } from '@/types/api';
import { AxiosRequestConfig } from 'axios';

/**
 * PaginatedEnvelope represents the server's paginated response wrapper.
 * Backend returns { items: T[], total, page, size, pages } inside the `data` field.
 */
export type PaginatedEnvelope<T> = {
  items: T[];
  total: number;
  pages: number;
  page: number;
  size: number;
};

/**
 * Unwrap a paginated API response into a flat shape.
 * Transforms `APIResponse<PaginatedEnvelope<T>>` → `APIResponse<T[]> & { total, pages, page, size }`.
 * Use this in service methods that need to return the flat array format.
 */
export function unwrapPaginated<T>(
  response: APIResponse<PaginatedEnvelope<T>>
): APIResponse<T[]> & { total?: number; pages?: number; page?: number; size?: number } {
  if (response.success && response.data) {
    return {
      ...response,
      data: response.data.items,
      total: response.data.total,
      pages: response.data.pages,
      page: response.data.page,
      size: response.data.size,
    };
  }
  return {
    ...response,
    data: [],
    total: 0,
    pages: 0,
    page: 1,
    size: 20,
  };
}

/**
 * apiClient Helper Wrapper
 * Simplifies API calls by resolving the AxiosResponse outer envelope
 * and directly returning the backend's standardized APIResponse<T>.
 * 
 * For advanced use cases (file downloads, custom config), use the `api` instance directly.
 */
export const apiClient = {
  get: async <T>(url: string, params?: any, config?: AxiosRequestConfig): Promise<APIResponse<T>> => {
    const response = await api.get<APIResponse<T>>(url, { params, ...config });
    return response.data;
  },

  post: async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<APIResponse<T>> => {
    const response = await api.post<APIResponse<T>>(url, data, config);
    return response.data;
  },

  put: async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<APIResponse<T>> => {
    const response = await api.put<APIResponse<T>>(url, data, config);
    return response.data;
  },

  patch: async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<APIResponse<T>> => {
    const response = await api.patch<APIResponse<T>>(url, data, config);
    return response.data;
  },

  delete: async <T>(url: string, config?: AxiosRequestConfig): Promise<APIResponse<T>> => {
    const response = await api.delete<APIResponse<T>>(url, config);
    return response.data;
  },
};
export default apiClient;
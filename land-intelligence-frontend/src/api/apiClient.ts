import { api } from './axios';
import { APIResponse } from '@/types/api';
import { AxiosRequestConfig } from 'axios';

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
import { api } from './axios';
import { APIResponse } from '@/types/api';

/**
 * apiClient Helper Wrapper
 * Simplifies API calls by resolving the AxiosResponse outer envelope
 * and directly returning the backend's standardized APIResponse<T>.
 */
export const apiClient = {
  get: async <T>(url: string, params?: any): Promise<APIResponse<T>> => {
    const response = await api.get<APIResponse<T>>(url, { params });
    return response.data;
  },

  post: async <T>(url: string, data?: any): Promise<APIResponse<T>> => {
    const response = await api.post<APIResponse<T>>(url, data);
    return response.data;
  },

  put: async <T>(url: string, data?: any): Promise<APIResponse<T>> => {
    const response = await api.put<APIResponse<T>>(url, data);
    return response.data;
  },

  patch: async <T>(url: string, data?: any): Promise<APIResponse<T>> => {
    const response = await api.patch<APIResponse<T>>(url, data);
    return response.data;
  },

  delete: async <T>(url: string): Promise<APIResponse<T>> => {
    const response = await api.delete<APIResponse<T>>(url);
    return response.data;
  },
};
export default apiClient;

import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { UserResponse, UserCreate, UserListResponse } from '@/types/user';
import { APIResponse } from '@/types/api';

export const userService = {
  getUsers: async (params?: { page?: number; size?: number; search?: string }): Promise<APIResponse<UserResponse[]>> => {
    const response = await apiClient.get<UserListResponse>(ENDPOINTS.USERS.BASE, params);
    // Transform paginated response to just the items array for the table
    if (response.success && response.data) {
      const transformedResponse: APIResponse<UserResponse[]> = {
        success: response.success,
        data: response.data.items,
        message: response.message,
        errors: response.errors,
        meta: response.meta,
        timestamp: response.timestamp,
      };
      return transformedResponse;
    }
    // Return empty array if no data
    return {
      success: false,
      data: [],
      message: response.message,
      errors: response.errors,
      meta: null,
      timestamp: response.timestamp,
    };
  },

  getUserById: async (id: string): Promise<APIResponse<UserResponse>> => {
    return apiClient.get<UserResponse>(ENDPOINTS.USERS.BY_ID(id));
  },

  createUser: async (user: UserCreate): Promise<APIResponse<UserResponse>> => {
    // Admin creates user via auth register endpoint
    return apiClient.post<UserResponse>(ENDPOINTS.AUTH.REGISTER, user);
  },

  updateUser: async (id: string, user: Partial<UserResponse>): Promise<APIResponse<UserResponse>> => {
    return apiClient.patch<UserResponse>(ENDPOINTS.USERS.BY_ID(id), user);
  },

  deleteUser: async (id: string): Promise<APIResponse<{ message: string }>> => {
    return apiClient.delete<{ message: string }>(ENDPOINTS.USERS.BY_ID(id));
  },

  updateCurrentUser: async (user: Partial<UserResponse>): Promise<APIResponse<UserResponse>> => {
    return apiClient.patch<UserResponse>(ENDPOINTS.AUTH.UPDATE_ME, user);
  },
};

export default userService;
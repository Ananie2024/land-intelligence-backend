import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { UserLogin, UserCreate, TokenResponse, UserResponse, PasswordChange } from '@/types/user';
import { APIResponse } from '@/types/api';

export const authService = {
  login: async (credentials: UserLogin): Promise<APIResponse<TokenResponse>> => {
    return apiClient.post<TokenResponse>(ENDPOINTS.AUTH.LOGIN, credentials);
  },

  register: async (userData: UserCreate): Promise<APIResponse<UserResponse>> => {
    return apiClient.post<UserResponse>(ENDPOINTS.AUTH.REGISTER, userData);
  },

  refresh: async (refreshToken: string): Promise<APIResponse<TokenResponse>> => {
    return apiClient.post<TokenResponse>(ENDPOINTS.AUTH.REFRESH, { refresh_token: refreshToken });
  },

  logout: async (): Promise<APIResponse<{ message: string }>> => {
    return apiClient.post<{ message: string }>(ENDPOINTS.AUTH.LOGOUT);
  },

  getMe: async (): Promise<APIResponse<UserResponse>> => {
    return apiClient.get<UserResponse>(ENDPOINTS.AUTH.ME);
  },

  changePassword: async (data: PasswordChange): Promise<APIResponse<{ message: string }>> => {
    return apiClient.post<{ message: string }>(ENDPOINTS.AUTH.CHANGE_PASSWORD, data);
  },
};

export default authService;

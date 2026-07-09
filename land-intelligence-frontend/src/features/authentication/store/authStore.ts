// Authentication Store
// Land Intelligence System

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '@/services/authService';
import { userService } from '@/services/userService';
import { LOCAL_STORAGE_KEYS } from '@/utils/constants';
import { ApiError } from '@/api/axios';
import type { AuthState, LoginCredentials } from '../types/auth';
import type { UserResponse, UserRole } from '@/types/user';

// Role hierarchy: admin > client > viewer
const ROLE_HIERARCHY: Record<UserRole, number> = {
  admin: 3,
  client: 2,
  viewer: 1,
};

export const useAuthStore = create<AuthState & { 
  login: (credentials: LoginCredentials) => Promise<boolean>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
  hasRole: (role: UserRole) => boolean;
  hasAnyRole: (roles: UserRole[]) => boolean;
  initializeFromStorage: () => void;
}>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Initialize from localStorage
      initializeFromStorage: () => {
        const token = localStorage.getItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN);
        const refreshToken = localStorage.getItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN);
        const userProfile = localStorage.getItem(LOCAL_STORAGE_KEYS.USER_PROFILE);

        if (token && refreshToken && userProfile) {
          try {
            const user = JSON.parse(userProfile) as UserResponse;
            set({
              user,
              accessToken: token,
              refreshToken: refreshToken,
              isAuthenticated: true,
            });
          } catch (e) {
            console.error('Failed to parse user profile', e);
            get().logout();
          }
        }
      },

      // Login action
      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authService.login(credentials);
          
          if (response.success && response.data) {
            const { access_token, refresh_token, user } = response.data;
            
            // Store tokens
            localStorage.setItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN, access_token);
            localStorage.setItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN, refresh_token);
            localStorage.setItem(LOCAL_STORAGE_KEYS.USER_PROFILE, JSON.stringify(user));
            
            set({
              user,
              accessToken: access_token,
              refreshToken: refresh_token,
              isAuthenticated: true,
              isLoading: false,
            });
            return true;
          } else {
            throw new Error(response.message || 'Login failed');
          }
        } catch (error) {
          const message = error instanceof ApiError 
            ? error.message 
            : (error as Error).message || 'Login failed';
          set({ error: message, isLoading: false, isAuthenticated: false });
          return false;
        }
      },

      // Logout action
      logout: () => {
        // Invalidate token on backend (fire and forget)
        if (get().accessToken) {
          authService.logout().catch(() => {});
        }
        
        // Clear local storage
        localStorage.removeItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN);
        localStorage.removeItem(LOCAL_STORAGE_KEYS.USER_PROFILE);
        
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null,
        });
      },

      // Refresh access token
      refreshAccessToken: async () => {
        const refreshToken = get().refreshToken;
        if (!refreshToken) return;

        try {
          const response = await authService.refresh(refreshToken);
          
          if (response.success && response.data) {
            const { access_token, refresh_token, user } = response.data;
            
            localStorage.setItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN, access_token);
            localStorage.setItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN, refresh_token);
            localStorage.setItem(LOCAL_STORAGE_KEYS.USER_PROFILE, JSON.stringify(user));
            
            set({
              user,
              accessToken: access_token,
              refreshToken: refresh_token,
            });
          }
        } catch (error) {
          get().logout();
        }
      },

      // Fetch current user
      fetchCurrentUser: async () => {
        set({ isLoading: true });
        try {
          const user = get().user;
          if (!user?.id) {
            set({ isLoading: false });
            return;
          }
          
          const response = await userService.getUserById(user.id);
          
          if (response.success && response.data) {
            set({ user: response.data, isLoading: false });
          }
        } catch (error) {
          set({ isLoading: false });
        }
      },

      // Check if user has specific role
      hasRole: (role: UserRole): boolean => {
        const user = get().user;
        if (!user) return false;
        return user.role === role;
      },

      // Check if user has any of the specified roles
      hasAnyRole: (roles: UserRole[]): boolean => {
        const user = get().user;
        if (!user) return false;
        const userRoleLevel = ROLE_HIERARCHY[user.role];
        return roles.some(role => ROLE_HIERARCHY[role] <= userRoleLevel);
      },
    }),
    {
      name: 'land-intelligence-auth',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Main hook for useAuth
export const useAuth = () => {
  const store = useAuthStore();
  
  return {
    state: {
      user: store.user,
      accessToken: store.accessToken,
      refreshToken: store.refreshToken,
      isAuthenticated: store.isAuthenticated,
      isLoading: store.isLoading,
      error: store.error,
    },
    login: store.login,
    logout: store.logout,
    refreshAccessToken: store.refreshAccessToken,
    fetchCurrentUser: store.fetchCurrentUser,
    hasRole: store.hasRole,
    hasAnyRole: store.hasAnyRole,
  };
};

// Convenience hooks for role-based access
export const useUser = () => useAuthStore(state => state.user);
export const useAccessToken = () => useAuthStore(state => state.accessToken);
export const useRefreshToken = () => useAuthStore(state => state.refreshToken);
export const useAuthLoading = () => useAuthStore(state => state.isLoading);
export const useAuthError = () => useAuthStore(state => state.error);
export const useAuthStatus = () => {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);
  const user = useAuthStore(state => state.user);
  
  return {
    isAuthenticated,
    user,
    isLoading: useAuthStore(state => state.isLoading),
    hasRole: useAuthStore(state => state.hasRole),
    hasAnyRole: useAuthStore(state => state.hasAnyRole),
  };
};
export const useUserRole = () => useAuthStore(state => state.user?.role);
export const useIsAuthenticated = () => useAuthStore(state => state.isAuthenticated);
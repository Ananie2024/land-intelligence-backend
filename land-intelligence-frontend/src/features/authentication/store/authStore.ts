// Authentication Store
// Land Intelligence System

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '@/services/authService';
import { userService } from '@/services/userService';
import { LOCAL_STORAGE_KEYS } from '@/utils/constants';
import { ApiError } from '@/api/axios';
import type { LoginCredentials } from '../types/auth';
import type { UserResponse, UserRole } from '@/types/user';

// Role hierarchy: admin > client > viewer
const ROLE_HIERARCHY: Record<UserRole, number> = {
  admin: 3,
  client: 2,
  viewer: 1,
};

// Auth state interface
interface AuthState {
  user: UserResponse | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  initializeFromStorage: () => void;
  setupUnauthorizedListener: () => () => void;
  login: (credentials: LoginCredentials) => Promise<boolean>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
  hasRole: (role: UserRole) => boolean;
  hasAnyRole: (roles: UserRole[]) => boolean;
}

// Create the store with middleware - use proper typing for zustand v5
// Using any type to work around middleware typing incompatibility
export const useAuthStore: any = create(
  // @ts-ignore
  persist(
    (set: (partial: Partial<AuthState>) => void, get: () => AuthState) => ({
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
        const refreshTokenVal = localStorage.getItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN);
        const userProfile = localStorage.getItem(LOCAL_STORAGE_KEYS.USER_PROFILE);

        if (token && refreshTokenVal && userProfile) {
          try {
            const user = JSON.parse(userProfile) as UserResponse;
            set({
              user,
              accessToken: token,
              refreshToken: refreshTokenVal,
              isAuthenticated: true,
            });
          } catch (e) {
            console.error('Failed to parse user profile', e);
            get().logout();
          }
        }
      },

      // Listen for unauthorized events from axios interceptor
      setupUnauthorizedListener: () => {
        const handleUnauthorized = () => {
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            error: 'Session expired. Please log in again.',
          });
        };

        window.addEventListener('auth:unauthorized', handleUnauthorized);

        // Return cleanup function
        return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
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
        const currentToken = get().accessToken;
        if (currentToken) {
          authService.logout().catch(() => { });
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
        const refreshTokenValue = get().refreshToken;
        if (!refreshTokenValue) return;

        try {
          const response = await authService.refresh(refreshTokenValue);

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
            // Update both localStorage and state
            localStorage.setItem(LOCAL_STORAGE_KEYS.USER_PROFILE, JSON.stringify(response.data));
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

      // Check if user has any of the specified roles (with hierarchy support)
      hasAnyRole: (roles: UserRole[]): boolean => {
        const user = get().user;
        if (!user) return false;
        const userRole = user.role as UserRole;
        const userRoleLevel = ROLE_HIERARCHY[userRole];
        return roles.some(role => ROLE_HIERARCHY[role] <= userRoleLevel);
      },
    }),
    {
      name: 'land-intelligence-auth',
      partialize: (state: AuthState) => ({
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
  const user = useAuthStore((state: AuthState) => state.user);
  const accessToken = useAuthStore((state: AuthState) => state.accessToken);
  const refreshToken = useAuthStore((state: AuthState) => state.refreshToken);
  const isAuthenticated = useAuthStore((state: AuthState) => state.isAuthenticated);
  const isLoading = useAuthStore((state: AuthState) => state.isLoading);
  const error = useAuthStore((state: AuthState) => state.error);
  const login = useAuthStore((state: AuthState) => state.login);
  const logout = useAuthStore((state: AuthState) => state.logout);
  const refreshAccessToken = useAuthStore((state: AuthState) => state.refreshAccessToken);
  const fetchCurrentUser = useAuthStore((state: AuthState) => state.fetchCurrentUser);
  const hasRole = useAuthStore((state: AuthState) => state.hasRole);
  const hasAnyRole = useAuthStore((state: AuthState) => state.hasAnyRole);

  return {
    state: {
      user,
      accessToken,
      refreshToken,
      isAuthenticated,
      isLoading,
      error,
    },
    login,
    logout,
    refreshAccessToken,
    fetchCurrentUser,
    hasRole,
    hasAnyRole,
  };
};

// Convenience hooks for role-based access
export const useUser = () => useAuthStore((state: AuthState) => state.user);
export const useAccessToken = () => useAuthStore((state: AuthState) => state.accessToken);
export const useRefreshToken = () => useAuthStore((state: AuthState) => state.refreshToken);
export const useAuthLoading = () => useAuthStore((state: AuthState) => state.isLoading);
export const useAuthError = () => useAuthStore((state: AuthState) => state.error);
export const useAuthStatus = () => {
  const isAuthenticated = useAuthStore((state: AuthState) => state.isAuthenticated);
  const user = useAuthStore((state: AuthState) => state.user);

  return {
    isAuthenticated,
    user,
    isLoading: useAuthStore((state: AuthState) => state.isLoading),
    hasRole: useAuthStore((state: AuthState) => state.hasRole),
    hasAnyRole: useAuthStore((state: AuthState) => state.hasAnyRole),
  };
};
export const useUserRole = () => useAuthStore((state: AuthState) => state.user?.role);
export const useIsAuthenticated = () => useAuthStore((state: AuthState) => state.isAuthenticated);

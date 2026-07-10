// Auth Provider Component
// Land Intelligence System
// Handles session restoration and automatic logout on unauthorized responses

import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isInitializing, setIsInitializing] = useState(true);
  const isAuthenticated = useAuthStore((state: any) => state.isAuthenticated);
  const user = useAuthStore((state: any) => state.user);
  const initializeFromStorage = useAuthStore((state: any) => state.initializeFromStorage);
  const setupUnauthorizedListener = useAuthStore((state: any) => state.setupUnauthorizedListener);
  const refreshAccessToken = useAuthStore((state: any) => state.refreshAccessToken);
  const logout = useAuthStore((state: any) => state.logout);

  // Session restoration on mount
  useEffect(() => {
    initializeFromStorage();
    setIsInitializing(false);
  }, [initializeFromStorage]);

  // Setup unauthorized event listener
  useEffect(() => {
    const cleanup = setupUnauthorizedListener();
    return cleanup;
  }, [setupUnauthorizedListener]);

  // Handle automatic token refresh on visibility change (tab focus)
  useEffect(() => {
    const handleVisibilityChange = async () => {
      if (document.visibilityState === 'visible' && isAuthenticated) {
        // Check if token might be expired and refresh if needed
        try {
          await refreshAccessToken();
        } catch (error) {
          console.error('Token refresh failed on tab focus:', error);
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [isAuthenticated, refreshAccessToken]);

  // Listen for storage events for multi-tab sync
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'land_intel_access_token' && !e.newValue) {
        // Token was removed in another tab, logout current tab
        logout();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [logout]);

  // Show loading spinner while initializing
  if (isInitializing) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-slate-950">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return <>{children}</>;
};

export default AuthProvider;
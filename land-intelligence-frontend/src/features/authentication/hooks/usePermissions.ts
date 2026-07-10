// Permissions Hook
// Land Intelligence System
// Handles loading and checking user permissions

import { useEffect } from 'react';
import { useAuth } from '../store/authStore';
import { authService } from '@/services/authService';

interface PermissionState {
  permissions: string[];
  isLoading: boolean;
  error: string | null;
}

// Define all available permissions in the system
export const PERMISSIONS = {
  // Parcel permissions
  PARCELS_VIEW: 'parcels:view',
  PARCELS_CREATE: 'parcels:create',
  PARCELS_EDIT: 'parcels:edit',
  PARCELS_DELETE: 'parcels:delete',
  
  // Parish permissions
  PARISHES_VIEW: 'parishes:view',
  PARISHES_CREATE: 'parishes:create',
  PARISHES_EDIT: 'parishes:edit',
  
  // Document permissions
  DOCUMENTS_VIEW: 'documents:view',
  DOCUMENTS_UPLOAD: 'documents:upload',
  DOCUMENTS_DOWNLOAD: 'documents:download',
  DOCUMENTS_DELETE: 'documents:delete',
  
  // Tax permissions
  TAX_VIEW: 'tax:view',
  TAX_CALCULATE: 'tax:calculate',
  
  // User permissions
  USERS_VIEW: 'users:view',
  USERS_CREATE: 'users:create',
  USERS_EDIT: 'users:edit',
  USERS_DELETE: 'users:delete',
  
  // Backup permissions
  BACKUPS_VIEW: 'backups:view',
  BACKUPS_CREATE: 'backups:create',
  BACKUPS_RESTORE: 'backups:restore',
  
  // QR permissions
  QR_VIEW: 'qr:view',
  QR_GENERATE: 'qr:generate',
} as const;

export type Permission = (typeof PERMISSIONS)[keyof typeof PERMISSIONS];

// Role-based permission mapping
const ROLE_PERMISSIONS: Record<string, Permission[]> = {
  admin: Object.values(PERMISSIONS), // All permissions
  client: [
    PERMISSIONS.PARCELS_VIEW,
    PERMISSIONS.PARISHES_VIEW,
    PERMISSIONS.DOCUMENTS_VIEW,
    PERMISSIONS.QR_VIEW,
  ],
  viewer: [
    PERMISSIONS.PARCELS_VIEW,
    PERMISSIONS.PARISHES_VIEW,
    PERMISSIONS.DOCUMENTS_VIEW,
    PERMISSIONS.QR_VIEW,
  ],
};

// Hook to load and manage permissions
export function usePermissions() {
  const { state } = useAuth();
  const userRole = state.user?.role;

  // Get permissions for current user role
  const getUserPermissions = (): Permission[] => {
    if (!userRole) return [];
    return ROLE_PERMISSIONS[userRole] || [];
  };

  // Check if user has a specific permission
  const hasPermission = (permission: Permission): boolean => {
    const permissions = getUserPermissions();
    return permissions.includes(permission);
  };

  // Check if user has all specified permissions
  const hasAllPermissions = (permissions: Permission[]): boolean => {
    return permissions.every(permission => hasPermission(permission));
  };

  // Check if user has any of the specified permissions
  const hasAnyPermission = (permissions: Permission[]): boolean => {
    return permissions.some(permission => hasPermission(permission));
  };

  return {
    permissions: getUserPermissions(),
    hasPermission,
    hasAllPermissions,
    hasAnyPermission,
    isLoading: state.isLoading,
    error: state.error,
  };
}

// Hook to load permissions from backend (if API supports it)
export function usePermissionsLoader() {
  const { state } = useAuth();
  
  useEffect(() => {
    // This would be used to fetch permissions from the backend
    // For now, we use role-based permissions
    const loadPermissions = async () => {
      if (state.isAuthenticated && state.accessToken) {
        // Future: fetch permissions from /auth/permissions endpoint
        // const response = await authService.getPermissions();
      }
    };
    
    loadPermissions();
  }, [state.isAuthenticated, state.accessToken]);
}

export default usePermissions;
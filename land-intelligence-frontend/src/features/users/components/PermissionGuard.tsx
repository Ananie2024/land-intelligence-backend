// Permission Guard Component
// Land Intelligence System

import React from 'react';
import type { UserRole } from '@/types/user';

interface PermissionGuardProps {
  children: React.ReactNode;
  allowedRoles: UserRole[];
  fallback?: React.ReactNode;
}

export const PermissionGuard: React.FC<PermissionGuardProps> = ({ 
  children, 
  allowedRoles,
  fallback = null 
}) => {
  // Get user from authentication - will use the hook from authentication feature
  const isAuthenticated = false; // Placeholder - will be connected to useAuth
  const userRole: UserRole | undefined = undefined; // Placeholder
  
  if (!isAuthenticated || !userRole) {
    return <>{fallback}</>;
  }

  // Role hierarchy check
  const ROLE_HIERARCHY: Record<UserRole, number> = {
    admin: 3,
    client: 2,
    viewer: 1,
  };

  const hasAccess = allowedRoles.some(role => 
    ROLE_HIERARCHY[role] <= ROLE_HIERARCHY[userRole]
  );

  if (!hasAccess) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};

export default PermissionGuard;
// Permission Guard Component
// Land Intelligence System

import React from 'react';
import { useAuth } from '@/features/authentication/hooks/useAuth';
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
  // Get user from authentication context
  const auth = useAuth();
  const user = auth.state?.user;
  const isAuthenticated = auth.state?.isAuthenticated;
  const userRole = user?.role as UserRole | undefined;
  
  if (!isAuthenticated || !userRole) {
    return <>{fallback}</>;
  }

  // Role hierarchy check
  const ROLE_HIERARCHY: Record<string, number> = {
    admin: 3,
    client: 2,
    viewer: 1,
  };

  const hasAccess = allowedRoles.some(role => 
    ROLE_HIERARCHY[role] <= ROLE_HIERARCHY[userRole as string]
  );

  if (!hasAccess) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};

export default PermissionGuard;

// Role Guard Component
// Land Intelligence System

import React from 'react';
import { useAuth } from '../store/authStore';
import type { UserRole } from '@/types/user';

interface RoleGuardProps {
  children: React.ReactNode;
  allowedRoles: UserRole[];
  fallback?: React.ReactNode;
}

export const RoleGuard: React.FC<RoleGuardProps> = ({ 
  children, 
  allowedRoles,
  fallback = null 
}) => {
  const { state } = useAuth();

  if (!state.isAuthenticated || !state.user) {
    return <>{fallback}</>;
  }

  // Check if user has any of the allowed roles
  const hasAccess = allowedRoles.includes(state.user.role);

  if (!hasAccess) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};

export default RoleGuard;
import React from 'react';
import { Navigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '@/features/authentication';
import { SessionTimeoutWarning } from '@/features/authentication/components/SessionTimeoutWarning';

interface ProtectedRouteProps {
  allowedRoles?: ('admin' | 'client' | 'viewer')[];
}

// Role hierarchy: admin > client > viewer
const ROLE_HIERARCHY: Record<string, number> = {
  admin: 3,
  client: 2,
  viewer: 1,
};

// Check if user has access based on role hierarchy
const hasRoleAccess = (userRole: string | undefined, allowedRoles?: ('admin' | 'client' | 'viewer')[]): boolean => {
  if (!allowedRoles || allowedRoles.length === 0) return true;
  if (!userRole) return false;
  const userRoleLevel = ROLE_HIERARCHY[userRole as 'admin' | 'client' | 'viewer'];
  return allowedRoles.some(role => ROLE_HIERARCHY[role] <= userRoleLevel);
};

export function ProtectedRoute({ allowedRoles }: ProtectedRouteProps) {
  const { state } = useAuth();
  const location = useLocation();

  // Check if user is authenticated
  if (!state.isAuthenticated) {
    // Redirect to login if user is not authenticated
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check role-based access if roles are specified
  if (allowedRoles && state.user) {
    if (!hasRoleAccess(state.user.role, allowedRoles)) {
      // Redirect to unauthorized page if user role is not permitted
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return (
    <>
      {/* Session timeout warning - appears when session is about to expire */}
      <SessionTimeoutWarning />
      <Outlet />
    </>
  );
}
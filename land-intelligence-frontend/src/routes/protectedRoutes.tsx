import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '@/features/authentication';

interface ProtectedRouteProps {
  allowedRoles?: ('admin' | 'client' | 'viewer')[];
}

export function ProtectedRoute({ allowedRoles }: ProtectedRouteProps) {
  const { state } = useAuth();
  const location = useLocation();

  if (!state.isAuthenticated) {
    // Redirect to login if user is not authenticated
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && state.user) {
    const hasAccess = allowedRoles.includes(state.user.role);
    if (!hasAccess) {
      // Redirect to unauthorized page if user role is not permitted
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return <Outlet />;
}
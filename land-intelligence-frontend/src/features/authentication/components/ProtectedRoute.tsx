// Protected Route Component
// Land Intelligence System

import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../store/authStore';
import type { UserRole } from '@/types/user';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: UserRole[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRoles 
}) => {
  const { state } = useAuth();
  const location = useLocation();

  // Check if user is authenticated
  if (!state.isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

// Check role-based access if roles are specified
  if (requiredRoles && state.user) {
    const hasAccess = requiredRoles.some(role => state.user?.role === role);
    if (!hasAccess) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return <>{children}</>;
};

export default ProtectedRoute;
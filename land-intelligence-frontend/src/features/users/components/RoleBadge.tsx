// Role Badge Component
// Land Intelligence System

import type { UserRole } from '@/types/user';

interface RoleBadgeProps {
  role: UserRole;
  className?: string;
}

const ROLE_STYLES: Record<UserRole, string> = {
  admin: 'bg-purple-100 text-purple-800',
  client: 'bg-blue-100 text-blue-800',
  viewer: 'bg-gray-100 text-gray-800',
};

export const RoleBadge: React.FC<RoleBadgeProps> = ({ role, className = '' }) => {
  return (
    <span 
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${ROLE_STYLES[role]} ${className}`}
    >
      {role.charAt(0).toUpperCase() + role.slice(1)}
    </span>
  );
};

export default RoleBadge;
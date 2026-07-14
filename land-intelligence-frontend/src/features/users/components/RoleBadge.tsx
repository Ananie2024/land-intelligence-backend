// Role Badge Component
// Land Intelligence System

import type { UserRole } from '@/types/user';

interface RoleBadgeProps {
  role: UserRole;
  className?: string;
}

const ROLE_STYLES: Record<UserRole, string> = {
  admin: 'bg-purple-500/20 text-purple-400',
  client: 'bg-primary-500/20 text-primary-400',
  viewer: 'bg-slate-700/50 text-slate-300',
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

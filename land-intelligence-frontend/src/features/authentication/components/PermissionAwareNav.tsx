// Permission-Aware Navigation Component
// Land Intelligence System
// Dynamically shows/hides navigation items based on user role

import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../store/authStore';
import type { UserRole } from '@/types/user';

export interface NavItem {
  name: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  requiredRoles?: UserRole[];
}

export interface NavGroup {
  title: string;
  roles?: UserRole[];
  links: NavItem[];
}

interface PermissionAwareNavProps {
  groups: NavGroup[];
  onItemClick?: () => void;
}

// Check role hierarchy
const ROLE_HIERARCHY: Record<UserRole, number> = {
  admin: 3,
  client: 2,
  viewer: 1,
};

// Check if user can see this navigation item
const canAccessItem = (requiredRoles?: UserRole[], userRole?: UserRole): boolean => {
  if (!requiredRoles || requiredRoles.length === 0) return true;
  if (!userRole) return false;
  
  const userRoleLevel = ROLE_HIERARCHY[userRole];
  return requiredRoles.some(role => ROLE_HIERARCHY[role] <= userRoleLevel);
};

// Check if user can see this navigation group
const canAccessGroup = (roles?: UserRole[], userRole?: UserRole): boolean => {
  if (!roles || roles.length === 0) return true;
  if (!userRole) return false;
  
  const userRoleLevel = ROLE_HIERARCHY[userRole];
  return roles.some(role => ROLE_HIERARCHY[role] <= userRoleLevel);
};

export const PermissionAwareNav: React.FC<PermissionAwareNavProps> = ({ groups, onItemClick }) => {
  const { state } = useAuth();
  const userRole = state.user?.role as UserRole | undefined;

  // Filter groups and items based on permissions
  const visibleGroups = groups
    .filter(group => canAccessGroup(group.roles, userRole))
    .map(group => ({
      ...group,
      links: group.links.filter(link => canAccessItem(link.requiredRoles, userRole)),
    }))
    .filter(group => group.links.length > 0);

  return (
    <nav className="flex-grow p-4 space-y-6 overflow-y-auto">
      {visibleGroups.map((group, groupIdx) => (
        <div key={groupIdx} className="space-y-2">
          <h4 className="text-[10px] font-bold text-gold-400 uppercase tracking-widest px-3">
            {group.title}
          </h4>
          <ul className="space-y-1">
            {group.links.map((link, linkIdx) => (
              <li key={linkIdx}>
                <NavLink
                  to={link.path}
                  onClick={onItemClick}
                  className={(props: { isActive: boolean }) => `
                    flex items-center gap-3 px-3 py-2 text-sm font-semibold rounded-lg transition-all duration-200 group
                    ${
                      props.isActive
                        ? 'bg-primary-500/20 text-white border-l-2 border-primary-400 pl-2.5'
                        : 'text-slate-300 hover:text-white hover:bg-slate-700/50'
                    }
                  `}
                >
                  {(props: { isActive: boolean }) => {
                    const Icon = link.icon;
                    return (
                      <>
                        <Icon
                          className={`w-4 h-5 transition-colors ${
                            props.isActive ? 'text-primary-400' : 'text-slate-400 group-hover:text-primary-400'
                          }`}
                        />
                        {link.name}
                      </>
                    );
                  }}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
};

export default PermissionAwareNav;
import React from 'react';
import {
  LayoutDashboard,
  Map,
  FileText,
  Users,
  Settings,
  Database,
  QrCode,
  DollarSign,
  Building2,
  X,
} from 'lucide-react';
import { env } from '@/utils/env';
import { PermissionAwareNav } from '@/features/authentication/components/PermissionAwareNav';
import type { NavGroup } from '@/features/authentication/components/PermissionAwareNav';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  // Define navigation structure with role requirements
  const menuItems: NavGroup[] = [
    {
      title: 'General',
      links: [
        { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
        { name: 'Land Parcels', path: '/parcels', icon: Map },
        { name: 'Parishes', path: '/parishes', icon: Building2 },
      ],
    },
    {
      title: 'Services',
      links: [
        { name: 'Document Archive', path: '/documents', icon: FileText },
        { name: 'Tax Calculations', path: '/tax', icon: DollarSign },
        { name: 'QR Codes', path: '/qr', icon: QrCode },
      ],
    },
    {
      title: 'Administration',
      roles: ['admin'], // Only show this group for admin users
      links: [
        { name: 'User Management', path: '/users', icon: Users, requiredRoles: ['admin'] },
        { name: 'System Backups', path: '/backups', icon: Database, requiredRoles: ['admin'] },
        { name: 'Settings', path: '/settings', icon: Settings, requiredRoles: ['admin'] },
      ],
    },
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm lg:hidden"
        />
      )}

      {/* Sidebar Navigation */}
      <aside
        className={`
          fixed top-0 bottom-0 left-0 z-40 w-64 border-r border-slate-900 bg-slate-950 flex flex-col transition-transform duration-300
          lg:translate-x-0 lg:static lg:h-screen
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Header Branding */}
        <div className="h-16 px-6 border-b border-slate-900 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-accent-600 flex items-center justify-center font-black text-white shadow-md shadow-primary-500/20">
              L
            </div>
            <span className="text-white font-extrabold text-base tracking-tight truncate max-w-[170px]">
              {env.VITE_APP_NAME}
            </span>
          </div>

          {/* Close button for mobile drawer */}
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors lg:hidden"
            aria-label="Close menu drawer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Permission-Aware Navigation Items */}
        <PermissionAwareNav groups={menuItems} onItemClick={onClose} />

        {/* Footer info/System status */}
        <div className="p-4 border-t border-slate-900 bg-slate-900/20 text-[10px] text-slate-500 flex items-center justify-between">
          <span>v1.0.0</span>
          <span className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
            API Connected
          </span>
        </div>
      </aside>
    </>
  );
}
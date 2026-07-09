import React from 'react';
import { NavLink } from 'react-router-dom';
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

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const menuItems = [
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
      links: [
        { name: 'User Management', path: '/users', icon: Users },
        { name: 'System Backups', path: '/backups', icon: Database },
        { name: 'Settings', path: '/settings', icon: Settings },
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

        {/* Navigation Items */}
        <nav className="flex-grow p-4 space-y-6 overflow-y-auto">
          {menuItems.map((group, groupIdx) => (
            <div key={groupIdx} className="space-y-2">
              <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-3">
                {group.title}
              </h4>
              <ul className="space-y-1">
                {group.links.map((link, linkIdx) => (
                  <li key={linkIdx}>
                    <NavLink
                      to={link.path}
                      onClick={onClose}
                      className={({ isActive }) => `
                        flex items-center gap-3 px-3 py-2 text-sm font-semibold rounded-lg transition-all duration-200 group
                        ${
                          isActive
                            ? 'bg-primary-600/10 text-primary-400 border-l-2 border-primary-500 pl-2.5'
                            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                        }
                      `}
                    >
                      {({ isActive }) => {
                        const Icon = link.icon;
                        return (
                          <>
                            <Icon
                              className={`w-4 h-5 transition-colors ${
                                isActive ? 'text-primary-400' : 'text-slate-400 group-hover:text-slate-200'
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

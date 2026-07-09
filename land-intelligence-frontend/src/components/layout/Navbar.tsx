import React, { useState, useRef, useEffect } from 'react';
import { Menu, Bell, User, LogOut, ChevronDown, ShieldCheck } from 'lucide-react';
import { LOCAL_STORAGE_KEYS } from '@/utils/constants';

interface NavbarProps {
  onToggleSidebar: () => void;
}

export function Navbar({ onToggleSidebar }: NavbarProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  // Placeholder user profile data, fallback if localStorage is empty
  const [userInfo, setUserInfo] = useState({
    username: 'Guest',
    email: 'guest@archdiocese-kigali.org',
    role: 'viewer',
    full_name: 'Guest User',
  });

  useEffect(() => {
    try {
      const storedUser = localStorage.getItem(LOCAL_STORAGE_KEYS.USER_PROFILE);
      if (storedUser) {
        setUserInfo(JSON.parse(storedUser));
      }
    } catch (e) {
      console.warn('Failed to load user profile from storage', e);
    }
  }, []);

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(LOCAL_STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(LOCAL_STORAGE_KEYS.USER_PROFILE);
    window.location.href = '/login';
  };

  return (
    <header className="h-16 px-6 border-b border-slate-900 bg-slate-950/40 backdrop-blur-md flex items-center justify-between sticky top-0 z-30">
      {/* Mobile Toggle Button */}
      <button
        onClick={onToggleSidebar}
        className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors lg:hidden"
        aria-label="Toggle sidebar menu"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* Spacing or Search Input */}
      <div className="hidden sm:flex items-center gap-2">
        <span className="text-slate-500 text-xs font-semibold uppercase tracking-widest bg-slate-900 border border-slate-800/80 px-2.5 py-1 rounded-md flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-success" />
          Kigali Archdiocese
        </span>
      </div>

      {/* Right side operations */}
      <div className="flex items-center gap-4 ml-auto">
        {/* Notifications Bell */}
        <button className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-primary-500 ring-2 ring-slate-950" />
        </button>

        {/* User Profile Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="flex items-center gap-2.5 p-1 px-2.5 rounded-xl hover:bg-slate-800/50 transition-colors"
          >
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-primary-500 to-accent-500 flex items-center justify-center font-bold text-white text-sm shadow-md">
              {userInfo.full_name?.charAt(0) || userInfo.username?.charAt(0) || 'U'}
            </div>
            <div className="text-left hidden md:block">
              <p className="text-xs text-white font-bold leading-none">{userInfo.full_name || userInfo.username}</p>
              <p className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider mt-0.5">{userInfo.role}</p>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </button>

          {isDropdownOpen && (
            <div className="absolute right-0 mt-2.5 w-56 rounded-xl border border-slate-800 bg-slate-900 p-2 shadow-2xl z-50">
              <div className="px-3.5 py-2.5 border-b border-slate-800">
                <p className="text-xs text-slate-400 font-medium">Logged in as</p>
                <p className="text-sm font-bold text-white truncate mt-0.5">{userInfo.email}</p>
              </div>
              <div className="py-1">
                <a
                  href="/profile"
                  className="flex items-center gap-2.5 px-3.5 py-2 text-sm text-slate-300 rounded-lg hover:bg-slate-800 hover:text-white transition-colors"
                  onClick={(e) => {
                    e.preventDefault();
                    window.location.href = '/profile';
                  }}
                >
                  <User className="w-4 h-4" />
                  My Profile
                </a>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2.5 w-full text-left px-3.5 py-2 text-sm text-danger rounded-lg hover:bg-danger/10 hover:text-white transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  Log Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

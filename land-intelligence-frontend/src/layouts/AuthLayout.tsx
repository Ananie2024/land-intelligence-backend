import React from 'react';
import { Outlet } from 'react-router-dom';
import { env } from '@/utils/env';

export default function AuthLayout() {
  return (
    <div className="min-h-screen w-screen bg-slate-950 flex flex-col items-center justify-center p-4 md:p-6 font-sans relative">
      {/* Background visual graphics */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute inset-0 bg-dot-pattern pointer-events-none opacity-30 z-0" />

      {/* Main glass box container */}
      <div className="w-full max-w-[440px] glass-panel rounded-2xl shadow-2xl p-8 z-10 relative border border-slate-800/80 bg-slate-900/40">
        
        {/* App Logo & Branding */}
        <div className="flex flex-col items-center text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-accent-600 flex items-center justify-center font-black text-white text-xl shadow-lg shadow-primary-500/20 mb-4">
            L
          </div>
          <h2 className="text-xl font-extrabold text-white tracking-tight leading-none m-0">
            {env.VITE_APP_NAME}
          </h2>
          <p className="text-xs text-slate-400 font-medium mt-2 leading-relaxed max-w-[280px]">
            Archdiocese of Kigali • Digital Land Management System
          </p>
        </div>

        {/* Form content Outlet */}
        <Outlet />

      </div>

      {/* System Status info */}
      <div className="absolute bottom-6 text-[10px] text-slate-500 font-medium z-10 select-none">
        Kigali Archdiocese Land Records System • Secure Access Required
      </div>
    </div>
  );
}

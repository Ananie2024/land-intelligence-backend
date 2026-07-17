import React from 'react';
import { Outlet } from 'react-router-dom';

export default function MainLayout() {
  return (
    <div className="min-h-screen bg-bg-base text-slate-200 flex flex-col relative font-sans">
      <div className="absolute inset-0 bg-dot-pattern pointer-events-none opacity-[0.15] z-0" />
      <div className="flex-grow z-10 flex flex-col">
        <Outlet />
      </div>
    </div>
  );
}

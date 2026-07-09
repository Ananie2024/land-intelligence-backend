import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from '@/components/layout/Sidebar';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';

export default function DashboardLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 font-sans">
      {/* Sidebar Drawer */}
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />

      {/* Main Body */}
      <div className="flex flex-col flex-grow min-w-0 overflow-hidden relative">
        {/* Dot pattern background */}
        <div className="absolute inset-0 bg-dot-pattern pointer-events-none opacity-[0.25] z-0" />

        {/* Top Navbar */}
        <Navbar onToggleSidebar={() => setIsSidebarOpen(true)} />

        {/* Dynamic Route Content */}
        <main className="flex-grow overflow-y-auto relative z-10 flex flex-col">
          <Outlet />
          <Footer />
        </main>
      </div>
    </div>
  );
}

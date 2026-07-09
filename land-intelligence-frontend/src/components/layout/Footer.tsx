import React from 'react';
import { env } from '@/utils/env';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="w-full py-6 px-8 border-t border-slate-900 bg-slate-950/40 text-center text-xs text-slate-500 mt-auto flex flex-col sm:flex-row items-center justify-between gap-4">
      <div>
        &copy; {currentYear} {env.VITE_APP_NAME}. Archdiocese of Kigali. All rights reserved.
      </div>
      <div className="flex items-center gap-6">
        <a href="#" className="hover:text-slate-300 transition-colors">Privacy Policy</a>
        <a href="#" className="hover:text-slate-300 transition-colors">Terms of Service</a>
        <a href="#" className="hover:text-slate-300 transition-colors">Support & Helpdesk</a>
      </div>
    </footer>
  );
}

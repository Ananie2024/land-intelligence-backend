import React from 'react';
import { env } from '@/utils/env';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="w-full py-6 px-8 border-t border-slate-700 bg-bg-surface/40 text-center text-xs text-slate-400 mt-auto flex flex-col sm:flex-row items-center justify-between gap-4">
      <div>
        &copy; {currentYear} <span className="text-white font-semibold">{env.VITE_APP_NAME}</span>.{' '}
        <span className="text-gold-400">Archdiocese of Kigali</span>. All rights reserved.
      </div>
      <div className="flex items-center gap-6 text-slate-400">
        <a href="#" className="hover:text-gold-400 transition-colors">Privacy Policy</a>
        <a href="#" className="hover:text-gold-400 transition-colors">Terms of Service</a>
        <a href="#" className="hover:text-gold-400 transition-colors">Support & Helpdesk</a>
      </div>
    </footer>
  );
}
// Suspense Fallback Wrapper
// Land Intelligence System

import React from 'react';

export function SuspenseFallback({ children }: { children: React.ReactNode }) {
  return (
    <React.Suspense fallback={
      <div className="flex-grow flex items-center justify-center min-h-[300px]">
        <div className="rounded-full border-t-primary-500 border-slate-700 animate-spin w-8 h-8 border-3" />
      </div>
    }>
      {children}
    </React.Suspense>
  );
}

export default SuspenseFallback;
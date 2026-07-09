import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
  className?: string;
}

export function LoadingSpinner({ size = 'md', fullScreen = false, className = '' }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-5 h-5 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
  };

  const spinner = (
    <div
      className={`rounded-full border-t-primary-500 border-slate-700 animate-spin ${sizeClasses[size]} ${className}`}
      role="status"
      aria-label="loading"
    />
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm">
        <div className="flex flex-col items-center gap-3">
          {spinner}
          <span className="text-slate-400 text-sm font-medium animate-pulse">Loading Land System...</span>
        </div>
      </div>
    );
  }

  return spinner;
}

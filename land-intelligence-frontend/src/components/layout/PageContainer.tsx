import React from 'react';
import { LoadingSpinner } from '../ui/LoadingSpinner';

interface PageContainerProps {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  isLoading?: boolean;
  children: React.ReactNode;
  className?: string;
}

export function PageContainer({
  title,
  subtitle,
  action,
  isLoading = false,
  children,
  className = '',
}: PageContainerProps) {
  return (
    <div className={`flex flex-col gap-6 w-full p-6 md:p-8 animate-float ${className}`}>
      {/* Page Header */}
      {(title || subtitle || action) && (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-700 pb-6">
          <div>
            {title && (
              <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight leading-none m-0">
                {title}
              </h1>
            )}
            {subtitle && (
              <p className="text-slate-400 text-sm md:text-base mt-2 font-medium">
                {subtitle}
              </p>
            )}
          </div>
          {action && <div className="flex items-center gap-3">{action}</div>}
        </div>
      )}

      {/* Page Body */}
      <div className="relative flex-grow">
        {isLoading ? (
          <div className="flex items-center justify-center min-h-[300px]">
            <LoadingSpinner size="lg" className="border-t-primary-500" />
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
}
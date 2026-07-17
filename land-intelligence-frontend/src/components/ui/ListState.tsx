import React from 'react';
import { LoadingSpinner } from './LoadingSpinner';
import { Button } from './Button';

interface ListStateProps {
  isLoading: boolean;
  error: string | null;
  onRetry: () => void;
  label: string;
  children: React.ReactNode;
}

/**
 * Reusable component for rendering loading and error states in list pages.
 * Encapsulates the common pattern used across Backups, Documents, Parcels, Parishes, and Users pages.
 */
export function ListState({ isLoading, error, onRetry, label, children }: ListStateProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-3">
        <LoadingSpinner size="md" className="border-t-primary-500" />
        <span className="text-slate-400 text-xs">Loading {label}...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400 mb-4">{error}</p>
        <Button
          variant="primary"
          onClick={onRetry}
        >
          Try Again
        </Button>
      </div>
    );
  }

  return <>{children}</>;
}
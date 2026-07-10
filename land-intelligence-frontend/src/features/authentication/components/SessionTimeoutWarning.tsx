// Session Timeout Warning Component
// Land Intelligence System
// Shows a warning when session is about to expire

import React, { useState, useEffect } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { useAuth } from '../store/authStore';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

interface SessionTimeoutWarningProps {
  /** Time in minutes before token expiry to show warning */
  warningMinutes?: number;
  /** Auto-refresh enabled */
  autoRefresh?: boolean;
}

export const SessionTimeoutWarning: React.FC<SessionTimeoutWarningProps> = ({
  warningMinutes = 5,
  autoRefresh = true,
}) => {
  const { state, refreshAccessToken, logout } = useAuth();
  const [showWarning, setShowWarning] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);

  useEffect(() => {
    if (!state.accessToken) {
      setShowWarning(false);
      return;
    }

    // Try to get token expiry from the token itself (JWT)
    const getTokenExpiry = (): number | null => {
      try {
        const payload = JSON.parse(atob(state.accessToken!.split('.')[1]));
        return payload.exp ? payload.exp * 1000 : null; // Convert to milliseconds
      } catch {
        return null;
      }
    };

    const expiry = getTokenExpiry();
    if (!expiry) return;

    const checkExpiry = () => {
      const now = Date.now();
      const remaining = expiry - now;
      const warningThreshold = warningMinutes * 60 * 1000;

      if (remaining <= warningThreshold && remaining > 0) {
        setShowWarning(true);
        setTimeRemaining(Math.floor(remaining / 1000)); // in seconds
      } else {
        setShowWarning(false);
      }
    };

    checkExpiry();
    const interval = setInterval(checkExpiry, 1000);

    return () => clearInterval(interval);
  }, [state.accessToken, warningMinutes]);

  // Auto-refresh when warning shows
  useEffect(() => {
    if (showWarning && autoRefresh && !isRefreshing) {
      const handleAutoRefresh = async () => {
        setIsRefreshing(true);
        try {
          await refreshAccessToken();
        } catch (error) {
          console.error('Session refresh failed:', error);
        } finally {
          setIsRefreshing(false);
        }
      };
      
      // Attempt refresh immediately when warning shows
      handleAutoRefresh();
    }
  }, [showWarning, autoRefresh, refreshAccessToken, isRefreshing]);

  if (!showWarning) return null;

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="fixed top-16 right-4 z-50 max-w-sm w-full">
      <div className="rounded-xl border border-warning/30 bg-warning/10 p-4 shadow-2xl backdrop-blur-sm">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-warning">Session Expiring</h3>
            <p className="text-xs text-slate-300 mt-1">
              Your session will expire in {timeRemaining ? formatTime(timeRemaining) : 'a few minutes'}.
            </p>
            <div className="flex gap-2 mt-3">
              <button
                onClick={async () => {
                  setIsRefreshing(true);
                  try {
                    await refreshAccessToken();
                    setShowWarning(false);
                  } finally {
                    setIsRefreshing(false);
                  }
                }}
                disabled={isRefreshing}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
              >
                {isRefreshing ? <LoadingSpinner size="sm" /> : <RefreshCw className="w-3 h-3" />}
                Refresh Session
              </button>
              <button
                onClick={logout}
                className="px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors"
              >
                Log Out
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SessionTimeoutWarning;
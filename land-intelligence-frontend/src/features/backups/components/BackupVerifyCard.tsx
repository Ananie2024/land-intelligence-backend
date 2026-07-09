// Backup Verify Card Component
// Land Intelligence System

import { CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import type { BackupVerifyResponse } from '@/types/backup';

interface BackupVerifyCardProps {
  verifyData: BackupVerifyResponse | null;
  isLoading: boolean;
  onVerify: () => void;
}

export const BackupVerifyCard: React.FC<BackupVerifyCardProps> = ({ 
  verifyData, 
  isLoading, 
  onVerify 
}) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">Backup Verification</h3>
        <button
          onClick={onVerify}
          disabled={isLoading}
          className="flex items-center gap-2 px-3 py-1 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          Verify
        </button>
      </div>

      {verifyData && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            {verifyData.status === 'healthy' ? (
              <CheckCircle className="h-5 w-5 text-green-600" />
            ) : (
              <XCircle className="h-5 w-5 text-red-600" />
            )}
            <span className="font-medium">{verifyData.message}</span>
          </div>
          <div className="grid grid-cols-2 gap-4 mt-4">
            <div>
              <p className="text-sm text-gray-500">Total Backups</p>
              <p className="text-xl font-bold text-gray-900">{verifyData.backup_count}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Size</p>
              <p className="text-xl font-bold text-gray-900">{verifyData.total_size_mb.toFixed(1)} MB</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BackupVerifyCard;
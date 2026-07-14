// Backup Table Component
// Land Intelligence System

import { Download, Database, CheckCircle, XCircle, Clock } from 'lucide-react';
import type { Backup } from '@/types/backup';

interface BackupTableProps {
  backups: Backup[];
  onDownload: (backup: Backup) => void;
}

// Helper to normalize status for comparison
const normalizeStatus = (status: string | undefined): string => {
  return (status || 'pending').toUpperCase();
};

// Helper to check if backup is completed (handles both cases)
const isCompleted = (status: string | undefined): boolean => {
  return normalizeStatus(status) === 'COMPLETED';
};

export const BackupTable: React.FC<BackupTableProps> = ({ backups, onDownload }) => {
  if (!backups || backups.length === 0) {
    return (
      <div className="text-center py-12 text-slate-400">
        <p>No backups found</p>
      </div>
    );
  }

  const formatSize = (bytes: number | undefined) => {
    if (!bytes || bytes < 0) return '0 KB';
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getStatusStyles = (status: string | undefined) => {
    const normalized = normalizeStatus(status);
    switch (normalized) {
      case 'COMPLETED':
        return 'bg-success/20 text-success';
      case 'FAILED':
        return 'bg-red-500/20 text-red-400';
      case 'CANCELLED':
        return 'bg-slate-700/50 text-slate-300';
      case 'PENDING':
      case 'IN_PROGRESS':
      default:
        return 'bg-warning/20 text-warning';
    }
  };

  const getBackupTypeLabel = (backup: Backup) => {
    // Map job_type to display label
    if (backup.job_type) {
      return backup.job_type.toLowerCase();
    }
    return backup.backup_type || 'manual';
  };

  const getStatusDisplay = (status: string | undefined): string => {
    // Display the status in lowercase for UI
    return normalizeStatus(status).toLowerCase();
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-800">
        <thead className="bg-slate-900/60">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Filename
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Size
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Type
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Created
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-slate-900/40 divide-y divide-slate-800">
          {backups.map((backup) => (
            <tr key={backup.id} className="hover:bg-slate-900/60 transition-colors">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <Database className="h-5 w-5 text-slate-400 mr-2" />
                  <span className="font-mono text-sm text-slate-200">
                    {backup.filename || backup.destination_path?.split('/').pop() || 'backup.zip'}
                  </span>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                {formatSize(backup.file_size_bytes)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400 capitalize">
                {getBackupTypeLabel(backup)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusStyles(backup.status)}`}>
                  {isCompleted(backup.status) && <CheckCircle className="h-3 w-3 mr-1" />}
                  {normalizeStatus(backup.status) === 'FAILED' && <XCircle className="h-3 w-3 mr-1" />}
                  {(normalizeStatus(backup.status) === 'PENDING' || normalizeStatus(backup.status) === 'IN_PROGRESS') && <Clock className="h-3 w-3 mr-1" />}
                  {getStatusDisplay(backup.status)}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                {new Date(backup.created_at).toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  onClick={() => onDownload(backup)}
                  disabled={!isCompleted(backup.status)}
                  className="text-slate-400 hover:text-slate-200 disabled:opacity-50"
                  title="Download"
                >
                  <Download className="h-4 w-4" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default BackupTable;

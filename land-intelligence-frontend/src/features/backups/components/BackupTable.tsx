// Backup Table Component
// Land Intelligence System

import { Download, Database, CheckCircle, XCircle } from 'lucide-react';
import type { Backup } from '@/types/backup';

interface BackupTableProps {
  backups: Backup[];
  onDownload: (backup: Backup) => void;
}

export const BackupTable: React.FC<BackupTableProps> = ({ backups, onDownload }) => {
  if (!backups || backups.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No backups found</p>
      </div>
    );
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Filename
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Size
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Type
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Created
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {backups.map((backup) => (
            <tr key={backup.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <Database className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="font-mono text-sm text-gray-900">{backup.filename}</span>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatSize(backup.file_size_bytes)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">
                {backup.backup_type}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  backup.status === 'successful' 
                    ? 'bg-green-100 text-green-800'
                    : backup.status === 'failed'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {backup.status === 'successful' && <CheckCircle className="h-3 w-3 mr-1" />}
                  {backup.status === 'failed' && <XCircle className="h-3 w-3 mr-1" />}
                  {backup.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(backup.created_at).toLocaleString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  onClick={() => onDownload(backup)}
                  disabled={backup.status !== 'successful'}
                  className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
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
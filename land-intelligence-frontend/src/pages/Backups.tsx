import React, { useState, useEffect } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { Database, RefreshCw } from 'lucide-react';
import { backupService } from '@/services/backupService';
import type { Backup } from '@/types/backup';
import { BackupTable } from '@/features/backups/components/BackupTable';

export default function Backups() {
  const [backups, setBackups] = useState<Backup[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadBackups = async () => {
      try {
        const response = await backupService.getBackups();
        if (response.success && response.data) {
          setBackups(response.data);
        }
      } catch (error) {
        console.error('Failed to load backups', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadBackups();
  }, []);

  const handleCreateBackup = async () => {
    try {
      await backupService.createBackup();
      // Reload backups after creation
      const response = await backupService.getBackups();
      if (response.success && response.data) {
        setBackups(response.data);
      }
    } catch (error) {
      console.error('Failed to create backup', error);
    }
  };

  return (
    <PageContainer
      title="System Snapshots & Backups"
      subtitle="Administrative database backups and storage synchronization audits."
      action={
        <button
          onClick={handleCreateBackup}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          <RefreshCw className="w-4 h-4" />
          Backup Now
        </button>
      }
    >
      <div className="flex items-center gap-3 p-6 rounded-xl border border-slate-800/80 bg-slate-900/30 mb-6">
        <Database className="w-6 h-6 text-info" />
        <div className="text-sm">
          <p className="text-white font-bold">Cloud Sync Active</p>
          <p className="text-slate-400 mt-1">Automated cron runs sync snapshots to secure GCS bucket daily at 11:00 AM UTC.</p>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-slate-400">Loading backups...</div>
      ) : (
        <BackupTable 
          backups={backups}
          onDownload={(backup) => console.log('Download backup:', backup)}
        />
      )}
    </PageContainer>
  );
}
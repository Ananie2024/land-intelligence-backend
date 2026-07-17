// Backup List Page with Download Functionality
// Land Intelligence System

import { useState } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/ui/Button';
import { ListState } from '@/components/ui/ListState';
import { Database, RefreshCw } from 'lucide-react';
import { backupService } from '@/services/backupService';
import type { Backup } from '@/types/backup';
import { BackupTable } from '@/features/backups/components/BackupTable';
import { BackupVerifyCard } from '@/features/backups/components/BackupVerifyCard';
import { useResourceQuery } from '@/hooks/useResourceList';
import toast from 'react-hot-toast';

export default function Backups() {
  const [verifyData, setVerifyData] = useState<any>(null);
  const [isVerifying, setIsVerifying] = useState(false);

  const { data, isLoading, error, refetch } = useResourceQuery<Backup[]>(
    ['backups'],
    () => backupService.getBackups(),
  );

  const backups = data || [];

  const handleVerify = async () => {
    setIsVerifying(true);
    try {
      const response = await backupService.verifyBackups();
      if (response.success && response.data) {
        setVerifyData(response.data);
        toast.success('Backup verification completed');
      }
    } catch (err) {
      console.error('Failed to verify backups', err);
      toast.error('Failed to verify backups');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleCreateBackup = async () => {
    try {
      await backupService.triggerBackup({ jobType: 'backup' });
      toast.success('Backup initiated successfully');
      refetch();
    } catch (err) {
      console.error('Failed to create backup', err);
      toast.error('Failed to create backup');
    }
  };

  const handleDownload = async (backup: Backup) => {
    const normalizedStatus = (backup.status || '').toUpperCase();
    if (normalizedStatus !== 'COMPLETED') {
      toast.error('Only completed backups can be downloaded');
      return;
    }

    try {
      const blob = await backupService.downloadBackup(backup.id);
      const filename = backup.destination_path?.split('/').pop() || 
                       `backup_${backup.id}.zip`;

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.success('Backup downloaded successfully');
    } catch (err) {
      console.error('Failed to download backup', err);
      toast.error('Failed to download backup');
    }
  };

  const handleRetry = () => {
    refetch();
  };

  return (
    <PageContainer
      title="System Snapshots & Backups"
      subtitle="Administrative database backups and storage synchronization audits."
      action={
        <Button 
          variant="primary" 
          leftIcon={<RefreshCw className="w-4 h-4" />}
          onClick={handleCreateBackup}
        >
          Backup Now
        </Button>
      }
    >
      <div className="space-y-6">
        <div className="flex items-center gap-3 p-6 rounded-xl border border-slate-800/80 bg-slate-900/30">
          <Database className="w-6 h-6 text-info" />
          <div className="text-sm flex-1">
            <p className="text-white font-bold">Cloud Sync Active</p>
            <p className="text-slate-400 mt-1">Automated cron runs sync snapshots to secure GCS bucket daily at 11:00 AM UTC.</p>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            Refresh
          </Button>
        </div>

        <BackupVerifyCard 
          verifyData={verifyData}
          isLoading={isVerifying}
          onVerify={handleVerify}
        />

        <ListState 
          isLoading={isLoading} 
          error={error} 
          onRetry={handleRetry} 
          label="backups"
        >
          <BackupTable 
            backups={backups}
            onDownload={handleDownload}
          />
        </ListState>
      </div>
    </PageContainer>
  );
}
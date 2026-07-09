// Backup List Page
// Land Intelligence System

import { useState, useEffect } from 'react';
import { backupService } from '@/services/backupService';
import type { Backup, BackupVerifyResponse } from '@/types/backup';
import { BackupTable } from '../components/BackupTable';
import { BackupVerifyCard } from '../components/BackupVerifyCard';

export const BackupListPage: React.FC = () => {
  const [backups, setBackups] = useState<Backup[]>([]);
  const [verifyData, setVerifyData] = useState<BackupVerifyResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isVerifying, setIsVerifying] = useState(false);

  const loadBackups = async () => {
    setIsLoading(true);
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

  const handleVerify = async () => {
    setIsVerifying(true);
    try {
      const response = await backupService.verifyBackups();
      if (response.success && response.data) {
        setVerifyData(response.data);
      }
    } catch (error) {
      console.error('Failed to verify backups', error);
    } finally {
      setIsVerifying(false);
    }
  };

  useEffect(() => {
    loadBackups();
  }, []);

  const handleDownload = (backup: Backup) => {
    // Implementation for downloading backup files
    console.log('Download backup:', backup.filename);
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">System Backups</h1>
        <p className="text-gray-500">Manage database snapshots and cloud sync verification.</p>
      </div>

      <BackupVerifyCard 
        verifyData={verifyData}
        isLoading={isVerifying}
        onVerify={handleVerify}
      />

      {isLoading ? (
        <div className="text-center py-12">Loading backups...</div>
      ) : (
        <BackupTable 
          backups={backups}
          onDownload={handleDownload}
        />
      )}
    </div>
  );
};

export default BackupListPage;
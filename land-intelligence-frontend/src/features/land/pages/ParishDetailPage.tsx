// Parish Detail Page
// Land Intelligence System

import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { landService } from '@/services/landService';
import { ParishDetail } from '../components/ParishDetail';
import { Loader2, AlertCircle } from 'lucide-react';
import type { Parish } from '@/types/land';

export const ParishDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [parish, setParish] = useState<Parish | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const loadParish = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await landService.getParishById(id);
        if (response.success && response.data) {
          setParish(response.data);
        } else {
          setError(response.message || 'Failed to load parish');
        }
      } catch (err) {
        console.error('Failed to load parish:', err);
        setError('Failed to load parish details');
      } finally {
        setIsLoading(false);
      }
    };

    loadParish();
  }, [id]);

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[300px]">
        <div className="flex items-center gap-3 text-slate-400">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Loading parish details...</span>
        </div>
      </div>
    );
  }

  if (error || !parish) {
    return (
      <div className="p-6">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center gap-2 text-red-500 mb-2">
            <AlertCircle className="h-5 w-5" />
            <span className="font-medium">Error</span>
          </div>
          <p className="text-gray-500">{error || 'Parish not found'}</p>
          <p className="text-gray-400 text-sm mt-2">Parish ID: {id}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="bg-white shadow rounded-lg p-6">
        <ParishDetail parish={parish} />
      </div>
    </div>
  );
};

export default ParishDetailPage;
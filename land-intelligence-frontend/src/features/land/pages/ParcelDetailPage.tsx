// Parcel Detail Page
// Land Intelligence System

import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { landService } from '@/services/landService';
import { ParcelDetail } from '../components/ParcelDetail';
import { Loader2, AlertCircle } from 'lucide-react';
import type { Parcel } from '@/types/land';

export const ParcelDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [parcel, setParcel] = useState<Parcel | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const loadParcel = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await landService.getParcelById(id);
        if (response.success && response.data) {
          setParcel(response.data);
        } else {
          setError(response.message || 'Failed to load parcel');
        }
      } catch (err) {
        console.error('Failed to load parcel:', err);
        setError('Failed to load parcel details');
      } finally {
        setIsLoading(false);
      }
    };

    loadParcel();
  }, [id]);

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[300px]">
        <div className="flex items-center gap-3 text-slate-400">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Loading parcel details...</span>
        </div>
      </div>
    );
  }

  if (error || !parcel) {
    return (
      <div className="p-6">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center gap-2 text-red-500 mb-2">
            <AlertCircle className="h-5 w-5" />
            <span className="font-medium">Error</span>
          </div>
          <p className="text-gray-500">{error || 'Parcel not found'}</p>
          <p className="text-gray-400 text-sm mt-2">Parcel ID: {id}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="bg-white shadow rounded-lg p-6">
        <ParcelDetail parcel={parcel} />
      </div>
    </div>
  );
};

export default ParcelDetailPage;
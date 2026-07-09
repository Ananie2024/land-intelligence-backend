import React, { useState, useEffect } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { Table, Column } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { MapPin, Plus } from 'lucide-react';
import { landService } from '@/services/landService';
import type { Parcel } from '@/types/land';
import { ParcelTable } from '@/features/land/components/ParcelTable';

export default function Parcels() {
  const [parcels, setParcels] = useState<Parcel[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadParcels = async () => {
      try {
        const response = await landService.getParcels();
        if (response.success && response.data) {
          setParcels(response.data);
        }
      } catch (error) {
        console.error('Failed to load parcels', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadParcels();
  }, []);

  return (
    <PageContainer
      title="Land Parcels Registry"
      subtitle="Comprehensive list of church land properties registered within the Diocese."
      action={
        <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
          Register Parcel
        </Button>
      }
    >
      <div className="space-y-6">
        <div className="flex items-center gap-3 p-4 rounded-xl border border-slate-800/80 bg-slate-900/30">
          <div className="p-2 rounded-lg bg-primary-500/10 text-primary-400">
            <MapPin className="w-5 h-5" />
          </div>
          <div className="text-xs">
            <p className="text-white font-bold">GIS Coordinates Active</p>
            <p className="text-slate-500 mt-0.5">Click any parcel record to open structural documents or display boundary pins.</p>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-12 text-slate-400">Loading parcels...</div>
        ) : (
          <ParcelTable 
            parcels={parcels}
            onView={(parcel) => console.log('View parcel:', parcel)}
            onEdit={(parcel) => console.log('Edit parcel:', parcel)}
            onDelete={(parcel) => console.log('Delete parcel:', parcel)}
          />
        )}
      </div>
    </PageContainer>
  );
}
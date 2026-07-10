// GIS Map Page
// Land Intelligence System

import React, { useState, useEffect } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { GISMap } from '@/components/ui/GISMap';
import { Button } from '@/components/ui/Button';
import { RefreshCw, Layers } from 'lucide-react';
import { landService } from '@/services/landService';
import type { Parcel } from '@/types/land';
import { toast } from 'react-hot-toast';

import { parseWkbToCoordinates } from '@/utils/wkbParser';

interface ParcelGeoData {
  id: string;
  parcel_number: string;
  owner_name: string;
  area_sqm: number;
  geometry: [number, number][][]; // Array of polygon rings
  valuation?: number;
}

export default function GisPage() {
  const [parcels, setParcels] = useState<ParcelGeoData[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadParcels();
  }, []);

  const loadParcels = async () => {
    setIsLoading(true);
    try {
      const response = await landService.getParcelsForMap();
      if (response.success && response.data) {
        // Transform parcels to geo format for map
        // API returns parcels with geometry_wkb (hex string), parse to coordinates
        const geoParcels: ParcelGeoData[] = response.data.map((parcel: Parcel) => ({
          id: parcel.id,
          parcel_number: parcel.parcel_number,
          owner_name: parcel.owner_name,
          area_sqm: parcel.area_sqm,
          valuation: parcel.valuation ?? undefined,
          geometry: parseWkbToCoordinates(parcel.geometry_wkb),
        }));
        setParcels(geoParcels);
      } else {
        toast.error('Failed to load parcels for map');
      }
    } catch (error) {
      console.error('Failed to load parcels', error);
      toast.error('Failed to load parcels');
    } finally {
      setIsLoading(false);
    }
  };

  const handleParcelClick = (parcel: ParcelGeoData) => {
    console.log('Parcel clicked:', parcel);
    // Could open a side panel or modal with parcel details
  };

  return (
    <PageContainer
      title="GIS Map View"
      subtitle="Interactive map of land parcels and parish boundaries."
      action={
        <Button 
          variant="secondary" 
          leftIcon={<RefreshCw className="w-4 h-4" />}
          onClick={loadParcels}
          disabled={isLoading}
        >
          Refresh Map
        </Button>
      }
    >
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Parcel Map</CardTitle>
            <CardDescription>
              Visualize registered land parcels with color-coded valuation tiers
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 mb-3 text-xs">
              <Layers className="w-4 h-4 text-slate-400" />
              <span className="text-slate-400">
                Legend: 
                <span className="ml-2 px-2 py-0.5 rounded bg-slate-500/20">No valuation</span>
                <span className="ml-2 px-2 py-0.5 rounded bg-success/20">{'<'} 1M RWF</span>
                <span className="ml-2 px-2 py-0.5 rounded bg-warning/20">1M-5M RWF</span>
                <span className="ml-2 px-2 py-0.5 rounded bg-accent-500/20">{'>'} 5M RWF</span>
              </span>
            </div>
            <GISMap
              parcels={parcels}
              height="600px"
              onParcelClick={handleParcelClick}
            />
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  );
}
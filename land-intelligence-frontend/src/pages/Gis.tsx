// GIS Map Page
// Land Intelligence System

import React, { useState, useEffect } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { GISMap } from '@/components/ui/GISMap';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { RefreshCw, Layers, MapPin, User, Ruler, DollarSign, FileText, Calendar } from 'lucide-react';
import { landService } from '@/services/landService';
import type { Parcel } from '@/types/land';
import { toast } from 'react-hot-toast';

import { parseWkbToCoordinates } from '@/utils/wkbParser';

interface ParcelGeoData {
  id: string;
  upi: string;
  owner_name: string;
  area_sqm: number;
  geometry: [number, number][][]; // Array of polygon rings
  valuation?: number;
  title_deed_number?: string | null;
  location_description?: string | null;
  valuation_date?: string | null;
  parish_name?: string | null;
  land_use_category_name?: string | null;
}

export default function GisPage() {
  const [parcels, setParcels] = useState<ParcelGeoData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedParcel, setSelectedParcel] = useState<ParcelGeoData | null>(null);

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
          upi: parcel.upi,
          owner_name: parcel.owner_name,
          area_sqm: parcel.area_sqm,
          valuation: parcel.valuation ?? undefined,
          title_deed_number: parcel.title_deed_number,
          location_description: parcel.location_description,
          valuation_date: parcel.valuation_date,
          parish_name: parcel.parish_name,
          land_use_category_name: parcel.land_use_category_name,
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
    setSelectedParcel(parcel);
  };

  const closeModal = () => {
    setSelectedParcel(null);
  };

  const formatNumber = (value: number | undefined) => {
    if (value === undefined) return 'N/A';
    return new Intl.NumberFormat('rw-RW').format(value);
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
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
              Click on a parcel to view details. Color-coded by valuation tiers.
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

      {/* Parcel Details Modal */}
      <Modal
        isOpen={!!selectedParcel}
        onClose={closeModal}
        title="Parcel Details"
        size="lg"
        footer={<Button variant="secondary" onClick={closeModal}>Close</Button>}
      >
        {selectedParcel && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-slate-400 mt-0.5" />
                <div>
                  <p className="text-xs text-slate-500">Parcel Number</p>
                  <p className="font-medium text-white">{selectedParcel.upi}</p>
                </div>
              </div>

              {selectedParcel.title_deed_number && (
                <div className="flex items-start gap-3">
                  <FileText className="w-5 h-5 text-slate-400 mt-0.5" />
                  <div>
                    <p className="text-xs text-slate-500">Title Deed Number</p>
                    <p className="font-medium text-white">{selectedParcel.title_deed_number}</p>
                  </div>
                </div>
              )}

              <div className="flex items-start gap-3">
                <User className="w-5 h-5 text-slate-400 mt-0.5" />
                <div>
                  <p className="text-xs text-slate-500">Owner</p>
                  <p className="font-medium text-white">{selectedParcel.owner_name}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Ruler className="w-5 h-5 text-slate-400 mt-0.5" />
                <div>
                  <p className="text-xs text-slate-500">Area (sqm)</p>
                  <p className="font-medium text-white">{formatNumber(selectedParcel.area_sqm)}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <DollarSign className="w-5 h-5 text-slate-400 mt-0.5" />
                <div>
                  <p className="text-xs text-slate-500">Valuation</p>
                  <p className="font-medium text-white">
                    {selectedParcel.valuation ? `${formatNumber(selectedParcel.valuation)} RWF` : 'Not Valued'}
                  </p>
                </div>
              </div>

              {selectedParcel.valuation_date && (
                <div className="flex items-start gap-3">
                  <Calendar className="w-5 h-5 text-slate-400 mt-0.5" />
                  <div>
                    <p className="text-xs text-slate-500">Valuation Date</p>
                    <p className="font-medium text-white">{formatDate(selectedParcel.valuation_date)}</p>
                  </div>
                </div>
              )}
            </div>

            {selectedParcel.parish_name && (
              <div>
                <p className="text-xs text-slate-500">Parish</p>
                <p className="font-medium text-white">{selectedParcel.parish_name}</p>
              </div>
            )}

            {selectedParcel.land_use_category_name && (
              <div>
                <p className="text-xs text-slate-500">Land Use Category</p>
                <p className="font-medium text-white">{selectedParcel.land_use_category_name}</p>
              </div>
            )}

            {selectedParcel.location_description && (
              <div>
                <p className="text-xs text-slate-500">Location Description</p>
                <p className="font-medium text-white">{selectedParcel.location_description}</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </PageContainer>
  );
}
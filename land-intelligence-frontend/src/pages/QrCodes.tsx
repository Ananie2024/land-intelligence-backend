import React, { useState, useCallback } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { QrCode, Search, MapPin } from 'lucide-react';
import { QrGenerator } from '@/features/qr/components/QrGenerator';
import { QrVerifier } from '@/features/qr/components/QrVerifier';
import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';

export default function QrCodes() {
  const [parcelId, setParcelId] = useState('');
  const [parcelSearch, setParcelSearch] = useState('');
  const [parcelSuggestions, setParcelSuggestions] = useState<{ id: string; upi: string }[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const searchParcels = useCallback(async (query: string) => {
    if (!query || query.length < 2) {
      setParcelSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    try {
      const response = await apiClient.get<{ items: { id: string; upi: string }[] }>(ENDPOINTS.PARCELS.BASE, {
        search: query,
        size: 10,
      });
      if (response.success && response.data) {
        setParcelSuggestions(response.data.items);
        setShowSuggestions(true);
      }
    } catch {
      setParcelSuggestions([]);
    }
  }, []);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setParcelSearch(value);
    searchParcels(value);
  };

  const selectParcel = (id: string, upi: string) => {
    setParcelId(upi);
    setParcelSearch(upi);
    setShowSuggestions(false);
  };

  return (
    <PageContainer
      title="QR Codes Generation"
      subtitle="Generate secure verification QR codes for land registry deeds."
    >
      <div className="flex items-center gap-3 p-6 rounded-xl border border-slate-800/80 bg-slate-900/30 mb-6">
        <QrCode className="w-6 h-6 text-accent-400" />
        <div className="text-sm flex-1">
          <p className="text-white font-bold">QR Verification Generator</p>
          <p className="text-slate-400 mt-1">Search for a parcel to generate a verified QR code linking directly to the cloud-stored deeds database.</p>
        </div>
      </div>

      <div className="bg-slate-900/40 p-6 rounded-lg border border-slate-800 mb-6">
        <label htmlFor="parcel-search" className="block text-sm font-medium text-slate-300 mb-2">
          Search Parcel
        </label>
        <div className="relative">
          <input
            type="text"
            id="parcel-search"
            placeholder="Search parcels by UPI or number..."
            value={parcelSearch}
            onChange={handleSearchChange}
            className="w-full pl-9 pr-3 py-2 bg-slate-900/60 border border-slate-700 rounded-md text-sm text-white placeholder-slate-500 focus:outline-none focus:border-primary-500 mb-4"
          />
          <Search className="absolute left-3 top-2 w-4 h-4 text-slate-500" />
          {showSuggestions && parcelSuggestions.length > 0 && (
            <div className="absolute top-full mt-1 w-full bg-slate-800 border border-slate-700 rounded-md shadow-lg z-10 max-h-48 overflow-auto">
              {parcelSuggestions.map((parcel) => (
                <button
                  key={parcel.id}
                  onClick={() => selectParcel(parcel.id, parcel.upi)}
                  className="w-full text-left px-3 py-2 text-sm text-slate-200 hover:bg-slate-700 transition-colors flex items-center gap-2"
                >
                  <MapPin className="w-3 h-3 text-slate-400" />
                  {parcel.upi}
                </button>
              ))}
            </div>
          )}
        </div>
        {parcelId && <QrGenerator parcelId={parcelId} />}
      </div>

      <QrVerifier />
    </PageContainer>
  );
}

// GIS Map Component
// Land Intelligence System

import React, { useEffect, useMemo, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import { MapContainer, TileLayer, Polygon, Popup } from 'react-leaflet';
// eslint-disable-next-line @typescript-eslint/no-explicit-any
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Leaflet with bundlers
// eslint-disable-next-line @typescript-eslint/no-explicit-any
delete ((L.Icon as any).Default.prototype as any)._getIconUrl;
(L.Icon as any).Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface ParcelGeoData {
  id: string;
  parcel_number: string;
  owner_name: string;
  area_sqm: number;
  geometry: [number, number][][]; // Array of polygon rings
  valuation?: number;
}

interface GISMapProps {
  parcels: ParcelGeoData[];
  height?: string;
  center?: [number, number];
  zoom?: number;
  onParcelClick?: (parcel: ParcelGeoData) => void;
}

// Component to fit map bounds to all parcels
function MapBoundsController({ parcels }: { parcels: ParcelGeoData[] }) {
  const map = useMap();

  useEffect(() => {
    if (parcels.length > 0) {
      const allPoints = parcels.flatMap(p => 
        p.geometry.flatMap(ring => ring.map(coord => [coord[1], coord[0]] as [number, number]))
      );

      if (allPoints.length > 0) {
        const bounds = (L as any).latLngBounds(allPoints);
        map.fitBounds(bounds, { padding: [20, 20] });
      }
    }
  }, [parcels, map]);

  return null;
}

export const GISMap: React.FC<GISMapProps> = ({
  parcels,
  height = '500px',
  center = [-1.9444, 30.0616], // Default: Kigali, Rwanda
  zoom = 12,
  onParcelClick,
}) => {
  const mapStyle = useMemo(() => ({ height, width: '100%' }), [height]);

  const getParcelColor = useCallback((valuation?: number): string => {
    if (!valuation || valuation === 0) return '#64748b';
    if (valuation < 1000000) return '#22c55e';
    if (valuation < 5000000) return '#eab308';
    return '#f97316';
  }, []);

  return (
    <div className="rounded-xl overflow-hidden border border-slate-800/80 bg-slate-900/40">
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      <MapContainer center={center} zoom={zoom} style={mapStyle} scrollWheelZoom={true} {...({} as any)}>
      <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          {...({ attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' } as any)}
        />

        <MapBoundsController parcels={parcels} />

        {parcels.map((parcel) => (
          <React.Fragment key={parcel.id}>
            {parcel.geometry.map((ring, index) => (
              <Polygon
                key={`${parcel.id}-ring-${index}`}
                positions={ring.map(coord => [coord[1], coord[0]] as [number, number])}
                pathOptions={{
                  color: getParcelColor(parcel.valuation),
                  weight: 2,
                  fillColor: getParcelColor(parcel.valuation),
                  fillOpacity: 0.5,
                }}
                eventHandlers={{
                  click: () => onParcelClick?.(parcel),
                }}
              />
            ))}
          </React.Fragment>
        ))}
      </MapContainer>
    </div>
  );
};

export default GISMap;

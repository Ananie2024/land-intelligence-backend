// Parcel Detail Component
// Land Intelligence System

import type { Parcel } from '@/types/land';

interface ParcelDetailProps {
  parcel: Parcel;
}

export const ParcelDetail: React.FC<ParcelDetailProps> = ({ parcel }) => {
  return (
    <div className="space-y-6">
<div>
        <h2 className="text-xl font-bold text-gray-900">UPI: {parcel.upi}</h2>
        <p className="text-sm text-gray-500">Parish: {parcel.parish_name || parcel.parish_id}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h3 className="text-sm font-medium text-gray-700">Area</h3>
          <p className="mt-1 text-gray-900">{parcel.area_sqm.toLocaleString()} m²</p>
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-700">Owner</h3>
          <p className="mt-1 text-gray-900">{parcel.owner_name}</p>
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-700">Title Deed</h3>
          <p className="mt-1 text-gray-900">{parcel.title_deed_number || 'Not registered'}</p>
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-700">Owner Contact</h3>
          <p className="mt-1 text-gray-900">{parcel.owner_contact || '-'}</p>
        </div>
      </div>

      {parcel.location_description && (
        <div>
          <h3 className="text-sm font-medium text-gray-700">Location</h3>
          <p className="mt-1 text-gray-900">{parcel.location_description}</p>
        </div>
      )}

      {parcel.valuation && (
        <div>
          <h3 className="text-sm font-medium text-gray-700">Valuation</h3>
          <p className="mt-1 text-gray-900">${parcel.valuation.toLocaleString()}</p>
          {parcel.valuation_date && (
            <p className="text-sm text-gray-500">
              Valued on {new Date(parcel.valuation_date).toLocaleDateString()}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default ParcelDetail;
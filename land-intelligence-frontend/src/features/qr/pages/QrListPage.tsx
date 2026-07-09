// QR List Page
// Land Intelligence System

import { useState } from 'react';
import { QrGenerator } from '../components/QrGenerator';
import { QrVerifier } from '../components/QrVerifier';

export const QrListPage: React.FC = () => {
  const [parcelId, setParcelId] = useState('');

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-4">QR Code Services</h1>
        <p className="text-gray-500">Generate and verify QR codes for land registry deeds.</p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <label htmlFor="parcel_id" className="block text-sm font-medium text-gray-700 mb-2">
          Parcel ID for QR Generation
        </label>
        <input
          type="text"
          id="parcel_id"
          placeholder="Enter parcel ID..."
          value={parcelId}
          onChange={(e) => setParcelId(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md mb-4"
        />
        {parcelId && <QrGenerator parcelId={parcelId} />}
      </div>

      <QrVerifier />
    </div>
  );
};

export default QrListPage;
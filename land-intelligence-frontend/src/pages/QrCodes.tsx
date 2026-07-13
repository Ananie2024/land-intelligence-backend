import React, { useState } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { QrCode } from 'lucide-react';
import { QrGenerator } from '@/features/qr/components/QrGenerator';
import { QrVerifier } from '@/features/qr/components/QrVerifier';

export default function QrCodes() {
  const [parcelId, setParcelId] = useState('');

  return (
    <PageContainer
      title="QR Codes Generation"
      subtitle="Generate secure verification QR codes for land registry deeds."
    >
      <div className="flex items-center gap-3 p-6 rounded-xl border border-slate-800/80 bg-slate-900/30 mb-6">
        <QrCode className="w-6 h-6 text-accent-400" />
        <div className="text-sm flex-1">
          <p className="text-white font-bold">QR Verification Generator</p>
          <p className="text-slate-400 mt-1">This panel will generate verified QR codes linking directly to the cloud-stored deeds database.</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <label htmlFor="upi" className="block text-sm font-medium text-gray-700 mb-2">
          UPI for QR Generation
        </label>
        <input
          type="text"
          id="upi"
          placeholder="Enter UPI (e.g., 1/02/02/03/1390)..."
          value={parcelId}
          onChange={(e) => setParcelId(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md mb-4"
        />
        {parcelId && <QrGenerator parcelId={parcelId} />}
      </div>

      <QrVerifier />
    </PageContainer>
  );
}
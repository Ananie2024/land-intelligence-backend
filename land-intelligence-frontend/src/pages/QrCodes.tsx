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

      <div className="bg-slate-900/40 p-6 rounded-lg border border-slate-800 mb-6">
        <label htmlFor="upi" className="block text-sm font-medium text-slate-300 mb-2">
          UPI for QR Generation
        </label>
        <input
          type="text"
          id="upi"
          placeholder="Enter UPI (e.g., 1/02/02/03/1390)..."
          value={parcelId}
          onChange={(e) => setParcelId(e.target.value)}
          className="w-full px-3 py-2 bg-slate-900/60 border border-slate-700 rounded-md text-sm text-white placeholder-slate-500 focus:outline-none focus:border-primary-500 mb-4"
        />
        {parcelId && <QrGenerator parcelId={parcelId} />}
      </div>

      <QrVerifier />
    </PageContainer>
  );
}

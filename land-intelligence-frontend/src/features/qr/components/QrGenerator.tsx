// QR Generator Component
// Land Intelligence System

import React, { useState } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { Download } from 'lucide-react';
import type { QrCodeGenerateResponse } from '@/types/qr';
import { qrService } from '@/services/qrService';

interface QrGeneratorProps {
  parcelId: string;
}

// Extended type for QR code generation response
interface QrCodeGenerateResponseExtended extends QrCodeGenerateResponse {
  token: string;
  qr_image_base64?: string;
  expires_at?: string | null;
}

export const QrGenerator: React.FC<QrGeneratorProps> = ({ parcelId }) => {
  const [qrData, setQrData] = useState<QrCodeGenerateResponseExtended | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const generateQr = async () => {
    setIsLoading(true);
    try {
      const response = await qrService.generateQrCode(parcelId);
      if (response.success && response.data) {
        setQrData(response.data as QrCodeGenerateResponseExtended);
      }
    } catch (error) {
      console.error('Failed to generate QR code', error);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadQr = () => {
    if (!qrData?.qr_image_base64) return;
    const link = document.createElement('a');
    link.href = `data:image/svg+xml;base64,${btoa(qrData.qr_image_base64)}`;
    link.download = `qr-${parcelId}.svg`;
    link.click();
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 mb-4">QR Code Generator</h3>
      
      <button
        onClick={generateQr}
        disabled={isLoading}
        className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 mb-4"
      >
        {isLoading ? 'Generating...' : 'Generate QR Code'}
      </button>

      {qrData && (
        <div className="flex items-center gap-4">
          <div className="bg-white p-2 rounded">
            <QRCodeSVG value={qrData.code} size={128} />
          </div>
          <div>
            <p className="text-sm text-gray-500">Expires: {qrData.expires_at ? new Date(qrData.expires_at).toLocaleDateString() : 'N/A'}</p>
            <button
              onClick={downloadQr}
              className="mt-2 flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-800"
            >
              <Download className="h-4 w-4" />
              Download
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default QrGenerator;

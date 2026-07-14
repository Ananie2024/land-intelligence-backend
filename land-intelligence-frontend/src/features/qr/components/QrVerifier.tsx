// QR Verifier Component
// Land Intelligence System

import { useState } from 'react';
import { QrCode, Check, X } from 'lucide-react';
import { qrService } from '@/services/qrService';

export const QrVerifier: React.FC = () => {
  const [token, setToken] = useState('');
  const [result, setResult] = useState<{ valid: boolean; parcelUpi?: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const verify = async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const response = await qrService.verifyQrCode(token);
      if (response.success && response.data) {
        setResult({
          valid: response.data.valid,
          parcelUpi: response.data.parcel_upi ?? undefined,
        });
      }
    } catch (error) {
      setResult({ valid: false });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 mb-4">QR Code Verifier</h3>
      
      <div className="flex items-center gap-2 mb-4">
        <input
          type="text"
          placeholder="Enter QR token..."
          value={token}
          onChange={(e) => setToken(e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md"
        />
        <button
          onClick={verify}
          disabled={isLoading || !token}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {isLoading ? 'Verifying...' : 'Verify'}
        </button>
      </div>

      {result && (
        <div className={`p-4 rounded-lg flex items-center gap-2 ${
          result.valid ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
        }`}>
          {result.valid ? <Check className="h-5 w-5" /> : <X className="h-5 w-5" />}
          <span>
            {result.valid 
              ? `Valid QR Code - Parcel: ${result.parcelUpi}` 
              : 'Invalid QR Code'}
          </span>
        </div>
      )}
    </div>
  );
};

export default QrVerifier;
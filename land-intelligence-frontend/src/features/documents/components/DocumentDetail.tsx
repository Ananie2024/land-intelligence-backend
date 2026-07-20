// Document Detail Component
// Land Intelligence System

import { useState, useEffect } from 'react';
import { FileText, MapPin, Archive, Loader2, QrCode } from 'lucide-react';
import { locationService } from '@/services/locationService';
import { documentQrService } from '@/services/qrService';
import type { Document } from '@/types/document';

interface DocumentDetailProps {
  document: Document;
}

interface PhysicalLocationInfo {
  location_name: string;
  location_code: string;
  cabinet_number?: string;
  row?: string;
  column?: string;
  building?: string;
  floor?: string;
  room?: string;
}

export const DocumentDetail: React.FC<DocumentDetailProps> = ({ document }) => {
  const [physicalLocation, setPhysicalLocation] = useState<PhysicalLocationInfo | null>(null);
  const [loadingLocation, setLoadingLocation] = useState(false);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [qrCode, setQrCode] = useState<string | null>(null);
  const [loadingQr, setLoadingQr] = useState(false);
  const [qrError, setQrError] = useState<string | null>(null);

  useEffect(() => {
    if (!document.parcel_upi && !document.id) return;

    const lookupPhysicalLocation = async () => {
      setLoadingLocation(true);
      setLocationError(null);
      try {
        const res = await locationService.findDocument({
          document_id: document.id,
          parcel_id: document.parcel_upi || undefined,
        });
        if (res.success && res.data) {
          setPhysicalLocation(res.data as PhysicalLocationInfo);
        } else {
          setPhysicalLocation(null);
        }
      } catch (error) {
        console.error('Failed to lookup physical location:', error);
        setLocationError('Location lookup unavailable');
        setPhysicalLocation(null);
      } finally {
        setLoadingLocation(false);
      }
    };

    lookupPhysicalLocation();

    // Load existing QR code for this document
    const loadQrCode = async () => {
      setLoadingQr(true);
      setQrError(null);
      try {
        const res = await documentQrService.getQrCode(document.id);
        if (res.success && res.data) {
          setQrCode(res.data.code);
        }
      } catch (error) {
        // QR code might not exist, which is normal
        setQrCode(null);
      } finally {
        setLoadingQr(false);
      }
    };

    loadQrCode();
  }, [document.id, document.parcel_upi]);

  const generateQrCode = async () => {
    setLoadingQr(true);
    setQrError(null);
    try {
      const res = await documentQrService.generateQrCode(document.id);
      if (res.success && res.data) {
        setQrCode(res.data.code);
      } else {
        setQrError(res.message || 'Failed to generate QR code');
      }
    } catch (error) {
      console.error('Failed to generate QR code:', error);
      setQrError('Failed to generate QR code');
    } finally {
      setLoadingQr(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-3">
        <FileText className="h-8 w-8 text-gray-400" />
        <div>
          <h2 className="text-xl font-bold text-gray-900">{document.filename}</h2>
          <p className="text-sm text-gray-500">{document.document_type_name}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h3 className="text-sm font-medium text-gray-700">File Size</h3>
          <p className="mt-1 text-gray-900">{formatFileSize(document.file_size_bytes)}</p>
        </div>
        <div>
          <h3 className="text-sm font-medium text-gray-700">MIME Type</h3>
          <p className="mt-1 text-gray-900">{document.mime_type}</p>
        </div>
        {document.document_date && (
          <div>
            <h3 className="text-sm font-medium text-gray-700">Document Date</h3>
            <p className="mt-1 text-gray-900">
              {new Date(document.document_date).toLocaleDateString()}
            </p>
          </div>
        )}
        {document.reference_number && (
          <div>
            <h3 className="text-sm font-medium text-gray-700">Reference Number</h3>
            <p className="mt-1 text-gray-900">{document.reference_number}</p>
          </div>
        )}
      </div>

      {document.parcel_upi && (
        <div className="flex items-center gap-2">
          <MapPin className="h-4 w-4 text-gray-400" />
          <span className="text-sm text-gray-500">Parcel: </span>
          <span className="text-sm font-medium text-gray-900">{document.parcel_upi}</span>
        </div>
      )}

      {document.description && (
        <div>
          <h3 className="text-sm font-medium text-gray-700">Description</h3>
          <p className="mt-1 text-gray-900">{document.description}</p>
        </div>
      )}

      <div>
        <h3 className="text-sm font-medium text-gray-700">Checksum</h3>
        <p className="mt-1 text-gray-900 font-mono text-xs">{document.checksum}</p>
      </div>

      {/* Physical Archive Location Section */}
      <div className="border-t border-gray-200 pt-4">
        <h3 className="text-sm font-medium text-gray-700 flex items-center gap-2 mb-3">
          <Archive className="h-4 w-4 text-gray-400" />
          Physical Archive Location
        </h3>
        {loadingLocation ? (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Loader2 className="h-4 w-4 animate-spin" />
            Looking up physical location...
          </div>
        ) : locationError ? (
          <p className="text-sm text-amber-600">{locationError}</p>
        ) : physicalLocation ? (
          <div className="bg-gray-50 rounded-md p-3 space-y-1">
            <p className="text-sm text-gray-900 font-medium">{physicalLocation.location_name}</p>
            <p className="text-xs text-gray-500">Code: {physicalLocation.location_code}</p>
            {physicalLocation.building && (
              <p className="text-xs text-gray-500">Building: {physicalLocation.building}</p>
            )}
            {physicalLocation.floor && (
              <p className="text-xs text-gray-500">Floor: {physicalLocation.floor}</p>
            )}
            {physicalLocation.room && (
              <p className="text-xs text-gray-500">Room: {physicalLocation.room}</p>
            )}
            {physicalLocation.cabinet_number && (
              <p className="text-xs text-gray-500">Cabinet: {physicalLocation.cabinet_number}</p>
            )}
            {physicalLocation.row && physicalLocation.column && (
              <p className="text-xs text-gray-500">Grid: Row {physicalLocation.row}, Column {physicalLocation.column}</p>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-400 italic">No physical location assigned</p>
        )}
      </div>

      {/* QR Code Section */}
      <div className="border-t border-gray-200 pt-4">
        <h3 className="text-sm font-medium text-gray-700 flex items-center gap-2 mb-3">
          <QrCode className="h-4 w-4 text-gray-400" />
          Document QR Code
        </h3>
        {loadingQr ? (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading QR code...
          </div>
        ) : qrCode ? (
          <div className="flex items-center gap-4">
            <div className="bg-white p-2 rounded border">
              {/* QR code would be displayed here - using text representation for now */}
              <QrCode className="h-12 w-12 text-gray-400" />
            </div>
            <div>
              <p className="text-xs text-gray-500 font-mono">{qrCode.substring(0, 30)}...</p>
              <p className="text-xs text-green-600 mt-1">QR code generated</p>
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <button
              onClick={generateQrCode}
              disabled={loadingQr}
              className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-1"
            >
              <QrCode className="h-4 w-4" />
              Generate QR Code
            </button>
            {qrError && (
              <p className="text-sm text-red-500">{qrError}</p>
            )}
          </div>
        )}
      </div>

      <div className="flex items-center gap-4 pt-4">
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          document.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
        }`}>
          {document.is_active ? 'Active' : 'Archived'}
        </span>
        {document.page_count && (
          <span className="text-sm text-gray-500">{document.page_count} pages</span>
        )}
      </div>
    </div>
  );
};

export default DocumentDetail;

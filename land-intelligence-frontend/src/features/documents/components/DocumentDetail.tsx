// Document Detail Component
// Land Intelligence System

import { FileText, MapPin } from 'lucide-react';
import type { Document } from '@/types/document';

interface DocumentDetailProps {
  document: Document;
}

export const DocumentDetail: React.FC<DocumentDetailProps> = ({ document }) => {
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

      {document.parcel_number && (
        <div className="flex items-center gap-2">
          <MapPin className="h-4 w-4 text-gray-400" />
          <span className="text-sm text-gray-500">Parcel: </span>
          <span className="text-sm font-medium text-gray-900">{document.parcel_number}</span>
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
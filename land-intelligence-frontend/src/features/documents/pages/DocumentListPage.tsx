// Document List Page
// Land Intelligence System

import { useState, useEffect } from 'react';
import { landService } from '@/services/landService';
import { documentService } from '@/services/documentService';
import type { Document } from '@/types/document';
import type { Parcel } from '@/types/land';
import { DocumentTable } from '../components/DocumentTable';
import { DocumentForm } from '../components/DocumentForm';

export const DocumentListPage: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [parcels, setParcels] = useState<Parcel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  const loadData = async () => {
    setIsLoading(true);
    try {
const [docsResponse, parcelsResponse] = await Promise.all([
        documentService.getDocuments(),
        landService.getParcels(),
      ]);
      
      if (docsResponse.success && docsResponse.data) {
        setDocuments(docsResponse.data);
      }
      if (parcelsResponse.success && parcelsResponse.data) {
        setParcels(parcelsResponse.data);
      }
    } catch (error) {
      console.error('Failed to load data', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDownload = async (document: Document) => {
    // Implementation for downloading documents
    console.log('Download document:', document.filename);
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
        <button 
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Upload Document
        </button>
      </div>
      
      {isLoading ? (
        <div className="text-center py-12">Loading documents...</div>
      ) : (
        <DocumentTable 
          documents={documents}
          onView={(doc) => console.log('View', doc)}
          onEdit={(doc) => console.log('Edit', doc)}
          onDelete={(doc) => console.log('Delete', doc)}
          onDownload={handleDownload}
        />
      )}

      {/* Modal Form */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full">
            <h2 className="text-lg font-bold mb-4">Upload Document</h2>
            <DocumentForm
              onSubmit={async (data) => {
                console.log('Upload:', data);
                setShowForm(false);
                loadData();
              }}
              parcels={parcels.map(p => ({ id: p.id, parcel_number: p.parcel_number }))}
            />
            <button
              onClick={() => setShowForm(false)}
              className="mt-4 px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentListPage;
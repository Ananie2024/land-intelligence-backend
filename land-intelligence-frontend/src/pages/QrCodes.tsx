import React, { useState, useCallback, useEffect } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { QrCode, Search, MapPin, FileText, ChevronDown } from 'lucide-react';
import { QrGenerator } from '@/features/qr/components/QrGenerator';
import { QrVerifier } from '@/features/qr/components/QrVerifier';
import { apiClient } from '@/api/apiClient';
import { documentService } from '@/services/documentService';
import { ENDPOINTS } from '@/api/endpoints';
import { DOCUMENT_TYPE_LABELS } from '@/types/document';
import { DOCUMENT_TYPES } from '@/utils/constants';
import type { Document } from '@/types/document';

export default function QrCodes() {
  const [activeTab, setActiveTab] = useState<'parcel' | 'document'>('parcel');
  const [parcelSearch, setParcelSearch] = useState('');
  const [parcelSuggestions, setParcelSuggestions] = useState<{ id: string; upi: string }[]>([]);
  const [showParcelSuggestions, setShowParcelSuggestions] = useState(false);
  
  const [selectedDocType, setSelectedDocType] = useState<string>(DOCUMENT_TYPES.LAND_TITLES);
  const [documentSuggestions, setDocumentSuggestions] = useState<Document[]>([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);

  // Search parcels for QR generation
  const searchParcels = useCallback(async (query: string) => {
    if (!query || query.length < 2) {
      setParcelSuggestions([]);
      setShowParcelSuggestions(false);
      return;
    }
    try {
      const response = await apiClient.get<{ items: { id: string; upi: string }[] }>(ENDPOINTS.PARCELS.BASE, {
        search: query,
        size: 10,
      });
      if (response.success && response.data) {
        setParcelSuggestions(response.data.items);
        setShowParcelSuggestions(true);
      }
    } catch {
      setParcelSuggestions([]);
    }
  }, []);

  const handleParcelSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setParcelSearch(value);
    searchParcels(value);
  };

  const selectParcel = (id: string, upi: string) => {
    setParcelSearch(upi);
    setShowParcelSuggestions(false);
  };

  // Load all documents of a specific type for dropdown
  const loadDocumentsByType = useCallback(async (docTypeCode: string) => {
    try {
      const response = await documentService.getDocumentsByType(docTypeCode);
      if (response.success && response.data) {
        setDocumentSuggestions(response.data);
      }
    } catch {
      setDocumentSuggestions([]);
    }
  }, []);

  const handleDocTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setSelectedDocType(value);
    setSelectedDocumentId(null);
    loadDocumentsByType(value);
  };

  const selectDocument = (id: string) => {
    setSelectedDocumentId(id);
  };

  // Load documents when document tab is active or type changes
  useEffect(() => {
    if (activeTab === 'document') {
      loadDocumentsByType(selectedDocType);
    }
  }, [activeTab, selectedDocType, loadDocumentsByType]);

  return (
    <PageContainer
      title="QR Codes Generation"
      subtitle="Generate secure verification QR codes for parcels and documents."
    >
      <div className="flex items-center gap-3 p-6 rounded-xl border border-slate-800/80 bg-slate-900/30 mb-6">
        <QrCode className="w-6 h-6 text-accent-400" />
        <div className="text-sm flex-1">
          <p className="text-white font-bold">QR Verification Generator</p>
          <p className="text-slate-400 mt-1">
            Generate QR codes for parcels to view all documents, or for individual documents to verify integrity.
          </p>
        </div>
      </div>

      {/* Tabs for Parcel vs Document */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setActiveTab('parcel')}
          className={`px-4 py-2 text-sm rounded-md flex items-center gap-2 ${
            activeTab === 'parcel'
              ? 'bg-primary-600 text-white'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          }`}
        >
          <MapPin className="w-4 h-4" />
          Parcel QR
        </button>
        <button
          onClick={() => setActiveTab('document')}
          className={`px-4 py-2 text-sm rounded-md flex items-center gap-2 ${
            activeTab === 'document'
              ? 'bg-primary-600 text-white'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          }`}
        >
          <FileText className="w-4 h-4" />
          Document QR
        </button>
      </div>

      {/* Parcel Search Section */}
      {activeTab === 'parcel' && (
        <div className="bg-slate-900/40 p-6 rounded-lg border border-slate-800 mb-6">
          <label htmlFor="parcel-search" className="block text-sm font-medium text-slate-300 mb-2">
            Search Parcel
          </label>
          <div className="relative">
            <input
              type="text"
              id="parcel-search"
              placeholder="Search parcels by UPI or number..."
              value={parcelSearch}
              onChange={handleParcelSearchChange}
              className="w-full pl-9 pr-3 py-2 bg-slate-900/60 border border-slate-700 rounded-md text-sm text-white placeholder-slate-500 focus:outline-none focus:border-primary-500 mb-4"
            />
            <Search className="absolute left-3 top-2 w-4 h-4 text-slate-500" />
            {showParcelSuggestions && parcelSuggestions.length > 0 && (
              <div className="absolute top-full mt-1 w-full bg-slate-800 border border-slate-700 rounded-md shadow-lg z-10 max-h-48 overflow-auto">
                {parcelSuggestions.map((parcel) => (
                  <button
                    key={parcel.id}
                    onClick={() => selectParcel(parcel.id, parcel.upi)}
                    className="w-full text-left px-3 py-2 text-sm text-slate-200 hover:bg-slate-700 transition-colors flex items-center gap-2"
                  >
                    <MapPin className="w-3 h-3 text-slate-400" />
                    {parcel.upi}
                  </button>
                ))}
              </div>
            )}
          </div>
          {parcelSearch && <QrGenerator parcelId={parcelSearch} />}
        </div>
      )}

      {/* Document Search Section */}
      {activeTab === 'document' && (
        <div className="bg-slate-900/40 p-6 rounded-lg border border-slate-800 mb-6">
          <div className="space-y-4">
            {/* Document Type Dropdown */}
            <div>
              <label htmlFor="doc-type-select" className="block text-sm font-medium text-slate-300 mb-2">
                Document Type
              </label>
              <div className="relative">
                <select
                  id="doc-type-select"
                  value={selectedDocType}
                  onChange={handleDocTypeChange}
                  className="w-full px-3 py-2 bg-slate-900/60 border border-slate-700 rounded-md text-sm text-white focus:outline-none focus:border-primary-500 appearance-none"
                >
                  {(Object.entries(DOCUMENT_TYPE_LABELS) as [string, string][]).map(([code, name]) => (
                    <option key={code} value={code} className="bg-slate-800">
                      {name}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-2 w-4 h-4 text-slate-500 pointer-events-none" />
              </div>
            </div>

            {/* Document Dropdown */}
            <div>
              <label htmlFor="document-select" className="block text-sm font-medium text-slate-300 mb-2">
                Select Document
              </label>
              <div className="relative">
                <select
                  id="document-select"
                  value={selectedDocumentId || ''}
                  onChange={(e) => selectDocument(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900/60 border border-slate-700 rounded-md text-sm text-white focus:outline-none focus:border-primary-500 appearance-none"
                >
                  <option value="" className="bg-slate-800">
                    Choose a document...
                  </option>
                  {documentSuggestions.map((doc) => (
                    <option key={doc.id} value={doc.id} className="bg-slate-800">
                      {doc.filename}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-2 w-4 h-4 text-slate-500 pointer-events-none" />
              </div>
            </div>

            {/* Generate Button */}
            {selectedDocumentId && (
              <div className="mt-4">
                <p className="text-sm text-green-400 mb-2">Document selected for QR generation</p>
                <button
                  onClick={async () => {
                    const res = await apiClient.post<{ code: string }>(ENDPOINTS.DOCUMENT_QR.GENERATE(selectedDocumentId));
                    if (res.success && res.data) {
                      alert(`QR Code Generated: ${res.data.code}`);
                    }
                  }}
                  className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                >
                  Generate QR Code
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      <QrVerifier />
    </PageContainer>
  );
}

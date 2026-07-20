// Document List Page with Full CRUD
// Land Intelligence System

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ListState } from '@/components/ui/ListState';
import { FileText, Upload, Archive, MapPin } from 'lucide-react';
import { landService } from '@/services/landService';
import { documentService } from '@/services/documentService';
import { locationService } from '@/services/locationService';
import type { Document, DocumentCreate, DocumentType } from '@/types/document';
import type { Parcel } from '@/types/land';
import { DOCUMENT_TYPE_LABELS } from '@/types/document';
import { DOCUMENT_TYPES } from '@/utils/constants';
import { DocumentTable } from '@/features/documents/components/DocumentTable';
import { DocumentForm } from '@/features/documents/components/DocumentForm';
import { Modal } from '@/components/ui/Modal';
import { Pagination } from '@/components/ui/Pagination';
import { useResourceList, useResourceMutation, useResourceQuery } from '@/hooks/useResourceList';
import toast from 'react-hot-toast';

interface PhysicalLocationResult {
  location_name?: string;
  location_code?: string;
  cabinet_number?: string;
  row?: string;
  column?: string;
  building?: string;
  floor?: string;
  room?: string;
  message?: string;
}

// Static document types for the dropdown (should match backend DocumentType enum)
const STATIC_DOCUMENT_TYPES: DocumentType[] = [
  { id: DOCUMENT_TYPES.LAND_TITLES, name: DOCUMENT_TYPE_LABELS.land_titles, code: DOCUMENT_TYPES.LAND_TITLES, document_count: 0 },
  { id: DOCUMENT_TYPES.LAND_DEEDS, name: DOCUMENT_TYPE_LABELS.land_deeds, code: DOCUMENT_TYPES.LAND_DEEDS, document_count: 0 },
  { id: DOCUMENT_TYPES.LETTERS, name: DOCUMENT_TYPE_LABELS.letters, code: DOCUMENT_TYPES.LETTERS, document_count: 0 },
  { id: DOCUMENT_TYPES.LAND_LEASES, name: DOCUMENT_TYPE_LABELS.land_leases, code: DOCUMENT_TYPES.LAND_LEASES, document_count: 0 },
  { id: DOCUMENT_TYPES.REPORTS, name: DOCUMENT_TYPE_LABELS.reports, code: DOCUMENT_TYPES.REPORTS, document_count: 0 },
  { id: DOCUMENT_TYPES.SURVEYS, name: DOCUMENT_TYPE_LABELS.surveys, code: DOCUMENT_TYPES.SURVEYS, document_count: 0 },
  { id: DOCUMENT_TYPES.CESSION, name: DOCUMENT_TYPE_LABELS.cession, code: DOCUMENT_TYPES.CESSION, document_count: 0 },
  { id: DOCUMENT_TYPES.OTHERS, name: DOCUMENT_TYPE_LABELS.others, code: DOCUMENT_TYPES.OTHERS, document_count: 0 },
  { id: DOCUMENT_TYPES.UNSPECIFIED, name: DOCUMENT_TYPE_LABELS.unspecified, code: DOCUMENT_TYPES.UNSPECIFIED, document_count: 0 },
];

export default function Documents() {
  const navigate = useNavigate();
  const [showForm, setShowForm] = useState(false);
  const [editingDocument, setEditingDocument] = useState<Document | null>(null);
  const [filters, setFilters] = useState({
    page: 1,
    size: 20,
    search: '',
  });

  // Location tracking state
  const [locatingDoc, setLocatingDoc] = useState<Document | null>(null);
  const [locationResult, setLocationResult] = useState<PhysicalLocationResult | null>(null);
  const [locationLoading, setLocationLoading] = useState(false);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [showLocationModal, setShowLocationModal] = useState(false);

  const { data, isLoading, error, totalItems, totalPages, refetch } = useResourceList<Document>(
    ['documents'],
    (f) => documentService.getDocuments(f),
    filters,
    { defaultFilters: { page: 1, size: 20, search: '' } }
  );

  // Load parcels for form dropdown (all, no pagination)
  const { data: parcels } = useResourceQuery<Parcel[]>(
    ['parcels-all'],
    () => landService.getParcelsAll()
  );

  const createMutation = useResourceMutation(
    (args: { data: DocumentCreate; file: File }) => documentService.uploadDocument(args.file, args.data),
    { invalidateKeys: ['documents'] }
  );

  const updateMutation = useResourceMutation(
    (data: DocumentCreate) => {
      if (!editingDocument) throw new Error('No document selected');
      return documentService.updateDocument(editingDocument.id, data);
    },
    { invalidateKeys: ['documents'] }
  );

  const deleteMutation = useResourceMutation(
    (id: string) => documentService.deleteDocument(id),
    { invalidateKeys: ['documents'] }
  );

  const documents = data || [];

  const handleCreate = async (data: DocumentCreate, file?: File) => {
    if (!file) {
      toast.error('Please select a file to upload');
      return;
    }
    const success = await createMutation.mutate({ data, file });
    if (success) {
      setShowForm(false);
      toast.success('Document uploaded successfully');
    }
  };

  const handleUpdate = async (data: DocumentCreate) => {
    if (!editingDocument) return;
    const success = await updateMutation.mutate(data);
    if (success) {
      setEditingDocument(null);
      setShowForm(false);
      toast.success('Document updated successfully');
    }
  };

  const handleDelete = async (document: Document) => {
    if (!confirm(`Delete document "${document.filename}"? This action cannot be undone.`)) return;
    const success = await deleteMutation.mutate(document.id);
    if (success) {
      toast.success('Document deleted successfully');
    }
  };

  const handleDownload = async (doc: Document) => {
    try {
      const blob = await documentService.downloadDocument(doc.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = doc.filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download document', err);
      toast.error('Failed to download document');
    }
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingDocument(null);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilters(prev => ({ ...prev, search: e.target.value, page: 1 }));
  };

  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }));
  };

  const handlePageSizeChange = (size: number) => {
    setFilters(prev => ({ ...prev, size, page: 1 }));
  };

  // Locate document in physical archive
  const handleLocate = async (doc: Document) => {
    setLocatingDoc(doc);
    setLocationResult(null);
    setLocationError(null);
    setShowLocationModal(true);
    setLocationLoading(true);
    try {
      const res = await locationService.findDocument({
        document_id: doc.id,
        parcel_id: doc.parcel_upi || undefined,
      });
      if (res.success && res.data) {
        setLocationResult(res.data as PhysicalLocationResult);
      } else {
        setLocationResult({ message: res.message || 'No physical location found for this document.' });
      }
    } catch (err) {
      console.error('Failed to locate document:', err);
      setLocationError('Location lookup failed. The service may be unavailable.');
    } finally {
      setLocationLoading(false);
    }
  };

  const handleCloseLocationModal = () => {
    setShowLocationModal(false);
    setLocatingDoc(null);
    setLocationResult(null);
    setLocationError(null);
  };

  const handleRetry = () => {
    refetch();
  };

  const isSubmitting = createMutation.isLoading || updateMutation.isLoading;

  return (
    <PageContainer
      title="Document Archive"
      subtitle="Digital deed registries, land titles, and lease files repository."
      action={
        <Button 
          variant="primary" 
          leftIcon={<Upload className="w-4 h-4" />}
          onClick={() => setShowForm(true)}
        >
          Upload Document
        </Button>
      }
    >
      <div className="space-y-6">
        <div className="flex items-center gap-3 p-6 rounded-xl border border-slate-800/80 bg-slate-900/30">
          <FileText className="w-6 h-6 text-info" />
          <div className="text-sm flex-1">
            <p className="text-white font-bold">Document Archive</p>
            <p className="text-slate-400 mt-1">Scanned papers, PDFs, and official land certificates will be archived and search-indexed here.</p>
          </div>
          <div className="relative">
            <input
              type="text"
              placeholder="Search documents..."
              value={filters.search || ''}
              onChange={handleSearchChange}
              className="pl-9 pr-3 py-2 w-64 bg-slate-900/60 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-primary-500"
            />
            <svg className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>

        <ListState 
          isLoading={isLoading} 
          error={error} 
          onRetry={handleRetry} 
          label="documents"
        >
          <DocumentTable 
            documents={documents}
            onView={(doc) => navigate(`/documents/${doc.id}`)}
            onEdit={(doc) => {
              setEditingDocument(doc);
              setShowForm(true);
            }}
            onDelete={handleDelete}
            onDownload={handleDownload}
            onLocate={handleLocate}
          />
          {totalPages > 1 && (
            <Pagination
              currentPage={filters.page || 1}
              totalPages={totalPages}
              totalItems={totalItems}
              pageSize={filters.size || 20}
              onPageChange={handlePageChange}
              onPageSizeChange={handlePageSizeChange}
            />
          )}
        </ListState>

        {/* Modal Form */}
        <Modal
          isOpen={showForm}
          onClose={handleCloseForm}
          title={editingDocument ? 'Edit Document' : 'Upload Document'}
          size="lg"
        >
          <DocumentForm
            document={editingDocument}
            onSubmit={editingDocument ? handleUpdate : handleCreate}
            isLoading={isSubmitting}
            parcels={(parcels || []).map(p => ({ id: p.id, upi: p.upi }))}
            documentTypes={STATIC_DOCUMENT_TYPES}
          />
        </Modal>

        {/* Physical Location Result Modal */}
        <Modal
          isOpen={showLocationModal}
          onClose={handleCloseLocationModal}
          title={locatingDoc ? `Archive Location: ${locatingDoc.filename}` : 'Physical Archive Location'}
          size="md"
        >
          {locationLoading ? (
            <div className="flex items-center justify-center gap-3 py-8 text-slate-400">
              <LoadingSpinner size="sm" className="border-t-primary-500" />
              <span>Looking up physical archive location...</span>
            </div>
          ) : locationError ? (
            <div className="py-4">
              <div className="flex items-center gap-2 text-amber-500 mb-2">
                <Archive className="h-5 w-5" />
                <span className="font-medium">Location Unavailable</span>
              </div>
              <p className="text-sm text-slate-400">{locationError}</p>
            </div>
          ) : locationResult ? (
            locationResult.location_name ? (
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-accent-400">
                  <MapPin className="h-5 w-5" />
                  <span className="font-medium text-white">Found in Archive</span>
                </div>
                <div className="bg-slate-900/60 rounded-lg p-4 space-y-2">
                  <p className="text-sm text-white font-medium">{locationResult.location_name}</p>
                  <p className="text-xs text-slate-400">Code: {locationResult.location_code}</p>
                  {locationResult.building && (
                    <p className="text-xs text-slate-400">Building: {locationResult.building}</p>
                  )}
                  {locationResult.floor && (
                    <p className="text-xs text-slate-400">Floor: {locationResult.floor}</p>
                  )}
                  {locationResult.room && (
                    <p className="text-xs text-slate-400">Room: {locationResult.room}</p>
                  )}
                  {locationResult.cabinet_number && (
                    <p className="text-xs text-slate-400">Cabinet: {locationResult.cabinet_number}</p>
                  )}
                  {locationResult.row && locationResult.column && (
                    <p className="text-xs text-slate-400">
                      Grid Position: Row {locationResult.row}, Column {locationResult.column}
                    </p>
                  )}
                </div>
              </div>
            ) : (
              <div className="py-4">
                <div className="flex items-center gap-2 text-slate-400 mb-2">
                  <Archive className="h-5 w-5" />
                  <span className="font-medium text-white">No Location Found</span>
                </div>
                <p className="text-sm text-slate-500">{locationResult.message || 'This document has no physical archive location assigned.'}</p>
              </div>
            )
          ) : null}
        </Modal>
      </div>
    </PageContainer>
  );
}
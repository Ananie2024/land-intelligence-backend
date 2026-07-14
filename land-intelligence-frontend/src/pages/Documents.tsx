// Document List Page with Full CRUD
// Land Intelligence System

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/ui/Button';
import { FileText, Upload } from 'lucide-react';
import { landService } from '@/services/landService';
import { documentService } from '@/services/documentService';
import type { Document, DocumentCreate, DocumentFilters } from '@/types/document';
import type { Parcel } from '@/types/land';
import { DocumentTable } from '@/features/documents/components/DocumentTable';
import { DocumentForm } from '@/features/documents/components/DocumentForm';
import { Modal } from '@/components/ui/Modal';
import { Pagination } from '@/components/ui/Pagination';
import { toast } from 'react-hot-toast';

export default function Documents() {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [parcels, setParcels] = useState<Parcel[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingDocument, setEditingDocument] = useState<Document | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [filters, setFilters] = useState<DocumentFilters & { search?: string }>({
    page: 1,
    size: 20,
    search: '',
  });
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [docsResponse, parcelsResponse] = await Promise.all([
        documentService.getDocuments(filters),
        landService.getParcels(),
      ]);
      
      if (docsResponse.success && docsResponse.data) {
        setDocuments(docsResponse.data);
        setTotalItems(docsResponse.total ?? 0);
        setTotalPages(docsResponse.pages ?? 0);
      } else {
        setError(docsResponse.message || 'Failed to load documents');
      }
      if (parcelsResponse.success && parcelsResponse.data) {
        setParcels(parcelsResponse.data);
      }
    } catch (error) {
      console.error('Failed to load data', error);
      setError('Failed to load documents');
      toast.error('Failed to load documents');
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleCreate = async (data: DocumentCreate, file?: File) => {
    setIsSubmitting(true);
    try {
      if (!file) {
        toast.error('Please select a file to upload');
        return;
      }
      const response = await documentService.uploadDocument(file, data);
      if (response.success) {
        setShowForm(false);
        toast.success('Document uploaded successfully');
        loadData();
      }
    } catch (error) {
      console.error('Failed to upload document', error);
      toast.error('Failed to upload document');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdate = async (data: DocumentCreate) => {
    if (!editingDocument) return;
    setIsSubmitting(true);
    try {
      const response = await documentService.updateDocument(editingDocument.id, data);
      if (response.success) {
        setEditingDocument(null);
        setShowForm(false);
        toast.success('Document updated successfully');
        loadData();
      }
    } catch (error) {
      console.error('Failed to update document', error);
      toast.error('Failed to update document');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (document: Document) => {
    if (!confirm(`Delete document "${document.filename}"? This action cannot be undone.`)) return;
    try {
      const response = await documentService.deleteDocument(document.id);
      if (response.success) {
        toast.success('Document deleted successfully');
        loadData();
      }
    } catch (error) {
      console.error('Failed to delete document', error);
      toast.error('Failed to delete document');
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
    } catch (error) {
      console.error('Failed to download document', error);
      toast.error('Failed to download document');
    }
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingDocument(null);
  };

  // Handle search input change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilters(prev => ({ ...prev, search: e.target.value, page: 1 }));
  };

  // Handle page change
  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }));
  };

  // Handle page size change
  const handlePageSizeChange = (size: number) => {
    setFilters(prev => ({ ...prev, size, page: 1 }));
  };

  // Retry function
  const handleRetry = () => {
    loadData();
  };

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

        {isLoading ? (
          <div className="text-center py-12 text-slate-400">Loading documents...</div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-400 mb-4">{error}</p>
            <button 
              onClick={handleRetry}
              className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : (
          <>
            <DocumentTable 
              documents={documents}
              onView={(doc) => navigate(`/documents/${doc.id}`)}
              onEdit={(doc) => {
                setEditingDocument(doc);
                setShowForm(true);
              }}
              onDelete={handleDelete}
              onDownload={handleDownload}
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
          </>
        )}

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
            parcels={parcels.map(p => ({ id: p.id, upi: p.upi }))}
            documentTypes={[
              { id: '1', name: 'Deed' },
              { id: '2', name: 'Title' },
              { id: '3', name: 'Lease' },
              { id: '4', name: 'Survey' },
            ]}
          />
        </Modal>
      </div>
    </PageContainer>
  );
}

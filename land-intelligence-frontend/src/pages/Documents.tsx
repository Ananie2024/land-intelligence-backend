// Document List Page with Full CRUD
// Land Intelligence System

import { useState, useEffect } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { Button } from '@/components/ui/Button';
import { FileText, Upload, Download } from 'lucide-react';
import { landService } from '@/services/landService';
import { documentService } from '@/services/documentService';
import type { Document, DocumentCreate } from '@/types/document';
import type { Parcel } from '@/types/land';
import { DocumentTable } from '@/features/documents/components/DocumentTable';
import { DocumentForm } from '@/features/documents/components/DocumentForm';
import { Modal } from '@/components/ui/Modal';
import { toast } from 'react-hot-toast';

export default function Documents() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [parcels, setParcels] = useState<Parcel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingDocument, setEditingDocument] = useState<Document | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

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
      toast.error('Failed to load documents');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

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
          <div className="text-sm">
            <p className="text-white font-bold">Document Archive</p>
            <p className="text-slate-400 mt-1">Scanned papers, PDFs, and official land certificates will be archived and search-indexed here.</p>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-12 text-slate-400">Loading documents...</div>
        ) : (
          <DocumentTable 
            documents={documents}
            onView={(doc) => console.log('View document:', doc)}
            onEdit={(doc) => {
              setEditingDocument(doc);
              setShowForm(true);
            }}
            onDelete={handleDelete}
            onDownload={handleDownload}
          />
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
            parcels={parcels.map(p => ({ id: p.id, parcel_number: p.parcel_number }))}
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
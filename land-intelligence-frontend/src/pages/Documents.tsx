import React, { useState, useEffect } from 'react';
import { PageContainer } from '@/components/layout/PageContainer';
import { FileText, Upload } from 'lucide-react';
import { documentService } from '@/services/documentService';
import type { Document } from '@/types/document';
import { DocumentTable } from '@/features/documents/components/DocumentTable';

export default function Documents() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadDocuments = async () => {
      try {
        const response = await documentService.getDocuments();
        if (response.success && response.data) {
          setDocuments(response.data);
        }
      } catch (error) {
        console.error('Failed to load documents', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadDocuments();
  }, []);

  return (
    <PageContainer
      title="Document Archive"
      subtitle="Digital deed registries, land titles, and lease files repository."
      action={
        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
          <Upload className="w-4 h-4" />
          Upload Document
        </button>
      }
    >
      <div className="flex items-center gap-3 p-6 rounded-xl border border-slate-800/80 bg-slate-900/30 mb-6">
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
          onEdit={(doc) => console.log('Edit document:', doc)}
          onDelete={(doc) => console.log('Delete document:', doc)}
          onDownload={(doc) => console.log('Download document:', doc)}
        />
      )}
    </PageContainer>
  );
}
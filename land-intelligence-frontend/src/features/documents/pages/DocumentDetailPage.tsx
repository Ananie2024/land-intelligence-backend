// Document Detail Page
// Land Intelligence System

import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { documentService } from '@/services/documentService';
import { DocumentDetail } from '@/features/documents/components/DocumentDetail';
import { Loader2, AlertCircle } from 'lucide-react';
import type { Document } from '@/types/document';

export const DocumentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [document, setDocument] = useState<Document | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const loadDocument = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await documentService.getDocumentById(id);
        if (response.success && response.data) {
          setDocument(response.data);
        } else {
          setError(response.message || 'Failed to load document');
        }
      } catch (err) {
        console.error('Failed to load document:', err);
        setError('Failed to load document details');
      } finally {
        setIsLoading(false);
      }
    };

    loadDocument();
  }, [id]);

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[300px]">
        <div className="flex items-center gap-3 text-slate-400">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Loading document details...</span>
        </div>
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="p-6">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center gap-2 text-red-500 mb-2">
            <AlertCircle className="h-5 w-5" />
            <span className="font-medium">Error</span>
          </div>
          <p className="text-gray-500">{error || 'Document not found'}</p>
          <p className="text-gray-400 text-sm mt-2">Document ID: {id}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="bg-white shadow rounded-lg p-6">
        <DocumentDetail document={document} />
      </div>
    </div>
  );
};

export default DocumentDetailPage;
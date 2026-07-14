// Document Table Component
// Land Intelligence System

import { Pencil, Trash2, Eye, FileText, Download } from 'lucide-react';
import type { Document } from '@/types/document';

interface DocumentTableProps {
  documents: Document[];
  onEdit: (document: Document) => void;
  onDelete: (document: Document) => void;
  onView: (document: Document) => void;
  onDownload: (document: Document) => void;
}

export const DocumentTable: React.FC<DocumentTableProps> = ({ 
  documents, 
  onEdit, 
  onDelete, 
  onView,
  onDownload 
}) => {
  if (!documents || documents.length === 0) {
    return (
      <div className="text-center py-12 text-slate-400">
        <p>No documents found</p>
      </div>
    );
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-800">
        <thead className="bg-slate-900/60">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Document
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Type
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Size
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Date
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
              Parcel
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-slate-900/40 divide-y divide-slate-800">
          {documents.map((document) => (
            <tr key={document.id} className="hover:bg-slate-900/60 transition-colors">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <FileText className="h-5 w-5 text-slate-400 mr-2" />
                  <div>
                    <div className="text-sm font-medium text-slate-200">{document.filename}</div>
                    {document.description && (
                      <div className="text-sm text-slate-400">{document.description}</div>
                    )}
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                {document.document_type_name || document.document_type_id}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                {formatFileSize(document.file_size_bytes)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                {document.document_date 
                  ? new Date(document.document_date).toLocaleDateString() 
                  : '-'}
              </td>
               <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                 {document.parcel_upi || '-'}
               </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div className="flex items-center justify-end gap-2">
                  <button
                    onClick={() => onDownload(document)}
                    className="text-slate-400 hover:text-slate-200"
                    title="Download"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onView(document)}
                    className="text-slate-400 hover:text-slate-200"
                    title="View"
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onEdit(document)}
                    className="text-primary-400 hover:text-primary-300"
                    title="Edit"
                  >
                    <Pencil className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => onDelete(document)}
                    className="text-red-400 hover:text-red-300"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DocumentTable;

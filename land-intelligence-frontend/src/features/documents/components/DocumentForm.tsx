// Document Form Component
// Land Intelligence System

import { useState, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import type { Document, DocumentCreate } from '@/types/document';

interface DocumentFormProps {
  document?: Document | null;
  onSubmit: (data: DocumentCreate, file?: File) => Promise<void>;
  isLoading?: boolean;
  parcels?: Array<{ id: string; upi: string }>;
  documentTypes?: Array<{ id: string; name: string }>;
}

export const DocumentForm: React.FC<DocumentFormProps> = ({ 
  document, 
  onSubmit, 
  isLoading = false,
  parcels = [],
  documentTypes = []
}) => {
  const {
    register,
    handleSubmit,
  } = useForm<DocumentCreate>({
    defaultValues: document ? {
      document_type_id: document.document_type_id,
      parcel_upi: document.parcel_upi || '',
      reference_number: document.reference_number || '',
      document_date: document.document_date || '',
      description: document.description || '',
    } : undefined,
  });
  
  // Store file in state to pass to submit handler
  const [selectedFile, setSelectedFile] = useState<File | undefined>(undefined);

  const handleFormSubmit = useCallback(async (data: DocumentCreate) => {
    await onSubmit(data, selectedFile);
  }, [onSubmit, selectedFile]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    setSelectedFile(file);
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <div>
        <label htmlFor="document_type_id" className="block text-sm font-medium text-gray-700">
          Document Type
        </label>
        <select
          {...register('document_type_id', { required: 'Document type is required' })}
          id="document_type_id"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        >
          <option value="">Select document type</option>
          {documentTypes.map((type) => (
            <option key={type.id} value={type.id}>{type.name}</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="parcel_upi" className="block text-sm font-medium text-gray-700">
          UPI (Unique Parcel Identifier)
        </label>
        <input
          {...register('parcel_upi')}
          type="text"
          id="parcel_upi"
          placeholder="e.g., 1/02/02/03/1390"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
        <p className="mt-1 text-xs text-gray-500">Enter the parcel UPI to link this document</p>
      </div>

      <div>
        <label htmlFor="reference_number" className="block text-sm font-medium text-gray-700">
          Reference Number
        </label>
        <input
          {...register('reference_number')}
          type="text"
          id="reference_number"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
      </div>

      <div>
        <label htmlFor="document_date" className="block text-sm font-medium text-gray-700">
          Document Date
        </label>
        <input
          {...register('document_date')}
          type="date"
          id="document_date"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          {...register('description')}
          id="description"
          rows={2}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          disabled={isLoading}
        />
      </div>

      <div>
        <label htmlFor="file" className="block text-sm font-medium text-gray-700">
          File Upload {!document && <span className="text-red-500">*</span>}
        </label>
        <input
          type="file"
          id="file"
          onChange={handleFileChange}
          className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700"
          disabled={isLoading}
          required={!document}
        />
        {document && (
          <p className="mt-1 text-xs text-gray-500">Current file: {document.filename}</p>
        )}
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {isLoading ? 'Saving...' : document ? 'Update Document' : 'Upload Document'}
        </button>
      </div>
    </form>
  );
};

export default DocumentForm;
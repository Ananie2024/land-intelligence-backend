// Document Form Component
// Land Intelligence System

import { useState, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { FormField } from '@/components/ui/FormField';
import type { Document, DocumentCreate, DocumentType } from '@/types/document';

interface DocumentFormProps {
  document?: Document | null;
  onSubmit: (data: DocumentCreate, file?: File) => Promise<void>;
  isLoading?: boolean;
  parcels?: Array<{ id: string; upi: string }>;
  documentTypes?: DocumentType[];
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
      <FormField
        label="Document Type"
        name="document_type_id"
        register={register}
        disabled={isLoading}
      >
        <option value="">Select document type</option>
        {documentTypes.map((type) => (
          <option key={type.id} value={type.id}>{type.name}</option>
        ))}
      </FormField>

      <FormField
        label="UPI (Unique Parcel Identifier)"
        name="parcel_upi"
        type="text"
        register={register}
        disabled={isLoading}
        placeholder="e.g., 1/02/02/03/1390"
        optional
        helperText="Enter the parcel UPI to link this document"
      />

      <FormField
        label="Reference Number"
        name="reference_number"
        type="text"
        register={register}
        disabled={isLoading}
        optional
      />

      <FormField
        label="Document Date"
        name="document_date"
        type="date"
        register={register}
        disabled={isLoading}
        optional
      />

      <FormField
        label="Description"
        name="description"
        type="text"
        register={register}
        disabled={isLoading}
        optional
        rows={2}
      />

      <FormField
        label="File Upload"
        name="file"
        type="file"
        disabled={isLoading}
        required={!document}
        onChange={handleFileChange}
        helperText={!document ? 'A file is required for new documents' : `Current file: ${document.filename}`}
        optional={!!document}
      />

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-500 disabled:opacity-50 transition-colors"
        >
          {isLoading ? 'Saving...' : document ? 'Update Document' : 'Upload Document'}
        </button>
      </div>
    </form>
  );
};

export default DocumentForm;
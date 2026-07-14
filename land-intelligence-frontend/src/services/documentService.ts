import { api } from '@/api/axios';
import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { Document, DocumentCreate, DocumentUpdate, DocumentFilters } from '@/types/document';
import { APIResponse } from '@/types/api';

export const documentService = {
  getDocuments: async (filters?: DocumentFilters): Promise<APIResponse<Document[]>> => {
    const response = await apiClient.get<{ items: Document[]; total: number; page: number; size: number; pages: number }>(ENDPOINTS.DOCUMENTS.BASE, filters);
    // Transform paginated response to expected format
    return {
      ...response,
      data: response.data?.items ?? null,
    };
  },

  getDocumentById: async (id: string): Promise<APIResponse<Document>> => {
    return apiClient.get<Document>(ENDPOINTS.DOCUMENTS.BY_ID(id));
  },

  uploadDocument: async (
    file: File,
    data: DocumentCreate
  ): Promise<APIResponse<Document>> => {
    // Note: File upload requires special handling with FormData
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type_id', data.document_type_id);
    if (data.parcel_upi) formData.append('parcel_upi', data.parcel_upi);
    if (data.description) formData.append('description', data.description);
    if (data.document_date) formData.append('document_date', data.document_date);
    if (data.reference_number) formData.append('reference_number', data.reference_number);

    return apiClient.post<Document>(ENDPOINTS.DOCUMENTS.UPLOAD, formData);
  },

  updateDocument: async (id: string, document: DocumentUpdate): Promise<APIResponse<Document>> => {
    return apiClient.patch<Document>(ENDPOINTS.DOCUMENTS.BY_ID(id), document);
  },

  deleteDocument: async (id: string, hardDelete?: boolean): Promise<APIResponse<{ message: string }>> => {
    // Use params to pass hard_delete flag
    const params = hardDelete ? { hard_delete: true } : undefined;
    
    // Use api instance directly for delete with params support
    const response = await api.delete<APIResponse<{ message: string }>>(ENDPOINTS.DOCUMENTS.BY_ID(id), { params });
    return response.data;
  },

  downloadDocument: async (id: string): Promise<Blob> => {
    // Use api instance directly with responseType: 'blob' for file download
    const response = await api.get(ENDPOINTS.DOCUMENTS.DOWNLOAD(id), {
      responseType: 'blob'
    });
    return response.data as Blob;
  },
};

export default documentService;

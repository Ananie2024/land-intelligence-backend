import { apiClient } from '@/api/apiClient';
import { ENDPOINTS } from '@/api/endpoints';
import { Document, DocumentCreate, DocumentUpdate, DocumentFilters } from '@/types/document';
import { APIResponse } from '@/types/api';

export const documentService = {
  getDocuments: async (filters?: DocumentFilters): Promise<APIResponse<Document[]>> => {
    return apiClient.get<Document[]>(ENDPOINTS.DOCUMENTS.BASE, filters);
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
    if (data.parcel_id) formData.append('parcel_id', data.parcel_id);
    if (data.description) formData.append('description', data.description);
    if (data.document_date) formData.append('document_date', data.document_date);
    if (data.reference_number) formData.append('reference_number', data.reference_number);

    return apiClient.post<Document>(ENDPOINTS.DOCUMENTS.UPLOAD, formData);
  },

  updateDocument: async (id: string, document: DocumentUpdate): Promise<APIResponse<Document>> => {
    return apiClient.patch<Document>(ENDPOINTS.DOCUMENTS.BY_ID(id), document);
  },

  deleteDocument: async (id: string, hardDelete?: boolean): Promise<APIResponse<{ message: string }>> => {
    const params = hardDelete ? { hard_delete: true } : undefined;
    return apiClient.delete<{ message: string }>(ENDPOINTS.DOCUMENTS.BY_ID(id));
  },

  downloadDocument: async (id: string): Promise<Blob> => {
    const response = await apiClient.get<Blob>(`${ENDPOINTS.DOCUMENTS.BY_ID(id)}/file`);
    return response.data as unknown as Blob;
  },
};

export default documentService;
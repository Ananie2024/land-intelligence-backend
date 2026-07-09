// API Index - Centralized exports for all API services and utilities
// Land Intelligence System

// Axios client and interceptors
export { api, ApiError } from './axios';

// API client wrapper
export { apiClient } from './apiClient';

// Query client for React Query
export { queryClient } from './queryClient';

// Endpoint definitions
export { ENDPOINTS } from './endpoints';

// Services
export { authService } from '@/services/authService';
export { landService } from '@/services/landService';
export { userService } from '@/services/userService';
export { documentService } from '@/services/documentService';
export { projectService } from '@/services/projectService';
export { reportService } from '@/services/reportService';

// Types
export type { APIResponse, PaginatedResponse, ErrorDetail } from '@/types/api';
export type { BaseEntity, QueryFilters, PaginationMeta } from '@/types/common';
export type {
  UserBase,
  UserCreate,
  UserResponse,
  UserLogin,
  TokenResponse,
  PasswordChange,
  UserRole,
} from '@/types/user';
export type {
  Parish,
  ParishCreate,
  Parcel,
  ParcelCreate,
  ParcelFilters,
  ParcelOwnershipHistory,
} from '@/types/land';
export type {
  Project,
  ProjectCreate,
  ProjectStatus,
} from '@/types/project';
export type {
  Document,
  DocumentCreate,
  DocumentUpdate,
  DocumentFilters,
  DocumentType,
} from '@/types/document';
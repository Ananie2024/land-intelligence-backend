/**
 * Backend API Endpoints Mapping
 * Land Intelligence System
 * 
 * Matches backend routes from app/api/v1/routes/
 */

export const ENDPOINTS = {
  // Health check
  HEALTH: '/health',
  
  // Auth endpoints
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
    ME: '/auth/me',
    CHANGE_PASSWORD: '/auth/change-password',
    UPDATE_ME: '/auth/me',
  },
  
   // Users endpoints (admin managed)
   USERS: {
      BASE: '/users/',
      BY_ID: (id: string) => `/users/${id}`,
      },
     
  // Parishes endpoints
  PARISHES: {
    BASE: '/parishes',
    BY_ID: (id: string) => `/parishes/${id}`,
    ALL: '/parishes/all',
  },
  
  // Parcels endpoints
  PARCELS: {
    BASE: '/parcels',
    BY_ID: (id: string) => `/parcels/${id}`,
    BY_NUMBER: (number: string) => `/parcels/by-number/${number}`,
    BY_PARISH: (parishId: string) => `/parcels/parish/${parishId}`,
    OWNERSHIP_HISTORY: (id: string) => `/parcels/${id}/ownership-history`,
    FOR_MAP: '/parcels/map',
    ALL: '/parcels/all',
  },
  
  // Documents endpoints
  DOCUMENTS: {
    BASE: '/documents',
    BY_ID: (id: string) => `/documents/${id}`,
    UPLOAD: '/documents/upload',
    DOWNLOAD: (id: string) => `/documents/${id}/file`,
  },
  
  // Document Types endpoints
  DOCUMENT_TYPES: {
    BASE: '/document-types',
    BY_ID: (id: string) => `/document-types/${id}`,
    BY_CODE: (code: string) => `/document-types/code/${code}`,
  },
  
  // GIS Analysis endpoints
  GIS: {
    BASE: '/gis',
    DISTANCE: '/gis/distance',
    INTERSECTS: '/gis/intersects',
    CONTAINS_POINT: '/gis/contains-point',
    CHECK_OVERLAY: '/gis/check-overlay',
  },
  
  // Tax endpoints
  TAX: {
    BASE: '/tax',
    CALCULATE: '/tax/calculate',
    ASSESS: '/tax/assess',
    ASSESS_PARISH: (parishId: string) => `/tax/assess/parish/${parishId}`,
    PAYMENTS: '/tax/payments',
    OUTSTANDING: (parcelId: string) => `/tax/outstanding/${parcelId}`,
    HISTORY: (parcelId: string) => `/tax/history/${parcelId}`,
    RECORD: (recordId: string) => `/tax/record/${recordId}`,
  },
  
  // QR Code endpoints
  QR: {
    BASE: '/qr',
    GENERATE_PARCEL: (id: string) => `/qr/generate/parcel/${id}`,
    GENERATE_DOCUMENT: (id: string) => `/qr/generate/document/${id}`,
    VERIFY: '/qr/verify',
    BY_ID: (id: string) => `/qr/${id}`,
    REVOKE: (id: string) => `/qr/${id}`,
  },
  
  // Locations endpoints
  LOCATIONS: {
    BASE: '/locations',
    BY_ID: (id: string) => `/locations/${id}`,
    FIND: '/locations/find',
    CABINETS: '/locations/cabinets',
    CABINETS_BY_ID: (id: string) => `/locations/cabinets/${id}`,
    GRID: (locationId: string) => `/locations/${locationId}/grid`,
  },

// Backups endpoints
    BACKUPS: {
       BASE: '/backups',
       TRIGGER: '/backups/trigger',
       VERIFY: '/backups/verify',
       JOBS: '/backups/jobs',
       BY_JOB_ID: (jobId: string) => `/backups/jobs/${jobId}`,
       DOWNLOAD: (jobId: string) => `/backups/jobs/${jobId}/download`,
       RESTORE: '/backups/restore',
       RESTORE_BY_ID: (jobId: string) => `/backups/restore/${jobId}`,
    },
  
    // Dashboard endpoints
    DASHBOARD: {
      BASE: '/dashboard',
      STATS: '/dashboard/stats',
      STATS_PARISHES: '/dashboard/stats/parishes',
      STATS_PARCELS: '/dashboard/stats/parcels',
      STATS_USERS: '/dashboard/stats/users',
    },

// Reports endpoints
    REPORTS: {
      BASE: '/reports',
      TAX: (parcelId: string) => `/reports/tax/${parcelId}`,
      PARCELS: '/reports/parcels',
      DASHBOARD: '/reports/dashboard',
    },
  
    // Settings endpoints
    SETTINGS: {
      GET: '/settings',
      UPDATE: '/settings',
      LOGS: '/settings/logs',
    },
    } as const;
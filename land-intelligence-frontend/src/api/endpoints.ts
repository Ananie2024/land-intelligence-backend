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
    BASE: '/users',
    BY_ID: (id: string) => `/users/${id}`,
    UPDATE_ME: '/auth/me',
  },
  
  // Parishes endpoints
  PARISHES: {
    BASE: '/parishes',
    BY_ID: (id: string) => `/parishes/${id}`,
    REFRESH_COUNT: (id: string) => `/parishes/${id}/refresh-count`,
  },
  
  // Parcels endpoints
  PARCELS: {
    BASE: '/parcels',
    BY_ID: (id: string) => `/parcels/${id}`,
    BY_NUMBER: (number: string) => `/parcels/by-number/${number}`,
    BY_DEED: (deed: string) => `/parcels/by-deed/${deed}`,
    BY_PARISH: (parishId: string) => `/parcels/parish/${parishId}`,
    OWNERSHIP_HISTORY: (id: string) => `/parcels/${id}/ownership-history`,
    FOR_MAP: '/parcels/map',
  },
  
  // Documents endpoints
  DOCUMENTS: {
    BASE: '/documents',
    BY_ID: (id: string) => `/documents/${id}`,
    UPLOAD: '/documents/upload',
    DOWNLOAD: (id: string) => `/documents/${id}/file`,
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
    GENERATE: (id: string) => `/qr/parcels/${id}/generate`,
    VERIFY: (token: string) => `/qr/verify/${token}`,
  },
  
  // Locations endpoints
  LOCATIONS: {
    BASE: '/locations',
    CABINETS: '/locations/cabinets',
  },
  
  // Backups endpoints
  BACKUPS: {
    BASE: '/backups',
    VERIFY: '/backups/verify',
  },

  // Projects endpoints (for future backend implementation)
  PROJECTS: {
    BASE: '/projects',
    BY_ID: (id: string) => `/projects/${id}`,
  },

  // Dashboard endpoints
  DASHBOARD: {
    BASE: '/dashboard',
    STATS: '/dashboard/stats',
    STATS_PARISHES: '/dashboard/stats/parishes',
    STATS_PARCELS: '/dashboard/stats/parcels',
    STATS_USERS: '/dashboard/stats/users',
  },
} as const;

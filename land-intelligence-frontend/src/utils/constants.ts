/**
 * Application Constants
 * Land Intelligence System
 */

export const LOCAL_STORAGE_KEYS = {
  ACCESS_TOKEN: 'land_intel_access_token',
  REFRESH_TOKEN: 'land_intel_refresh_token',
  USER_PROFILE: 'land_intel_user_profile',
  THEME: 'land_intel_theme',
} as const;

export const USER_ROLES = {
  ADMIN: 'admin',
  CLIENT: 'client',
  VIEWER: 'viewer',
} as const;

export type UserRole = (typeof USER_ROLES)[keyof typeof USER_ROLES];

export const API_ROUTES = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
    ME: '/auth/me',
    CHANGE_PASSWORD: '/auth/change-password',
  },
  PARISHES: '/parishes',
  PARCELS: '/parcels',
  DOCUMENTS: '/documents',
  GIS: '/gis',
  TAX: '/tax',
  QR: '/qr',
  LOCATIONS: '/locations',
  BACKUPS: '/backups',
} as const;

export const DEFAULT_PAGINATION = {
  PAGE: 1,
  SIZE: 10,
  SIZE_OPTIONS: [5, 10, 20, 50, 100],
} as const;

export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark',
} as const;

export type Theme = (typeof THEMES)[keyof typeof THEMES];

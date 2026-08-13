// Lazy-loaded page components
// Land Intelligence System

import React from 'react';

// Feature pages
export const Dashboard = React.lazy(() => import('@/pages/Dashboard'));
export const Parcels = React.lazy(() => import('@/pages/Parcels'));
export const Parishes = React.lazy(() => import('@/pages/Parishes'));
export const Documents = React.lazy(() => import('@/pages/Documents'));
export const Tax = React.lazy(() => import('@/pages/Tax'));
export const Leases = React.lazy(() => import('@/pages/Leases'));
export const QrCodes = React.lazy(() => import('@/pages/QrCodes'));
export const Gis = React.lazy(() => import('@/pages/Gis'));
export const Users = React.lazy(() => import('@/pages/Users'));
export const Backups = React.lazy(() => import('@/pages/Backups'));
export const Settings = React.lazy(() => import('@/pages/Settings'));
export const Reports = React.lazy(() => import('@/pages/Reports'));

// Detail pages
export const ParcelDetailPage = React.lazy(() => import('@/features/land/pages/ParcelDetailPage'));
export const ParishDetailPage = React.lazy(() => import('@/features/land/pages/ParishDetailPage'));
export const DocumentDetailPage = React.lazy(() => import('@/features/documents/pages/DocumentDetailPage'));
export const UserDetailPage = React.lazy(() => import('@/features/users/pages/UserDetailPage'));
export const UserProfilePage = React.lazy(() => import('@/features/users/pages/UserProfilePage'));
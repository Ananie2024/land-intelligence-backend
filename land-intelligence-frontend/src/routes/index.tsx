import { createBrowserRouter } from 'react-router-dom';
import DashboardLayout from '@/layouts/DashboardLayout';
import { ProtectedRoute } from './protectedRoutes';
import { publicRoutes } from './publicRoutes';
import { SuspenseFallback } from './SuspenseFallback';
import {
  Dashboard,
  Parcels,
  Parishes,
  Documents,
  Tax,
  Leases,
  QrCodes,
  Gis,
  Users,
  Backups,
  Settings,
  Reports,
  ParcelDetailPage,
  ParishDetailPage,
  DocumentDetailPage,
  UserDetailPage,
  UserProfilePage,
} from './lazyComponents';


export const router = createBrowserRouter([
  // Public routes (Auth pages, Unauthorized, 404 fallback)
  ...publicRoutes.map(route => ({
    ...route,
  })),

  // Protected application routes
  {
    path: '/',
    element: <ProtectedRoute />, // Root auth gate
    children: [
      {
        element: <DashboardLayout />,
        children: [
          {
            path: 'dashboard',
            element: <SuspenseFallback><Dashboard /></SuspenseFallback>,
          },
          {
            path: 'parcels',
            element: <SuspenseFallback><Parcels /></SuspenseFallback>,
          },
          {
            path: 'parcels/:id',
            element: <SuspenseFallback><ParcelDetailPage /></SuspenseFallback>,
          },
          {
            path: 'parishes',
            element: <SuspenseFallback><Parishes /></SuspenseFallback>,
          },
          {
            path: 'parishes/:id',
            element: <SuspenseFallback><ParishDetailPage /></SuspenseFallback>,
          },
          {
            path: 'documents',
            element: <SuspenseFallback><Documents /></SuspenseFallback>,
          },
          {
            path: 'documents/:id',
            element: <SuspenseFallback><DocumentDetailPage /></SuspenseFallback>,
          },
          {
            path: 'tax',
            element: <SuspenseFallback><Tax /></SuspenseFallback>,
          },
          {
            path: 'leases',
            element: <SuspenseFallback><Leases /></SuspenseFallback>,
          },
          {
            path: 'qr',
            element: <SuspenseFallback><QrCodes /></SuspenseFallback>,
          },
          {
            path: 'gis',
            element: <SuspenseFallback><Gis /></SuspenseFallback>,
          },
          {
            path: 'reports',
            element: <SuspenseFallback><Reports /></SuspenseFallback>,
          },
          {
            path: 'profile',
            element: <SuspenseFallback><UserProfilePage /></SuspenseFallback>,
          },
          {
            path: 'settings',
            element: <SuspenseFallback><Settings /></SuspenseFallback>,
          },
          // Admin-only protected sub-routes
          {
            element: <ProtectedRoute allowedRoles={['admin']} />,
            children: [
              {
                path: 'users',
                element: <SuspenseFallback><Users /></SuspenseFallback>,
              },
              {
                path: 'users/:id',
                element: <SuspenseFallback><UserDetailPage /></SuspenseFallback>,
              },
              {
                path: 'backups',
                element: <SuspenseFallback><Backups /></SuspenseFallback>,
              },
            ],
          },
        ],
      },
    ],
  },
]);
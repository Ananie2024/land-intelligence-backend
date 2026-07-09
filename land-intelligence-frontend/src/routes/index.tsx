import React from 'react';
import { createBrowserRouter, Navigate, useLocation, useSearchParams } from 'react-router-dom';
import DashboardLayout from '@/layouts/DashboardLayout';
import { ProtectedRoute } from './protectedRoutes';
import { publicRoutes } from './publicRoutes';

// Lazy load feature pages for better chunk loading
const Dashboard = React.lazy(() => import('@/pages/Dashboard'));
const Parcels = React.lazy(() => import('@/pages/Parcels'));
const Parishes = React.lazy(() => import('@/pages/Parishes'));
const Documents = React.lazy(() => import('@/pages/Documents'));
const Tax = React.lazy(() => import('@/pages/Tax'));
const QrCodes = React.lazy(() => import('@/pages/QrCodes'));
const Gis = React.lazy(() => import('@/pages/Gis'));
const Users = React.lazy(() => import('@/pages/Users'));
const Backups = React.lazy(() => import('@/pages/Backups'));
const Settings = React.lazy(() => import('@/pages/Settings'));

// Loading page fallback wrapper
function SuspenseFallback({ children }: { children: React.ReactNode }) {
  return (
    <React.Suspense fallback={
      <div className="flex-grow flex items-center justify-center min-h-[300px]">
        <div className="rounded-full border-t-primary-500 border-slate-700 animate-spin w-8 h-8 border-3" />
      </div>
    }>
      {children}
    </React.Suspense>
  );
}

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
            path: 'parishes',
            element: <SuspenseFallback><Parishes /></SuspenseFallback>,
          },
          {
            path: 'documents',
            element: <SuspenseFallback><Documents /></SuspenseFallback>,
          },
          {
            path: 'tax',
            element: <SuspenseFallback><Tax /></SuspenseFallback>,
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
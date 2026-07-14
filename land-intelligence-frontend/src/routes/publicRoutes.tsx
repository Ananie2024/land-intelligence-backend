import React from 'react';
import { RouteObject } from 'react-router-dom';
import AuthLayout from '@/layouts/AuthLayout';
import Landing from '@/pages/Landing';
import Login from '@/pages/Login';
import Unauthorized from '@/pages/Unauthorized';
import NotFound from '@/pages/NotFound';

export const publicRoutes: RouteObject[] = [
  {
    path: '/',
    element: <AuthLayout />,
    children: [
      {
        index: true,
        element: <Landing />,
      },
      {
        path: 'login',
        element: <Login />,
      },
    ],
  },
  {
    path: '/unauthorized',
    element: <Unauthorized />,
  },
  {
    path: '*',
    element: <NotFound />,
  },
];

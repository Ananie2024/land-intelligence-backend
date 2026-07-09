import { QueryClient, QueryCache, MutationCache } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { ApiError } from '@/api/axios';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => {
        // Do not retry for unauthorized (session invalidation/refresh failures), 
        // forbidden (no permissions), or not found (doesn't exist) errors.
        if (error instanceof ApiError) {
          if ([401, 403, 404].includes(error.status)) {
            return false;
          }
        }
        // Otherwise retry transient errors up to 2 times
        return failureCount < 2;
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (garbage collection time / cacheTime)
    },
    mutations: {
      retry: false,
    },
  },
  queryCache: new QueryCache({
    onError: (error) => {
      // Global error handler for all query fetches
      if (error instanceof ApiError) {
        // Suppress 401 messages as they trigger redirects or token refresh loops
        if (error.status !== 401) {
          toast.error(error.message || 'Failed to fetch required data.');
        }
      } else {
        toast.error((error as Error).message || 'An unexpected connection error occurred.');
      }
    },
  }),
  mutationCache: new MutationCache({
    onError: (error) => {
      // Global error handler for all data mutations (POST, PUT, DELETE, PATCH)
      if (error instanceof ApiError) {
        if (error.status !== 401) {
          if (error.errors && error.errors.length > 0) {
            // Display first validation/business rule error message
            toast.error(error.errors[0].message);
          } else {
            toast.error(error.message || 'Action could not be completed.');
          }
        }
      } else {
        toast.error((error as Error).message || 'An unexpected error occurred.');
      }
    },
  }),
});

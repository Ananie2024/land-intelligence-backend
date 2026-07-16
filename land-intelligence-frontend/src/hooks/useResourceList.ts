import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import type { UseQueryOptions } from '@tanstack/react-query';
import type { APIResponse } from '@/types/api';
import type { PaginatedEnvelope } from '@/api/apiClient';

export type ListFilters = {
  page?: number;
  size?: number;
  search?: string;
};

export type ResourceListResult<T> = {
  data: T[];
  isLoading: boolean;
  error: string | null;
  totalItems: number;
  totalPages: number;
  refetch: () => void;
  isRefetching: boolean;
};

export function transformFilters(filters: ListFilters): Record<string, any> {
  return {
    page: filters.page ?? 1,
    size: filters.size ?? 20,
    search: filters.search || undefined,
  };
}

export function useResourceList<T>(
  queryKey: string[],
  fetchFn: (filters: Record<string, any>) => Promise<APIResponse<PaginatedEnvelope<T>>>,
  filters: ListFilters,
  config?: {
    defaultFilters?: ListFilters;
    enableQuery?: boolean;
    queryOptions?: UseQueryOptions<APIResponse<PaginatedEnvelope<T>>>;
    onSuccess?: (result: ResourceListResult<T>) => void;
  }
): ResourceListResult<T> {
  const defaultFilters = config?.defaultFilters ?? { page: 1, size: 20, search: '' };
  const resolvedFilters = { ...defaultFilters, ...filters };
  const transformedFilters = transformFilters(resolvedFilters);

  const result = useQuery({
    queryKey: [...queryKey, transformedFilters],
    queryFn: () => fetchFn(transformedFilters),
    enabled: config?.enableQuery ?? true,
    ...config?.queryOptions,
  });

  const listResult: ResourceListResult<T> = {
    data: [],
    isLoading: result.isLoading,
    error: result.error ? (result.error as Error).message : null,
    totalItems: 0,
    totalPages: 0,
    refetch: result.refetch,
    isRefetching: result.isFetching,
  };

  if (result.data) {
    if (result.data.success && result.data.data) {
      listResult.data = result.data.data.items;
      listResult.totalItems = result.data.data.total;
      listResult.totalPages = result.data.data.pages;
      listResult.error = null;
    } else {
      listResult.error = result.data.message || 'Failed to load data';
    }
  }

  config?.onSuccess?.(listResult);

  return listResult;
}

export function useResourceQuery<T>(
  queryKey: string[],
  fetchFn: () => Promise<APIResponse<T>>,
  config?: {
    enabled?: boolean;
    queryOptions?: UseQueryOptions<APIResponse<T>>;
  }
): { data: T | null; isLoading: boolean; error: string | null; refetch: () => void; isRefetching: boolean } {
  const result = useQuery({
    queryKey,
    queryFn: fetchFn,
    enabled: config?.enabled ?? true,
    ...config?.queryOptions,
  });

  return {
    data: result.data?.success && result.data.data ? result.data.data : null,
    isLoading: result.isLoading,
    error: result.data?.success === false ? (result.data.message || 'Failed to load data') : (result.error ? (result.error as Error).message : null),
    refetch: result.refetch,
    isRefetching: result.isFetching,
  };
}

export function useResourceMutation<TData, TVariables>(
  mutationFn: (variables: TVariables) => Promise<APIResponse<TData>>,
  config?: {
    invalidateKeys?: string[];
    successMessage?: string;
    onSuccess?: (data: TData) => void;
    onError?: (error: Error) => void;
  }
): {
  mutate: (variables: TVariables) => Promise<void>;
  isLoading: boolean;
  error: string | null;
} {
  const queryClientInstance = useQueryClient();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return {
    mutate: async (variables: TVariables) => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await mutationFn(variables);
        if (response.success) {
          config?.invalidateKeys?.forEach((key) => {
            queryClientInstance.invalidateQueries({ queryKey: [key] });
          });
          if (response.data) {
            config?.onSuccess?.(response.data);
          }
        } else {
          const msg = response.message || 'Operation failed';
          setError(msg);
          config?.onError?.(new Error(msg));
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : 'An unexpected error occurred';
        setError(message);
        config?.onError?.(new Error(message));
      } finally {
        setIsLoading(false);
      }
    },
    isLoading,
    error,
  };
}
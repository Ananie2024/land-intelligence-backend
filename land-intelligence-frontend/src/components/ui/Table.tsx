import React from 'react';
import { LoadingSpinner } from './LoadingSpinner';

export interface Column<T> {
  key: string;
  header: React.ReactNode;
  render?: (row: T, index: number) => React.ReactNode;
  className?: string;
  headerClassName?: string;
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  isLoading?: boolean;
  emptyStateMessage?: string;
  onRowClick?: (row: T) => void;
  className?: string;
}

export function Table<T>({
  columns,
  data,
  isLoading = false,
  emptyStateMessage = 'No data available',
  onRowClick,
  className = '',
}: TableProps<T>) {
  return (
    <div className={`relative overflow-x-auto w-full rounded-xl border border-primary-200/60 bg-white ${className}`}>
      <table className="w-full text-sm text-left text-slate-600">
        <thead className="text-xs uppercase bg-primary-50/80 text-slate-500 border-b border-primary-200/60">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                scope="col"
                className={`px-6 py-4 font-semibold tracking-wider ${column.headerClassName || ''} ${column.className || ''}`}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-primary-100">
          {isLoading && data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-6 py-12 text-center">
                <div className="flex flex-col items-center justify-center gap-3">
                  <LoadingSpinner size="md" className="border-t-primary-500" />
                  <span className="text-slate-500 text-xs">Fetching records...</span>
                </div>
              </td>
            </tr>
          ) : data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-6 py-12 text-center text-slate-400">
                {emptyStateMessage}
              </td>
            </tr>
          ) : (
            data.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                onClick={() => onRowClick && onRowClick(row)}
                className={`
                  ${onRowClick ? 'cursor-pointer hover:bg-primary-50' : 'hover:bg-primary-50/50'}
                  transition-colors duration-150 group
                `}
              >
                {columns.map((column) => {
                  const renderedValue = column.render
                    ? column.render(row, rowIndex)
                    : (row as any)[column.key];

                  return (
                    <td
                      key={column.key}
                      className={`px-6 py-4.5 text-slate-600 font-medium group-hover:text-slate-800 transition-colors ${column.className || ''}`}
                    >
                      {renderedValue}
                    </td>
                  );
                })}
              </tr>
            ))
          )}
        </tbody>
      </table>
      
      {/* Loading Overlay for background updates */}
      {isLoading && data.length > 0 && (
        <div className="absolute inset-0 bg-white/60 backdrop-blur-[1px] flex items-center justify-center">
          <LoadingSpinner size="sm" className="border-t-primary-500" />
        </div>
      )}
    </div>
  );
}

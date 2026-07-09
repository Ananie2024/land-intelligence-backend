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
    <div className={`relative overflow-x-auto w-full rounded-xl border border-slate-800/80 bg-slate-900/40 ${className}`}>
      <table className="w-full text-sm text-left text-slate-300">
        <thead className="text-xs uppercase bg-slate-900/80 text-slate-400 border-b border-slate-800/80">
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
        <tbody className="divide-y divide-slate-800/50">
          {isLoading && data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-6 py-12 text-center">
                <div className="flex flex-col items-center justify-center gap-3">
                  <LoadingSpinner size="md" className="border-t-primary-500" />
                  <span className="text-slate-400 text-xs">Fetching records...</span>
                </div>
              </td>
            </tr>
          ) : data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-6 py-12 text-center text-slate-500">
                {emptyStateMessage}
              </td>
            </tr>
          ) : (
            data.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                onClick={() => onRowClick && onRowClick(row)}
                className={`
                  ${onRowClick ? 'cursor-pointer hover:bg-slate-800/30' : 'hover:bg-slate-900/20'}
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
                      className={`px-6 py-4.5 text-slate-300 font-medium group-hover:text-white transition-colors ${column.className || ''}`}
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
        <div className="absolute inset-0 bg-slate-950/40 backdrop-blur-[1px] flex items-center justify-center">
          <LoadingSpinner size="sm" className="border-t-primary-500" />
        </div>
      )}
    </div>
  );
}

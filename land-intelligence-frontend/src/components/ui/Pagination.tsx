/**
 * Reusable Pagination Component
 * Land Intelligence System
 */

import { ChevronLeft, ChevronRight, MoreHorizontal } from 'lucide-react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  totalItems,
  pageSize,
  onPageChange,
  onPageSizeChange,
}) => {
  const pages = [];
  const maxVisiblePages = 5;
  
  // Generate page numbers with ellipsis
  if (totalPages <= maxVisiblePages) {
    for (let i = 1; i <= totalPages; i++) {
      pages.push(i);
    }
  } else {
    // Always show first page
    pages.push(1);
    
    // Calculate start and end for visible pages
    let startPage = Math.max(2, currentPage - 1);
    let endPage = Math.min(totalPages - 1, currentPage + 1);
    
    // Add ellipsis if needed
    if (startPage > 2) {
      pages.push(-1); // -1 represents ellipsis
    }
    
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    
    // Add ellipsis if needed
    if (endPage < totalPages - 1) {
      pages.push(-1);
    }
    
    // Always show last page
    pages.push(totalPages);
  }

  const startItem = (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalItems);

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 px-4 py-3 bg-bg-surface border-t border-slate-700">
      <div className="text-sm text-slate-400">
        Showing {startItem} to {endItem} of {totalItems} entries
      </div>
      
      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label="Previous page"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        
        <div className="flex items-center gap-1">
          {pages.map((page, idx) => 
            page === -1 ? (
              <span key={`ellipsis-${idx}`} className="px-2 text-slate-500">
                <MoreHorizontal className="w-4 h-4" />
              </span>
            ) : (
              <button
                key={page}
                onClick={() => onPageChange(page)}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
                  currentPage === page
                    ? 'bg-primary-500 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-slate-700'
                }`}
              >
                {page}
              </button>
            )
          )}
        </div>
        
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label="Next page"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
      
      {onPageSizeChange && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-400">Rows:</span>
          <select
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            className="px-2 py-1 text-sm bg-slate-900/60 border border-slate-700 rounded text-slate-200"
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
        </div>
      )}
    </div>
  );
};

export default Pagination;
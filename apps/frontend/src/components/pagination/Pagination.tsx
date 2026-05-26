'use client';

import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import React from 'react';

// ============================================================================
// TYPES
// ============================================================================

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
  onPageChange: (page: number) => void;
  disabled?: boolean;
  showPageNumbers?: boolean;
  maxVisiblePages?: number;
}

// ============================================================================
// PAGINATION COMPONENT
// ============================================================================

export function Pagination({
  currentPage,
  totalPages,
  hasNext,
  hasPrev,
  onPageChange,
  disabled = false,
  showPageNumbers = true,
  maxVisiblePages = 5,
}: PaginationProps) {
  const getVisiblePages = () => {
    const pages: (number | string)[] = [];
    const sidePages = Math.floor(maxVisiblePages / 2);

    let startPage = Math.max(1, currentPage - sidePages);
    let endPage = Math.min(totalPages, currentPage + sidePages);

    // Adjust if near the beginning
    if (currentPage <= sidePages) {
      endPage = Math.min(totalPages, maxVisiblePages);
    }

    // Adjust if near the end
    if (currentPage > totalPages - sidePages) {
      startPage = Math.max(1, totalPages - maxVisiblePages + 1);
    }

    // Add first page and ellipsis
    if (startPage > 1) {
      pages.push(1);
      if (startPage > 2) {
        pages.push('...');
      }
    }

    // Add page numbers
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    // Add last page and ellipsis
    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        pages.push('...');
      }
      pages.push(totalPages);
    }

    return pages;
  };

  const visiblePages = getVisiblePages();

  return (
    <div className="flex items-center justify-between py-4 px-2">
      {/* Info */}
      <div className="text-xs font-medium text-slate-600">
        Page <span className="font-bold text-slate-900">{currentPage}</span> of{' '}
        <span className="font-bold text-slate-900">{totalPages}</span>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-1">
        {/* First page */}
        <button
          onClick={() => onPageChange(1)}
          disabled={disabled || !hasPrev}
          className="p-1 rounded hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="First page"
          aria-label="Go to first page"
        >
          <ChevronsLeft className="w-4 h-4 text-slate-600" />
        </button>

        {/* Previous */}
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={disabled || !hasPrev}
          className="p-1 rounded hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Previous page"
          aria-label="Go to previous page"
        >
          <ChevronLeft className="w-4 h-4 text-slate-600" />
        </button>

        {/* Page numbers */}
        {showPageNumbers && (
          <div className="flex items-center gap-1 mx-2">
            {visiblePages.map((page, idx) => {
              if (page === '...') {
                return (
                  <span
                    key={`ellipsis-${idx}`}
                    className="px-2 py-1 text-xs text-slate-400"
                  >
                    ...
                  </span>
                );
              }

              const isActive = page === currentPage;
              return (
                <button
                  key={page}
                  onClick={() => onPageChange(page as number)}
                  disabled={disabled}
                  className={`
                    w-8 h-8 rounded text-xs font-semibold
                    transition-colors disabled:cursor-not-allowed
                    ${
                      isActive
                        ? 'bg-sky-500 text-white'
                        : 'hover:bg-slate-100 text-slate-600'
                    }
                  `}
                >
                  {page}
                </button>
              );
            })}
          </div>
        )}

        {/* Next */}
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={disabled || !hasNext}
          className="p-1 rounded hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Next page"
          aria-label="Go to next page"
        >
          <ChevronRight className="w-4 h-4 text-slate-600" />
        </button>

        {/* Last page */}
        <button
          onClick={() => onPageChange(totalPages)}
          disabled={disabled || !hasNext}
          className="p-1 rounded hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Last page"
          aria-label="Go to last page"
        >
          <ChevronsRight className="w-4 h-4 text-slate-600" />
        </button>
      </div>

      {/* Spacer */}
      <div className="w-24" />
    </div>
  );
}

// ============================================================================
// SIMPLE PAGINATION (PREVIOUS/NEXT ONLY)
// ============================================================================

export function SimplePagination({
  hasNext,
  hasPrev,
  onPrevious,
  onNext,
  disabled = false,
}: {
  hasNext: boolean;
  hasPrev: boolean;
  onPrevious: () => void;
  onNext: () => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex items-center justify-center gap-4 py-4">
      <button
        onClick={onPrevious}
        disabled={disabled || !hasPrev}
        className="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium text-slate-700"
      >
        <ChevronLeft className="w-4 h-4" />
        Previous
      </button>

      <button
        onClick={onNext}
        disabled={disabled || !hasNext}
        className="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-200 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium text-slate-700"
      >
        Next
        <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  );
}

// ============================================================================
// PAGE SIZE SELECTOR
// ============================================================================

export function PageSizeSelector({
  pageSize,
  onPageSizeChange,
  options = [10, 20, 50],
  disabled = false,
}: {
  pageSize: number;
  onPageSizeChange: (size: number) => void;
  options?: number[];
  disabled?: boolean;
}) {
  return (
    <div className="flex items-center gap-2">
      <label htmlFor="page-size" className="text-xs font-medium text-slate-600">
        Show:
      </label>
      <select
        id="page-size"
        value={pageSize}
        onChange={(e) => onPageSizeChange(Number(e.target.value))}
        disabled={disabled}
        className="px-2 py-1 rounded border border-slate-200 bg-white text-xs font-medium text-slate-700 focus:outline-none focus:border-sky-400 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {options.map((size) => (
          <option key={size} value={size}>
            {size} items
          </option>
        ))}
      </select>
      <span className="text-xs text-slate-500">per page</span>
    </div>
  );
}

// ============================================================================
// PAGINATION WITH PAGE SIZE SELECTOR
// ============================================================================

export function PaginationWithPageSize({
  currentPage,
  totalPages,
  hasNext,
  hasPrev,
  pageSize,
  onPageChange,
  onPageSizeChange,
  disabled = false,
  pageSizeOptions = [10, 20, 50],
}: PaginationProps & {
  pageSize: number;
  onPageSizeChange: (size: number) => void;
  pageSizeOptions?: number[];
}) {
  return (
    <div className="flex items-center justify-between py-4 px-2 border-t border-slate-200">
      <PageSizeSelector
        pageSize={pageSize}
        onPageSizeChange={onPageSizeChange}
        options={pageSizeOptions}
        disabled={disabled}
      />

      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        hasNext={hasNext}
        hasPrev={hasPrev}
        onPageChange={onPageChange}
        disabled={disabled}
        showPageNumbers={true}
      />
    </div>
  );
}

// ============================================================================
// PAGINATION HOOK
// ============================================================================

import { useCallback } from 'react';

export function usePagination(
  initialPage = 1,
  initialPageSize = 20,
  onPageChange?: (page: number) => void,
  onPageSizeChange?: (pageSize: number) => void
) {
  const [page, setPage] = React.useState(initialPage);
  const [pageSize, setPageSize] = React.useState(initialPageSize);

  const handlePageChange = useCallback(
    (newPage: number) => {
      setPage(newPage);
      onPageChange?.(newPage);
    },
    [onPageChange]
  );

  const handlePageSizeChange = useCallback(
    (newPageSize: number) => {
      setPageSize(newPageSize);
      setPage(1); // Reset to first page on page size change
      onPageSizeChange?.(newPageSize);
    },
    [onPageSizeChange]
  );

  return {
    page,
    pageSize,
    setPage: handlePageChange,
    setPageSize: handlePageSizeChange,
  };
}

// ============================================================================
// RESULTS INFO COMPONENT
// ============================================================================

export function ResultsInfo({
  total,
  pageSize,
  currentPage,
  hasData = true,
}: {
  total: number;
  pageSize: number;
  currentPage: number;
  hasData?: boolean;
}) {
  if (!hasData) {
    return null;
  }

  const startItem = (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, total);

  return (
    <div className="text-xs text-slate-600">
      Showing <span className="font-semibold text-slate-900">{startItem}</span> to{' '}
      <span className="font-semibold text-slate-900">{endItem}</span> of{' '}
      <span className="font-semibold text-slate-900">{total}</span> results
    </div>
  );
}

'use client';

import React from 'react';

// ============================================================================
// SKELETON LOADER COMPONENTS
// ============================================================================

export function SkeletonBox({
  width = 'w-full',
  height = 'h-4',
  className = '',
}: {
  width?: string;
  height?: string;
  className?: string;
}) {
  return (
    <div
      className={`${width} ${height} bg-gradient-to-r from-slate-200 via-slate-100 to-slate-200 rounded animate-pulse ${className}`}
    />
  );
}

export function SkeletonProfessorCard() {
  return (
    <div className="border border-slate-200 rounded-lg p-4 mb-4 animate-pulse">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <SkeletonBox width="w-48" height="h-5" className="mb-2" />
          <SkeletonBox width="w-32" height="h-4" className="bg-slate-150" />
        </div>
        <SkeletonBox width="w-16" height="h-8" />
      </div>

      <div className="grid grid-cols-2 gap-3 mb-3">
        {[1, 2, 3, 4].map((i) => (
          <div key={i}>
            <SkeletonBox width="w-16" height="h-3" className="mb-1" />
            <SkeletonBox width="w-24" height="h-4" />
          </div>
        ))}
      </div>

      <SkeletonBox width="w-full" height="h-3" />
    </div>
  );
}

export function SkeletonList({ count = 5 }: { count?: number }) {
  return (
    <div>
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonProfessorCard key={i} />
      ))}
    </div>
  );
}

export function SkeletonTableRow({ columnCount = 5 }: { columnCount?: number }) {
  return (
    <tr className="border-b border-slate-200">
      {Array.from({ length: columnCount }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <SkeletonBox width="w-full" height="h-4" />
        </td>
      ))}
    </tr>
  );
}

export function SkeletonTable({
  rows = 5,
  columnCount = 5,
}: {
  rows?: number;
  columnCount?: number;
}) {
  return (
    <table className="w-full">
      <tbody>
        {Array.from({ length: rows }).map((_, i) => (
          <SkeletonTableRow key={i} columnCount={columnCount} />
        ))}
      </tbody>
    </table>
  );
}

export function SkeletonPagination() {
  return (
    <div className="flex items-center justify-between py-4 px-4">
      <SkeletonBox width="w-32" height="h-4" />
      <div className="flex gap-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <SkeletonBox
            key={i}
            width="w-8"
            height="h-8"
            className="rounded"
          />
        ))}
      </div>
      <SkeletonBox width="w-32" height="h-4" />
    </div>
  );
}

export function SkeletonDetailPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-6">
        <SkeletonBox width="w-64" height="h-8" className="mb-2" />
        <SkeletonBox width="w-48" height="h-4" />
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="border border-slate-200 rounded-lg p-4">
            <SkeletonBox width="w-20" height="h-3" className="mb-2" />
            <SkeletonBox width="w-12" height="h-6" />
          </div>
        ))}
      </div>

      {/* Comments Section */}
      <div>
        <SkeletonBox width="w-32" height="h-6" className="mb-4" />
        <SkeletonList count={3} />
      </div>
    </div>
  );
}

// ============================================================================
// LOADING STATE COMPONENTS
// ============================================================================

export function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className={`${sizeClasses[size]} border-2 border-sky-200 border-t-sky-600 rounded-full animate-spin`} />
  );
}

export function LoadingOverlay() {
  return (
    <div className="fixed inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 shadow-xl">
        <LoadingSpinner size="lg" />
        <p className="text-center text-sm text-slate-600 mt-4">Loading...</p>
      </div>
    </div>
  );
}

export function LoadingPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <LoadingSpinner size="lg" />
      <p className="text-center text-slate-600 mt-4">Loading content...</p>
    </div>
  );
}

// ============================================================================
// EMPTY STATE COMPONENTS
// ============================================================================

interface EmptyStateProps {
  icon?: string;
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export function EmptyState({
  icon = '🔍',
  title = 'No results found',
  subtitle = 'Try adjusting your filters',
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4">
      <div className="text-5xl mb-4">{icon}</div>
      <h3 className="text-lg font-semibold text-slate-800 mb-2">{title}</h3>
      <p className="text-sm text-slate-500 mb-6">{subtitle}</p>
      {action && <div>{action}</div>}
    </div>
  );
}

export function NoResultsState() {
  return (
    <EmptyState
      icon="📭"
      title="No results found"
      subtitle="Try adjusting your filters or search criteria"
    />
  );
}

export function NoDataState() {
  return (
    <EmptyState
      icon="📊"
      title="No data available"
      subtitle="There's nothing to display right now"
    />
  );
}

// ============================================================================
// ERROR STATE COMPONENTS
// ============================================================================

export function ErrorState({
  error,
  onRetry,
}: {
  error: Error | string;
  onRetry?: () => void;
}) {
  const message = error instanceof Error ? error.message : String(error);

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
      <div className="flex items-start gap-4">
        <div className="text-2xl">⚠️</div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-red-900 mb-1">
            Something went wrong
          </h3>
          <p className="text-sm text-red-700 mb-4">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="text-sm font-semibold text-red-700 hover:text-red-900 transition-colors"
            >
              Try again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// ADAPTIVE COMPONENTS (SHOW BASED ON STATE)
// ============================================================================

export function AdaptiveList<T extends { id: string | number }>({
  items,
  loading,
  error,
  empty,
  renderItem,
  skeletonCount = 5,
  onRetry,
}: {
  items: T[] | null;
  loading: boolean;
  error: Error | null;
  empty?: boolean;
  renderItem: (item: T) => React.ReactNode;
  skeletonCount?: number;
  onRetry?: () => void;
}) {
  if (loading) {
    return <SkeletonList count={skeletonCount} />;
  }

  if (error) {
    return <ErrorState error={error} onRetry={onRetry} />;
  }

  if (!items || items.length === 0 || empty) {
    return <NoResultsState />;
  }

  return <div>{items.map((item) => renderItem(item))}</div>;
}

export function AdaptiveContent({
  loading,
  error,
  empty,
  children,
  onRetry,
  skeleton = <SkeletonList />,
}: {
  loading: boolean;
  error: Error | null;
  empty?: boolean;
  children: React.ReactNode;
  onRetry?: () => void;
  skeleton?: React.ReactNode;
}) {
  if (loading) {
    return skeleton;
  }

  if (error) {
    return <ErrorState error={error} onRetry={onRetry} />;
  }

  if (empty) {
    return <NoResultsState />;
  }

  return children;
}

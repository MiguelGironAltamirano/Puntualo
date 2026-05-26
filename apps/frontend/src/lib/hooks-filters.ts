'use client';

import { useState, useCallback, useMemo } from 'react';
import type {
  CourseListParams,
  ProfessorListParams,
  CommentListParams,
  EvaluationListParams,
} from '@/lib/api';

// ============================================================================
// TYPES
// ============================================================================

export interface FilterState {
  [key: string]: any;
}

export interface UseFilterReturn<T extends FilterState> {
  filters: T;
  setFilter: (key: keyof T, value: any) => void;
  setFilters: (filters: Partial<T>) => void;
  clearFilter: (key: keyof T) => void;
  clearAllFilters: () => void;
  hasActiveFilters: boolean;
  activeFilterCount: number;
}

// ============================================================================
// GENERIC FILTER HOOK
// ============================================================================

/**
 * Generic hook for managing filter state
 */
export function useFilters<T extends FilterState>(
  initialFilters: T
): UseFilterReturn<T> {
  const [filters, setFiltersState] = useState<T>(initialFilters);

  const setFilter = useCallback(
    (key: keyof T, value: any) => {
      setFiltersState((prev) => ({
        ...prev,
        [key]: value,
      }));
    },
    []
  );

  const setFilters = useCallback((newFilters: Partial<T>) => {
    setFiltersState((prev) => ({
      ...prev,
      ...newFilters,
    }));
  }, []);

  const clearFilter = useCallback((key: keyof T) => {
    setFiltersState((prev) => ({
      ...prev,
      [key]: initialFilters[key],
    }));
  }, [initialFilters]);

  const clearAllFilters = useCallback(() => {
    setFiltersState(initialFilters);
  }, [initialFilters]);

  const hasActiveFilters = useMemo(
    () =>
      Object.entries(filters).some(
        ([key, value]) => value !== initialFilters[key as keyof T]
      ),
    [filters, initialFilters]
  );

  const activeFilterCount = useMemo(
    () =>
      Object.entries(filters).filter(
        ([key, value]) => value !== initialFilters[key as keyof T] && value !== null && value !== undefined
      ).length,
    [filters, initialFilters]
  );

  return {
    filters,
    setFilter,
    setFilters,
    clearFilter,
    clearAllFilters,
    hasActiveFilters,
    activeFilterCount,
  };
}

// ============================================================================
// PROFESSOR FILTER HOOK
// ============================================================================

export interface ProfessorFilterState extends ProfessorListParams {
  search?: string;
  university_id?: number;
  faculty_id?: number;
  min_clarity?: number;
  max_clarity?: number;
  min_easiness?: number;
  max_easiness?: number;
  min_helpfulness?: number;
  max_helpfulness?: number;
  min_punctuality?: number;
  max_punctuality?: number;
  min_global_score?: number;
  max_global_score?: number;
  min_evaluations?: number;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

const INITIAL_PROFESSOR_FILTERS: ProfessorFilterState = {
  search: '',
  university_id: undefined,
  faculty_id: undefined,
  min_clarity: undefined,
  max_clarity: undefined,
  min_easiness: undefined,
  max_easiness: undefined,
  min_helpfulness: undefined,
  max_helpfulness: undefined,
  min_punctuality: undefined,
  max_punctuality: undefined,
  min_global_score: undefined,
  max_global_score: undefined,
  min_evaluations: undefined,
  date_from: undefined,
  date_to: undefined,
  page: 1,
  page_size: 20,
  sort_by: 'full_name',
  sort_order: 'asc',
};

export function useProfessorFilters(): UseFilterReturn<ProfessorFilterState> {
  return useFilters<ProfessorFilterState>(INITIAL_PROFESSOR_FILTERS);
}

// ============================================================================
// COURSE FILTER HOOK
// ============================================================================

export interface CourseFilterState extends CourseListParams {
  q?: string;
  university_id?: number;
  faculty_id?: number;
  page?: number;
  page_size?: number;
  sort_by?: 'name' | 'evaluation_count';
  sort_order?: 'asc' | 'desc';
}

const INITIAL_COURSE_FILTERS: CourseFilterState = {
  q: '',
  university_id: undefined,
  faculty_id: undefined,
  page: 1,
  page_size: 20,
  sort_by: 'name',
  sort_order: 'asc',
};

export function useCourseFilters(): UseFilterReturn<CourseFilterState> {
  return useFilters<CourseFilterState>(INITIAL_COURSE_FILTERS);
}

// ============================================================================
// EVALUATION FILTER HOOK
// ============================================================================

export interface EvaluationFilterState extends EvaluationListParams {
  professor_id?: string;
  course_id?: number;
  semester?: string;
  modality?: 'virtual' | 'presencial' | 'ambas';
  min_clarity?: number;
  max_clarity?: number;
  min_easiness?: number;
  max_easiness?: number;
  min_helpfulness?: number;
  max_helpfulness?: number;
  min_punctuality?: number;
  max_punctuality?: number;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

const INITIAL_EVALUATION_FILTERS: EvaluationFilterState = {
  professor_id: undefined,
  course_id: undefined,
  semester: undefined,
  modality: undefined,
  min_clarity: undefined,
  max_clarity: undefined,
  min_easiness: undefined,
  max_easiness: undefined,
  min_helpfulness: undefined,
  max_helpfulness: undefined,
  min_punctuality: undefined,
  max_punctuality: undefined,
  date_from: undefined,
  date_to: undefined,
  page: 1,
  page_size: 20,
  sort_by: 'created_at',
  sort_order: 'desc',
};

export function useEvaluationFilters(): UseFilterReturn<EvaluationFilterState> {
  return useFilters<EvaluationFilterState>(INITIAL_EVALUATION_FILTERS);
}

// ============================================================================
// COMMENT FILTER HOOK
// ============================================================================

export interface CommentFilterState extends CommentListParams {
  search?: string;
  min_likes?: number;
  max_likes?: number;
  min_dislikes?: number;
  max_dislikes?: number;
  min_net_score?: number;
  date_from?: string;
  date_to?: string;
  course_id?: number;
  modality?: 'virtual' | 'presencial' | 'ambas';
  hashtags?: string[];
  page?: number;
  page_size?: number;
  order_by?: string;
  sort_order?: 'asc' | 'desc';
}

const INITIAL_COMMENT_FILTERS: CommentFilterState = {
  search: '',
  min_likes: undefined,
  max_likes: undefined,
  min_dislikes: undefined,
  max_dislikes: undefined,
  min_net_score: undefined,
  date_from: undefined,
  date_to: undefined,
  course_id: undefined,
  modality: undefined,
  hashtags: [],
  page: 1,
  page_size: 20,
  order_by: 'created_at',
  sort_order: 'desc',
};

export function useCommentFilters(): UseFilterReturn<CommentFilterState> {
  return useFilters<CommentFilterState>(INITIAL_COMMENT_FILTERS);
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Convert filter state to API query parameters (removes undefined/null)
 */
export function filterStateToParams<T extends FilterState>(
  state: T
): Partial<T> {
  const result: Partial<T> = {};

  Object.entries(state).forEach(([key, value]) => {
    if (
      value !== undefined &&
      value !== null &&
      value !== '' &&
      (!Array.isArray(value) || value.length > 0)
    ) {
      result[key as keyof T] = value as any;
    }
  });

  return result;
}

/**
 * Get human-readable label for a filter value
 */
export function getFilterLabel(key: string, value: any): string {
  if (value === undefined || value === null || value === '') {
    return '';
  }

  const labelMap: Record<string, Record<string, string>> = {
    modality: {
      virtual: 'Virtual',
      presencial: 'Presencial',
      ambas: 'Both',
    },
    sort_order: {
      asc: 'Ascending',
      desc: 'Descending',
    },
  };

  if (labelMap[key]) {
    return labelMap[key][value] || String(value);
  }

  return String(value);
}

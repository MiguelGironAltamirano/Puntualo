/**
 * Custom React Hooks for API Data Fetching
 * Provides type-safe data fetching with loading and error states
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  coursesAPI,
  professorsAPI,
  evaluationsAPI,
  commentsAPI,
  CourseRead,
  ProfessorRead,
  EvaluationRead,
  CommentRead,
  PaginatedResponse,
  CourseListParams,
  ProfessorListParams,
  EvaluationListParams,
  CommentListParams,
  ProfessorComparisonResponse,
} from './api';

// ============================================================================
// TYPES
// ============================================================================

export interface UseQueryState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export interface UseListState<T> extends UseQueryState<PaginatedResponse<T>> {
  data: PaginatedResponse<T> | null;
}

// ============================================================================
// CUSTOM HOOKS
// ============================================================================

/**
 * Hook for fetching a paginated list of professors
 */
export function useProfessors(
  params?: ProfessorListParams,
  skip = false
): UseListState<ProfessorRead> {
  const [state, setState] = useState<UseListState<ProfessorRead>>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    if (skip) return;

    const fetchData = async () => {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      try {
        const data = await professorsAPI.list(params);
        setState({ data, loading: false, error: null });
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error : new Error('Unknown error'),
        });
      }
    };

    fetchData();
  }, [params, skip]);

  return state;
}

/**
 * Hook for fetching a single professor by ID
 */
export function useProfessor(
  id: string | null,
  skip = false
): UseQueryState<ProfessorRead> {
  const [state, setState] = useState<UseQueryState<ProfessorRead>>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    if (!id || skip) return;

    const fetchData = async () => {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      try {
        const data = await professorsAPI.get(id);
        setState({ data, loading: false, error: null });
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error : new Error('Unknown error'),
        });
      }
    };

    fetchData();
  }, [id, skip]);

  return state;
}

/**
 * Hook for fetching a paginated list of courses
 */
export function useCourses(
  params?: CourseListParams,
  skip = false
): UseListState<CourseRead> {
  const [state, setState] = useState<UseListState<CourseRead>>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    if (skip) return;

    const fetchData = async () => {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      try {
        const data = await coursesAPI.list(params);
        setState({ data, loading: false, error: null });
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error : new Error('Unknown error'),
        });
      }
    };

    fetchData();
  }, [params, skip]);

  return state;
}

/**
 * Hook for fetching a single course by ID
 */
export function useCourse(
  id: number | null,
  skip = false
): UseQueryState<CourseRead> {
  const [state, setState] = useState<UseQueryState<CourseRead>>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    if (id === null || skip) return;

    const fetchData = async () => {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      try {
        const data = await coursesAPI.get(id);
        setState({ data, loading: false, error: null });
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error : new Error('Unknown error'),
        });
      }
    };

    fetchData();
  }, [id, skip]);

  return state;
}

/**
 * Hook for fetching a paginated list of evaluations
 */
export function useEvaluations(
  params?: EvaluationListParams,
  skip = false
): UseListState<EvaluationRead> {
  const [state, setState] = useState<UseListState<EvaluationRead>>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    if (skip) return;

    const fetchData = async () => {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      try {
        const data = await evaluationsAPI.list(params);
        setState({ data, loading: false, error: null });
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error : new Error('Unknown error'),
        });
      }
    };

    fetchData();
  }, [params, skip]);

  return state;
}

/**
 * Hook for fetching a paginated list of comments for a professor
 */
export function useComments(
  professorId: string | null,
  params?: CommentListParams,
  skip = false
): UseListState<CommentRead> {
  const [state, setState] = useState<UseListState<CommentRead>>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    if (!professorId || skip) return;

    const fetchData = async () => {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      try {
        const data = await commentsAPI.list(professorId, params);
        setState({ data, loading: false, error: null });
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error : new Error('Unknown error'),
        });
      }
    };

    fetchData();
  }, [professorId, params, skip]);

  return state;
}

/**
 * Hook for comparing professors
 */
export function useCompareProfessors(
  professorIds: string[] | null,
  skip = false
): UseQueryState<ProfessorComparisonResponse> {
  const [state, setState] = useState<UseQueryState<ProfessorComparisonResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    if (!professorIds || professorIds.length < 2 || professorIds.length > 4 || skip) {
      return;
    }

    const fetchData = async () => {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      try {
        const data = await professorsAPI.compare(professorIds);
        setState({ data, loading: false, error: null });
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error : new Error('Unknown error'),
        });
      }
    };

    fetchData();
  }, [professorIds, skip]);

  return state;
}

// ============================================================================
// DEBOUNCED HOOKS (for search inputs)
// ============================================================================

/**
 * Hook for searching professors with debouncing
 */
export function useProfessorsSearch(
  searchTerm: string,
  debounceMs = 300,
  options?: Partial<ProfessorListParams>
): UseListState<ProfessorRead> {
  const [debouncedTerm, setDebouncedTerm] = useState(searchTerm);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedTerm(searchTerm);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [searchTerm, debounceMs]);

  const params: ProfessorListParams = {
    search: debouncedTerm,
    page: 1,
    page_size: 20,
    ...options,
  };

  return useProfessors(params, !debouncedTerm);
}

/**
 * Hook for searching courses with debouncing
 */
export function useCoursesSearch(
  searchTerm: string,
  debounceMs = 300,
  options?: Partial<CourseListParams>
): UseListState<CourseRead> {
  const [debouncedTerm, setDebouncedTerm] = useState(searchTerm);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedTerm(searchTerm);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [searchTerm, debounceMs]);

  const params: CourseListParams = {
    q: debouncedTerm,
    page: 1,
    page_size: 20,
    ...options,
  };

  return useCourses(params, !debouncedTerm);
}

/**
 * Hook for searching comments with debouncing
 */
export function useCommentsSearch(
  professorId: string | null,
  searchTerm: string,
  debounceMs = 300,
  options?: Partial<CommentListParams>
): UseListState<CommentRead> {
  const [debouncedTerm, setDebouncedTerm] = useState(searchTerm);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedTerm(searchTerm);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [searchTerm, debounceMs]);

  const params: CommentListParams = {
    search: debouncedTerm,
    page: 1,
    page_size: 20,
    ...options,
  };

  return useComments(professorId, params, !debouncedTerm || !professorId);
}

// ============================================================================
// IMPERATIVE HOOKS (for manual refetching)
// ============================================================================

/**
 * Hook that returns a function to manually fetch data
 * Useful for imperative patterns like form submissions
 */
export function useLazyProfessors() {
  const [state, setState] = useState<UseListState<ProfessorRead>>({
    data: null,
    loading: false,
    error: null,
  });

  const fetch = useCallback(async (params?: ProfessorListParams) => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await professorsAPI.list(params);
      setState({ data, loading: false, error: null });
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error instanceof Error ? error : new Error('Unknown error'),
      });
    }
  }, []);

  return { ...state, fetch };
}

/**
 * Hook that returns a function to manually fetch data for courses
 */
export function useLazyCourses() {
  const [state, setState] = useState<UseListState<CourseRead>>({
    data: null,
    loading: false,
    error: null,
  });

  const fetch = useCallback(async (params?: CourseListParams) => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await coursesAPI.list(params);
      setState({ data, loading: false, error: null });
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error instanceof Error ? error : new Error('Unknown error'),
      });
    }
  }, []);

  return { ...state, fetch };
}

/**
 * Hook that returns a function to manually fetch comparison data
 */
export function useLazyCompareProfessors() {
  const [state, setState] = useState<UseQueryState<ProfessorComparisonResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const fetch = useCallback(async (professorIds: string[]) => {
    if (professorIds.length < 2 || professorIds.length > 4) {
      setState({
        data: null,
        loading: false,
        error: new Error('Must provide between 2 and 4 professor IDs'),
      });
      return;
    }

    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await professorsAPI.compare(professorIds);
      setState({ data, loading: false, error: null });
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error instanceof Error ? error : new Error('Unknown error'),
      });
    }
  }, []);

  return { ...state, fetch };
}

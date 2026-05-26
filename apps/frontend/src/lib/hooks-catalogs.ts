'use client'

import { useState, useEffect } from 'react'
import { catalogsAPI, UniversityRead, FacultyRead, CourseRead, PaginatedResponse } from './api'

/**
 * State interface for data fetching hooks
 */
interface UseQueryState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

/**
 * Hook to fetch list of universities
 * Runs once on component mount
 */
export function useUniversities(): UseQueryState<UniversityRead[]> {
  const [state, setState] = useState<UseQueryState<UniversityRead[]>>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setState((prev) => ({ ...prev, loading: true, error: null }));
        const data = await catalogsAPI.listUniversities();
        setState({ data, loading: false, error: null });
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error : new Error('Failed to fetch universities'),
        });
      }
    };

    fetchData();
  }, []);

  return state;
}

/**
 * Hook to fetch faculties for a specific university
 * Re-fetches when universityId changes
 */
export function useFaculties(universityId: number | null): UseQueryState<FacultyRead[]> {
  const [state, setState] = useState<UseQueryState<FacultyRead[]>>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    if (!universityId || universityId <= 0) {
      setState({ data: null, loading: false, error: null });
      return;
    }

    const fetchData = async () => {
      try {
        setState((prev) => ({ ...prev, loading: true, error: null }));
        const data = await catalogsAPI.listFaculties(universityId);
        setState({ data, loading: false, error: null });
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error : new Error('Failed to fetch faculties'),
        });
      }
    };

    fetchData();
  }, [universityId]);

  return state;
}

/**
 * Hook to fetch courses for a specific faculty
 * Re-fetches when facultyId changes
 */
export function useCourses(facultyId: number | null): UseQueryState<PaginatedResponse<CourseRead>> {
  const [state, setState] = useState<UseQueryState<PaginatedResponse<CourseRead>>>({
    data: null,
    loading: false,
    error: null,
  });

  useEffect(() => {
    if (!facultyId || facultyId <= 0) {
      setState({ data: null, loading: false, error: null });
      return;
    }

    const fetchData = async () => {
      try {
        setState((prev) => ({ ...prev, loading: true, error: null }));
        const data = await catalogsAPI.listCourses({
          faculty_id: facultyId,
          page: 1,
          page_size: 50,
        });
        setState({ data, loading: false, error: null });
      } catch (error) {
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error : new Error('Failed to fetch courses'),
        });
      }
    };

    fetchData();
  }, [facultyId]);

  return state;
}

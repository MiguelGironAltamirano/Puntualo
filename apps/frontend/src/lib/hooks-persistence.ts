'use client';

import { useSearchParams, useRouter, usePathname } from 'next/navigation';
import { useEffect, useCallback, useState } from 'react';
import type { FilterState } from './hooks-filters';

// ============================================================================
// URL FILTER PERSISTENCE HOOK
// ============================================================================

/**
 * Hook to sync filter state with URL query parameters
 * Supports browser history (back/forward buttons)
 */
export function useURLFilters<T extends FilterState>(
  initialFilters: T,
  updateFilters: (filters: Partial<T>) => void
) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize filters from URL on mount
  useEffect(() => {
    if (isInitialized) return;

    const urlFilters: Partial<T> = {};
    
    searchParams.forEach((value, key) => {
      try {
        // Try to parse as JSON first (for complex types)
        (urlFilters as any)[key] = JSON.parse(value);
      } catch {
        // Fall back to string or number conversion
        const numValue = Number(value);
        (urlFilters as any)[key] = isNaN(numValue) ? value : numValue;
      }
    });

    if (Object.keys(urlFilters).length > 0) {
      updateFilters(urlFilters);
    }

    setIsInitialized(true);
  }, [searchParams, updateFilters, isInitialized]);

  // Update URL when filters change
  const persistFilters = useCallback(
    (filters: T) => {
      const params = new URLSearchParams();

      Object.entries(filters).forEach(([key, value]) => {
        if (
          value !== undefined &&
          value !== null &&
          value !== '' &&
          (!Array.isArray(value) || value.length > 0)
        ) {
          // Store arrays and objects as JSON
          if (typeof value === 'object') {
            params.set(key, JSON.stringify(value));
          } else {
            params.set(key, String(value));
          }
        }
      });

      const query = params.toString();
      const url = query ? `${pathname}?${query}` : pathname;
      router.push(url, { scroll: false });
    },
    [router, pathname]
  );

  return { persistFilters, isInitialized };
}

// ============================================================================
// SESSION STORAGE FILTERS HOOK
// ============================================================================

/**
 * Hook to persist filters in sessionStorage (survives page refresh but not browser close)
 */
export function useSessionFilters<T extends FilterState>(
  key: string,
  initialFilters: T
) {
  const [isLoaded, setIsLoaded] = useState(false);

  // Load from session storage on mount
  useEffect(() => {
    try {
      const stored = sessionStorage.getItem(key);
      if (stored) {
        const filters = JSON.parse(stored);
        // Initialize with stored filters
      }
    } catch (error) {
      console.error('Failed to load filters from sessionStorage:', error);
    }
    setIsLoaded(true);
  }, [key]);

  // Save to session storage
  const saveFilters = useCallback(
    (filters: T) => {
      try {
        sessionStorage.setItem(key, JSON.stringify(filters));
      } catch (error) {
        console.error('Failed to save filters to sessionStorage:', error);
      }
    },
    [key]
  );

  const clearFilters = useCallback(() => {
    try {
      sessionStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to clear filters from sessionStorage:', error);
    }
  }, [key]);

  return { saveFilters, clearFilters, isLoaded };
}

// ============================================================================
// LOCAL STORAGE FILTERS HOOK
// ============================================================================

/**
 * Hook to persist filters in localStorage (survives browser close)
 */
export function useLocalFilters<T extends FilterState>(
  key: string,
  initialFilters: T
) {
  const [filters, setFilters] = useState<T>(initialFilters);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load from local storage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(key);
      if (stored) {
        const loadedFilters = JSON.parse(stored);
        setFilters(loadedFilters);
      }
    } catch (error) {
      console.error('Failed to load filters from localStorage:', error);
    }
    setIsLoaded(true);
  }, [key]);

  // Save to local storage when filters change
  const saveFilters = useCallback(
    (newFilters: T) => {
      try {
        setFilters(newFilters);
        localStorage.setItem(key, JSON.stringify(newFilters));
      } catch (error) {
        console.error('Failed to save filters to localStorage:', error);
      }
    },
    [key]
  );

  const clearFilters = useCallback(() => {
    try {
      setFilters(initialFilters);
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to clear filters from localStorage:', error);
    }
  }, [initialFilters, key]);

  return { filters, saveFilters, clearFilters, isLoaded };
}

// ============================================================================
// COMBINED PERSISTENCE HOOK (URL + LOCAL STORAGE)
// ============================================================================

/**
 * Hook that combines URL parameters and localStorage
 * URL takes precedence over localStorage
 */
export function usePersistedFilters<T extends FilterState>(
  initialFilters: T,
  options: {
    useURL?: boolean;
    useLocalStorage?: boolean;
    storageKey?: string;
  } = {}
) {
  const {
    useURL = true,
    useLocalStorage = true,
    storageKey = 'filters',
  } = options;

  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const [filters, setFilters] = useState<T>(initialFilters);
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize filters from URL and localStorage
  useEffect(() => {
    if (isInitialized) return;

    let loadedFilters: Partial<T> = {};

    // Load from localStorage first
    if (useLocalStorage) {
      try {
        const stored = localStorage.getItem(storageKey);
        if (stored) {
          loadedFilters = JSON.parse(stored);
        }
      } catch (error) {
        console.error('Failed to load from localStorage:', error);
      }
    }

    // Override with URL parameters (URL takes precedence)
    if (useURL) {
      const urlFilters: Partial<T> = {};
      searchParams.forEach((value, key) => {
        try {
          (urlFilters as any)[key] = JSON.parse(value);
        } catch {
          const numValue = Number(value);
          (urlFilters as any)[key] = isNaN(numValue) ? value : numValue;
        }
      });
      loadedFilters = { ...loadedFilters, ...urlFilters };
    }

    if (Object.keys(loadedFilters).length > 0) {
      setFilters((prev) => ({ ...prev, ...loadedFilters }));
    }

    setIsInitialized(true);
  }, [searchParams, useURL, useLocalStorage, storageKey, isInitialized]);

  // Persist filters to both URL and localStorage
  const persistFilters = useCallback(
    (newFilters: T) => {
      setFilters(newFilters);

      // Save to localStorage
      if (useLocalStorage) {
        try {
          localStorage.setItem(storageKey, JSON.stringify(newFilters));
        } catch (error) {
          console.error('Failed to save to localStorage:', error);
        }
      }

      // Update URL
      if (useURL) {
        const params = new URLSearchParams();
        Object.entries(newFilters).forEach(([key, value]) => {
          if (
            value !== undefined &&
            value !== null &&
            value !== '' &&
            (!Array.isArray(value) || value.length > 0)
          ) {
            if (typeof value === 'object') {
              params.set(key, JSON.stringify(value));
            } else {
              params.set(key, String(value));
            }
          }
        });

        const query = params.toString();
        const url = query ? `${pathname}?${query}` : pathname;
        router.push(url, { scroll: false });
      }
    },
    [useURL, useLocalStorage, storageKey, router, pathname]
  );

  const clearAll = useCallback(() => {
    setFilters(initialFilters);

    if (useLocalStorage) {
      try {
        localStorage.removeItem(storageKey);
      } catch (error) {
        console.error('Failed to clear localStorage:', error);
      }
    }

    if (useURL) {
      router.push(pathname, { scroll: false });
    }
  }, [useURL, useLocalStorage, storageKey, initialFilters, router, pathname]);

  return {
    filters,
    persistFilters,
    clearAll,
    isInitialized,
  };
}

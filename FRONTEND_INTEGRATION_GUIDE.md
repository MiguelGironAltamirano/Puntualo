# Frontend Integration Guide - Search, Compare & Filters

Complete integration guide for connecting your frontend to the new search, filtering, and comparison API endpoints.

---

## Table of Contents

1. [Setup](#setup)
2. [Core Concepts](#core-concepts)
3. [API Client Usage](#api-client-usage)
4. [Custom Hooks](#custom-hooks)
5. [Filter Components](#filter-components)
6. [Integration Examples](#integration-examples)
7. [URL Persistence](#url-persistence)
8. [Error Handling](#error-handling)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

---

## Setup

### 1. Environment Configuration

Create a `.env.local` file in `apps/frontend`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, update to your production backend URL.

### 2. Verify API Client

The API client is located at `src/lib/api.ts` and exports:
- Type definitions for all data models
- API endpoint functions grouped by resource
- Helper functions for common patterns

---

## Core Concepts

### API Types

All API data is typed with TypeScript. Key types include:

```typescript
// From src/lib/api.ts
PaginatedResponse<T>        // Standard paginated response
CourseRead                  // Course data model
ProfessorRead              // Professor data model
EvaluationRead             // Evaluation data model
CommentRead                // Comment data model
ProfessorComparisonResponse // Comparison response
```

### Filter State

Filters are managed with dedicated hooks and hooks-filters:

```typescript
// From src/lib/hooks-filters.ts
useProfessorFilters()      // Hook for professor filter state
useCourseFilters()         // Hook for course filter state
useEvaluationFilters()     // Hook for evaluation filter state
useCommentFilters()        // Hook for comment filter state
```

### Data Fetching

Use custom hooks for automatic loading/error handling:

```typescript
// From src/lib/hooks.ts
useProfessors()           // Fetch professor list
useCourses()              // Fetch course list
useEvaluations()          // Fetch evaluation list
useComments()             // Fetch comments for a professor
useCompareProfessors()    // Compare 2-4 professors
```

---

## API Client Usage

### Basic Example

```typescript
import { professorsAPI, coursesAPI } from '@/lib/api';

// Search professors
const professors = await professorsAPI.list({
  search: 'Juan',
  min_clarity: 4,
  page: 1,
  page_size: 20,
});

// Search courses
const courses = await coursesAPI.list({
  q: 'mathematics',
  sort_by: 'evaluation_count',
  sort_order: 'desc',
});
```

### Courses API

```typescript
// List courses with filters
const response = await coursesAPI.list({
  q: 'search term',              // Fuzzy search
  university_id: 1,              // Filter by university
  faculty_id: 2,                 // Filter by faculty
  page: 1,                        // Page number (1-indexed)
  page_size: 20,                 // Items per page (1-50)
  sort_by: 'evaluation_count',   // 'name' or 'evaluation_count'
  sort_order: 'desc',            // 'asc' or 'desc'
});

// Get single course
const course = await coursesAPI.get(1);
```

### Professors API

```typescript
// List professors with advanced filters
const response = await professorsAPI.list({
  search: 'name',                   // Search by name
  university_id: 1,                 // Filter by university
  faculty_id: 2,                    // Filter by faculty
  min_clarity: 3,                   // Score range (1-5)
  max_clarity: 5,
  min_easiness: 2,
  max_easiness: 4,
  min_helpfulness: 3,
  max_helpfulness: 5,
  min_punctuality: 3,
  max_punctuality: 5,
  min_global_score: 4.0,            // Global score range (float)
  max_global_score: 5.0,
  min_evaluations: 5,               // Minimum number of evaluations
  date_from: '2024-01-01',          // ISO date format
  date_to: '2024-12-31',
  page: 1,
  page_size: 20,
  sort_by: 'global_score',
  sort_order: 'desc',
});

// Compare professors (2-4 only)
const comparison = await professorsAPI.compare([
  'uuid-1',
  'uuid-2',
]);
```

### Evaluations API

```typescript
// List evaluations with filters
const response = await evaluationsAPI.list({
  professor_id: 'uuid',             // Filter by professor
  course_id: 1,                      // Filter by course
  semester: '2024-1',                // Filter by semester
  modality: 'presencial',            // 'virtual', 'presencial', 'ambas'
  min_clarity: 4,                    // Score ranges (1-5)
  max_clarity: 5,
  // ... other score ranges
  date_from: '2024-01-01',
  date_to: '2024-12-31',
  page: 1,
  page_size: 20,
  sort_by: 'clarity',                // Any score field or 'created_at'
  sort_order: 'desc',
});
```

### Comments API

```typescript
// List comments for a professor
const response = await commentsAPI.list('professor-uuid', {
  search: 'excellent',              // Full-text search
  min_likes: 5,                      // Reaction count range
  max_likes: 100,
  min_dislikes: 0,
  max_dislikes: 10,
  min_net_score: 2,                  // likes - dislikes
  date_from: '2024-01-01',
  date_to: '2024-12-31',
  course_id: 1,                      // Filter by course
  modality: 'virtual',               // Filter by modality
  hashtags: ['clear', 'helpful'],    // Filter by tags
  page: 1,
  page_size: 20,
  order_by: 'likes',                 // Sort field
  sort_order: 'desc',
});
```

---

## Custom Hooks

### Fetch Hooks

```typescript
import {
  useProfessors,
  useCourses,
  useEvaluations,
  useComments,
  useCompareProfessors,
} from '@/lib/hooks';

export function MyComponent() {
  // Fetch professors with filters
  const { data, loading, error } = useProfessors({
    search: 'juan',
    min_clarity: 4,
    page: 1,
    page_size: 20,
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {data?.items.map((prof) => (
        <li key={prof.id}>{prof.full_name}</li>
      ))}
    </ul>
  );
}
```

### Search Hooks (with Debouncing)

```typescript
import {
  useProfessorsSearch,
  useCoursesSearch,
  useCommentsSearch,
} from '@/lib/hooks';

export function SearchExample() {
  const [searchTerm, setSearchTerm] = React.useState('');

  // Automatically debounced (300ms by default)
  const { data, loading } = useProfessorsSearch(searchTerm);

  return (
    <>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search professors..."
      />
      {loading && <div>Searching...</div>}
      {data?.items.map((prof) => (
        <div key={prof.id}>{prof.full_name}</div>
      ))}
    </>
  );
}
```

### Lazy Hooks (Imperative)

```typescript
import {
  useLazyProfessors,
  useLazyCourses,
  useLazyCompareProfessors,
} from '@/lib/hooks';

export function LazyExample() {
  const { data, loading, error, fetch } = useLazyProfessors();

  const handleSearch = async () => {
    await fetch({ search: 'juan', page: 1, page_size: 20 });
  };

  return (
    <>
      <button onClick={handleSearch}>Search</button>
      {loading && <div>Loading...</div>}
      {error && <div>Error: {error.message}</div>}
      {data?.items.map((prof) => (
        <div key={prof.id}>{prof.full_name}</div>
      ))}
    </>
  );
}
```

---

## Filter Components

### Basic Filter Components

```typescript
import {
  SearchFilter,
  ScoreRangeFilter,
  DateRangeFilter,
  SelectFilter,
  CheckboxFilter,
} from '@/components/filters/FilterComponents';

export function MyFilters() {
  const [search, setSearch] = React.useState('');
  const [minScore, setMinScore] = React.useState<number>();
  const [maxScore, setMaxScore] = React.useState<number>();

  return (
    <>
      <SearchFilter
        placeholder="Search professors..."
        value={search}
        onChange={setSearch}
      />

      <ScoreRangeFilter
        label="Clarity Rating"
        minScore={minScore}
        maxScore={maxScore}
        onMinChange={setMinScore}
        onMaxChange={setMaxScore}
      />

      <DateRangeFilter
        label="Date Range"
        dateFrom={dateFrom}
        dateTo={dateTo}
        onDateFromChange={setDateFrom}
        onDateToChange={setDateTo}
      />
    </>
  );
}
```

### Enhanced Filter Sidebar

```typescript
import { EnhancedFilterSidebar } from '@/components/filters/EnhancedFilterSidebar';

export function MyPage() {
  const handleFiltersChange = (filters) => {
    console.log('Filters changed:', filters);
    // Fetch data with new filters
  };

  return (
    <div className="flex">
      <EnhancedFilterSidebar
        onFiltersChange={handleFiltersChange}
        universities={[
          { id: 1, name: 'Universidad Nacional' },
          { id: 2, name: 'Universidad Privada' },
        ]}
        faculties={[
          { id: 1, name: 'Ingeniería' },
          { id: 2, name: 'Medicina' },
        ]}
      />
      {/* Content area */}
    </div>
  );
}
```

---

## Integration Examples

### Complete Teachers List Page

```typescript
'use client';

import React, { useState, useCallback } from 'react';
import { useProfessors } from '@/lib/hooks';
import { useProfessorFilters } from '@/lib/hooks-filters';
import { EnhancedFilterSidebar } from '@/components/filters/EnhancedFilterSidebar';
import { Pagination } from '@/components/pagination/Pagination';
import { SkeletonList, ErrorState } from '@/components/loaders/SkeletonLoaders';

export default function TeachersPage() {
  const { filters, setFilters, clearAllFilters } = useProfessorFilters();
  const { data, loading, error } = useProfessors(filters);

  const handleFilterChange = useCallback(
    (newFilters) => {
      setFilters({ ...newFilters, page: 1 }); // Reset to page 1
    },
    [setFilters]
  );

  const handlePageChange = useCallback(
    (page) => {
      setFilters({ ...filters, page });
    },
    [filters, setFilters]
  );

  return (
    <div className="flex">
      <EnhancedFilterSidebar onFiltersChange={handleFilterChange} />

      <div className="flex-1">
        {loading && <SkeletonList count={10} />}

        {error && <ErrorState error={error} onRetry={() => {}} />}

        {data && (
          <>
            <div className="grid gap-4">
              {data.items.map((professor) => (
                <div key={professor.id} className="border rounded p-4">
                  <h3 className="font-bold">{professor.full_name}</h3>
                  <p>Rating: {professor.global_score?.toFixed(1)}</p>
                  <p>{professor.total_evaluations} evaluations</p>
                </div>
              ))}
            </div>

            {data.total_pages > 1 && (
              <Pagination
                currentPage={data.page}
                totalPages={data.total_pages}
                hasNext={data.has_next}
                hasPrev={data.has_prev}
                onPageChange={handlePageChange}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}
```

### Comparison Page

```typescript
'use client';

import React, { useState } from 'react';
import { useCompareProfessors } from '@/lib/hooks';

export default function ComparePage() {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const { data, loading, error } = useCompareProfessors(
    selectedIds.length >= 2 && selectedIds.length <= 4 ? selectedIds : null
  );

  return (
    <div>
      <h1>Compare Professors</h1>

      {/* Professor selector */}
      <div className="mb-8">
        <label>Select 2-4 professors to compare:</label>
        {/* Implement professor multi-select here */}
      </div>

      {loading && <div>Loading comparison...</div>}
      {error && <div>Error: {error.message}</div>}

      {data && (
        <div className="grid grid-cols-auto gap-6">
          {data.professors.map((prof) => (
            <div key={prof.id} className="border rounded p-4">
              <h3 className="font-bold text-lg">{prof.full_name}</h3>

              <div className="grid grid-cols-2 gap-2 mt-4">
                <div>
                  <p className="text-sm text-gray-600">Clarity</p>
                  <p className="font-bold">{prof.avg_clarity.toFixed(1)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Easiness</p>
                  <p className="font-bold">{prof.avg_easiness.toFixed(1)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Helpfulness</p>
                  <p className="font-bold">{prof.avg_helpfulness.toFixed(1)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Punctuality</p>
                  <p className="font-bold">{prof.avg_punctuality.toFixed(1)}</p>
                </div>
              </div>

              <div className="mt-4">
                <h4 className="font-semibold">Common Courses:</h4>
                <ul className="mt-2">
                  {prof.common_courses.map((course) => (
                    <li key={course.id} className="text-sm">
                      {course.name}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}

      {data?.comparison_metrics && (
        <div className="mt-8">
          <h2>Comparison Highlights</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="border rounded p-4">
              <p className="text-sm text-gray-600">Best Clarity</p>
              <p className="font-bold">
                {data.comparison_metrics.best_clarity.professor_name}
              </p>
              <p className="text-sm">
                {data.comparison_metrics.best_clarity.score}
              </p>
            </div>
            {/* More metrics */}
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## URL Persistence

### Using usePersistedFilters Hook

```typescript
import { usePersistedFilters } from '@/lib/hooks-persistence';
import { useProfessorFilters } from '@/lib/hooks-filters';

export function PersistentFilterExample() {
  const initialFilters = useProfessorFilters();
  const { filters, persistFilters, isInitialized } = usePersistedFilters(
    initialFilters.filters,
    {
      useURL: true,           // Sync with URL query params
      useLocalStorage: true,  // Also save to localStorage
      storageKey: 'professorFilters',
    }
  );

  if (!isInitialized) return <div>Loading...</div>;

  return (
    <div>
      {/* URL will update with filter changes */}
      {/* Query params: ?search=juan&min_clarity=4&page=2 */}
    </div>
  );
}
```

---

## Error Handling

### Error Boundary

```typescript
import { ErrorBoundary } from '@/lib/error-handling';

export function MyPage() {
  return (
    <ErrorBoundary
      fallback={(error, reset) => (
        <div>
          <h1>Something went wrong</h1>
          <p>{error.message}</p>
          <button onClick={reset}>Try Again</button>
        </div>
      )}
    >
      <TeachersContent />
    </ErrorBoundary>
  );
}
```

### Retry Logic

```typescript
import { retryAsync } from '@/lib/error-handling';

async function fetchWithRetry() {
  try {
    const result = await retryAsync(
      () => professorsAPI.list({ search: 'juan' }),
      {
        maxRetries: 3,
        delayMs: 1000,
        backoffMultiplier: 2,
        onRetry: (attempt, error) => {
          console.log(`Retry attempt ${attempt}:`, error.message);
        },
      }
    );
    return result;
  } catch (error) {
    console.error('Failed after all retries:', error);
  }
}
```

---

## Testing

### Unit Test Example

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { useProfessors } from '@/lib/hooks';
import { professorsAPI } from '@/lib/api';

jest.mock('@/lib/api');

describe('useProfessors', () => {
  it('should fetch professors on mount', async () => {
    const mockData = {
      items: [{ id: '1', full_name: 'Dr. Juan' }],
      total: 1,
      page: 1,
      page_size: 20,
      total_pages: 1,
      has_next: false,
      has_prev: false,
    };

    (professorsAPI.list as jest.Mock).mockResolvedValue(mockData);

    const { result } = renderHook(() => useProfessors());

    await waitFor(() => {
      expect(result.current.data).toEqual(mockData);
    });
  });
});
```

---

## Troubleshooting

### Common Issues

1. **"API_URL is undefined"**
   - Ensure `NEXT_PUBLIC_API_URL` is set in `.env.local`
   - Restart dev server after changing env variables

2. **"404 Not Found" on requests**
   - Check backend is running on the correct port
   - Verify endpoint paths in API client match backend routes
   - Check professor UUIDs are valid format

3. **"Filters not persisting"**
   - Check if usePersistedFilters hook is properly configured
   - Verify browser localStorage is enabled
   - Check URL is being updated in browser address bar

4. **"Loading state never resolves"**
   - Check network tab in browser DevTools
   - Verify API response includes `total_pages` and pagination fields
   - Check for console errors

5. **"Results not updating after filter change"**
   - Ensure `page` is reset to 1 when filters change
   - Check that filter values are properly passed to hooks
   - Verify filters aren't being cleared unintentionally

---

## Next Steps

1. ✅ Backend API endpoints completed
2. ✅ Frontend API client created
3. ✅ React hooks built
4. ✅ Filter components ready
5. **→ Integrate with your pages**
6. **→ Test all filter combinations**
7. **→ Deploy to production**

---

For more details on specific endpoints, refer to `IMPLEMENTATION_GUIDE.md` and `TESTING_GUIDE.md` in the project root.

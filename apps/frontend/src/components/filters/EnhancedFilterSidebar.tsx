'use client';

import { useState, useCallback, useEffect } from 'react';
import {
  useProfessorFilters,
  filterStateToParams,
  ProfessorFilterState,
} from '@/lib/hooks-filters';
import {
  SearchFilter,
  ScoreRangeFilter,
  DateRangeFilter,
  SelectFilter,
  CheckboxFilter,
  FilterSection,
  ClearFiltersButton,
  FilterSidebarContainer,
} from './FilterComponents';

interface EnhancedFilterSidebarProps {
  onFiltersChange?: (filters: Partial<ProfessorFilterState>) => void;
  universities?: Array<{ id: number; name: string }>;
  faculties?: Array<{ id: number; name: string }>;
}

export function EnhancedFilterSidebar({
  onFiltersChange,
  universities = [],
  faculties = [],
}: EnhancedFilterSidebarProps) {
  const {
    filters,
    setFilter,
    setFilters,
    clearAllFilters,
    hasActiveFilters,
    activeFilterCount,
  } = useProfessorFilters();

  // Notify parent component when filters change
  useEffect(() => {
    if (onFiltersChange) {
      const params = filterStateToParams(filters);
      onFiltersChange(params as Partial<ProfessorFilterState>);
    }
  }, [filters, onFiltersChange]);

  const handleRangeChange = useCallback(
    (minKey: keyof ProfessorFilterState, maxKey: keyof ProfessorFilterState) =>
      (min: number | undefined, max: number | undefined) => {
        setFilters({
          [minKey]: min,
          [maxKey]: max,
        } as any);
      },
    [setFilters]
  );

  const handleDateChange = useCallback(
    (fromKey: keyof ProfessorFilterState, toKey: keyof ProfessorFilterState) =>
      (from: string | undefined, to: string | undefined) => {
        setFilters({
          [fromKey]: from,
          [toKey]: to,
        } as any);
      },
    [setFilters]
  );

  const modalityOptions = [
    { value: 'presencial', label: 'Presencial' },
    { value: 'virtual', label: 'Virtual' },
    { value: 'ambas', label: 'Both' },
  ];

  const sortOptions = [
    { value: 'full_name', label: 'Name (A-Z)' },
    { value: 'global_score', label: 'Rating (High to Low)' },
    { value: 'total_evaluations', label: 'Most Evaluated' },
  ];

  return (
    <FilterSidebarContainer
      title="Smart Search"
      subtitle="Refine your results"
      onClear={clearAllFilters}
    >
      {/* Active filters count */}
      {hasActiveFilters && (
        <div className="mb-4 p-3 bg-sky-50 border border-sky-200 rounded-lg">
          <p className="text-xs font-semibold text-sky-700">
            {activeFilterCount} active filter{activeFilterCount !== 1 ? 's' : ''}
          </p>
        </div>
      )}

      {/* Search Section */}
      <FilterSection title="Search">
        <SearchFilter
          placeholder="Professor name..."
          value={filters.search || ''}
          onChange={(value) => {
            setFilter('search', value);
            setFilter('page', 1); // Reset to page 1 on search
          }}
        />
      </FilterSection>

      {/* Institution Section */}
      {(universities.length > 0 || faculties.length > 0) && (
        <FilterSection title="Institution">
          {universities.length > 0 && (
            <SelectFilter
              label="University"
              options={universities.map((u) => ({
                value: u.id,
                label: u.name,
              }))}
              value={filters.university_id || null}
              onChange={(value) => {
                setFilter('university_id', value);
                setFilter('page', 1);
              }}
              placeholder="Select university"
            />
          )}

          {faculties.length > 0 && (
            <SelectFilter
              label="Faculty"
              options={faculties.map((f) => ({
                value: f.id,
                label: f.name,
              }))}
              value={filters.faculty_id || null}
              onChange={(value) => {
                setFilter('faculty_id', value);
                setFilter('page', 1);
              }}
              placeholder="Select faculty"
            />
          )}
        </FilterSection>
      )}

      {/* Score Filters Section */}
      <FilterSection title="Score Ranges">
        <ScoreRangeFilter
          label="Clarity"
          minScore={filters.min_clarity}
          maxScore={filters.max_clarity}
          onMinChange={(value) => setFilter('min_clarity', value)}
          onMaxChange={(value) => setFilter('max_clarity', value)}
        />

        <ScoreRangeFilter
          label="Easiness"
          minScore={filters.min_easiness}
          maxScore={filters.max_easiness}
          onMinChange={(value) => setFilter('min_easiness', value)}
          onMaxChange={(value) => setFilter('max_easiness', value)}
        />

        <ScoreRangeFilter
          label="Helpfulness"
          minScore={filters.min_helpfulness}
          maxScore={filters.max_helpfulness}
          onMinChange={(value) => setFilter('min_helpfulness', value)}
          onMaxChange={(value) => setFilter('max_helpfulness', value)}
        />

        <ScoreRangeFilter
          label="Punctuality"
          minScore={filters.min_punctuality}
          maxScore={filters.max_punctuality}
          onMinChange={(value) => setFilter('min_punctuality', value)}
          onMaxChange={(value) => setFilter('max_punctuality', value)}
        />

        <ScoreRangeFilter
          label="Global Score"
          minScore={
            filters.min_global_score !== undefined
              ? Math.round(filters.min_global_score * 10) / 10
              : undefined
          }
          maxScore={
            filters.max_global_score !== undefined
              ? Math.round(filters.max_global_score * 10) / 10
              : undefined
          }
          onMinChange={(value) =>
            setFilter('min_global_score', value ? Math.round(value * 10) / 10 : undefined)
          }
          onMaxChange={(value) =>
            setFilter('max_global_score', value ? Math.round(value * 10) / 10 : undefined)
          }
        />
      </FilterSection>

      {/* Evaluation Section */}
      <FilterSection title="Evaluations">
        <div className="mb-5">
          <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-2">
            Minimum Evaluations
          </label>
          <input
            type="number"
            min="0"
            value={filters.min_evaluations || ''}
            onChange={(e) =>
              setFilter(
                'min_evaluations',
                e.target.value ? Number(e.target.value) : undefined
              )
            }
            placeholder="At least..."
            className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-400 shadow-sm"
          />
        </div>
      </FilterSection>

      {/* Date Range Section */}
      <FilterSection title="Date Range">
        <DateRangeFilter
          label="Created Between"
          dateFrom={filters.date_from}
          dateTo={filters.date_to}
          onDateFromChange={(value) => {
            setFilter('date_from', value);
            setFilter('page', 1);
          }}
          onDateToChange={(value) => {
            setFilter('date_to', value);
            setFilter('page', 1);
          }}
        />
      </FilterSection>

      {/* Sorting Section */}
      <FilterSection title="Sort">
        <SelectFilter
          label="Sort By"
          options={sortOptions}
          value={filters.sort_by || 'full_name'}
          onChange={(value) => {
            setFilter('sort_by', value);
            setFilter('page', 1);
          }}
        />

        <CheckboxFilter
          label="Order"
          options={[
            { value: 'asc', label: 'Ascending' },
            { value: 'desc', label: 'Descending' },
          ]}
          selectedValues={filters.sort_order ? [filters.sort_order] : ['asc']}
          onChange={(values) => {
            setFilter('sort_order', values[0] || 'asc');
            setFilter('page', 1);
          }}
        />
      </FilterSection>

      {/* Pagination Size Section */}
      <FilterSection title="Results Per Page">
        <SelectFilter
          label="Page Size"
          options={[
            { value: 10, label: '10 items' },
            { value: 20, label: '20 items' },
            { value: 50, label: '50 items' },
          ]}
          value={filters.page_size || 20}
          onChange={(value) => {
            setFilter('page_size', value);
            setFilter('page', 1);
          }}
        />
      </FilterSection>
    </FilterSidebarContainer>
  );
}

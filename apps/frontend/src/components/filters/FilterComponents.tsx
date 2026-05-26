'use client';

import { useState, useCallback } from 'react';
import { ChevronDown, X } from 'lucide-react';

// ============================================================================
// TYPES
// ============================================================================

export interface FilterState {
  [key: string]: any;
}

export interface RangeFilterProps {
  label: string;
  min: number;
  max: number;
  step?: number;
  value: [number, number];
  onChange: (value: [number, number]) => void;
  minLabel?: string;
  maxLabel?: string;
}

export interface SelectFilterProps {
  label: string;
  options: Array<{ value: string | number; label: string }>;
  value: string | number | null;
  onChange: (value: string | number | null) => void;
  placeholder?: string;
  multiple?: boolean;
  selectedValues?: (string | number)[];
  onChangeMultiple?: (values: (string | number)[]) => void;
}

export interface CheckboxFilterProps {
  label: string;
  options: Array<{ value: string; label: string }>;
  selectedValues: string[];
  onChange: (values: string[]) => void;
}

export interface ScoreRangeFilterProps {
  label: string;
  minScore?: number;
  maxScore?: number;
  onMinChange: (value: number | undefined) => void;
  onMaxChange: (value: number | undefined) => void;
}

export interface DateRangeFilterProps {
  label: string;
  dateFrom?: string;
  dateTo?: string;
  onDateFromChange: (value: string | undefined) => void;
  onDateToChange: (value: string | undefined) => void;
}

export interface SearchFilterProps {
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  debounceMs?: number;
}

// ============================================================================
// RANGE SLIDER COMPONENT
// ============================================================================

export function RangeFilter({
  label,
  min,
  max,
  step = 1,
  value,
  onChange,
  minLabel = 'Min',
  maxLabel = 'Max',
}: RangeFilterProps) {
  return (
    <div className="mb-6">
      <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-3">
        {label}
      </label>
      <div className="space-y-3">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value[0]}
          onChange={(e) => onChange([Number(e.target.value), value[1]])}
          className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-sky-500"
        />
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value[1]}
          onChange={(e) => onChange([value[0], Number(e.target.value)])}
          className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-sky-500"
        />
      </div>
      <div className="flex justify-between text-[10px] font-bold text-slate-400 mt-2">
        <span>
          {minLabel}: {value[0]}
        </span>
        <span>
          {maxLabel}: {value[1]}
        </span>
      </div>
    </div>
  );
}

// ============================================================================
// SELECT DROPDOWN COMPONENT
// ============================================================================

export function SelectFilter({
  label,
  options,
  value,
  onChange,
  placeholder = 'Select an option',
}: SelectFilterProps) {
  return (
    <div className="mb-5">
      <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-2">
        {label}
      </label>
      <select
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value || null)}
        className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-medium text-slate-800 focus:outline-none focus:border-sky-400 transition-colors shadow-sm cursor-pointer"
      >
        <option value="">{placeholder}</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}

// ============================================================================
// CHECKBOX FILTER COMPONENT
// ============================================================================

export function CheckboxFilter({
  label,
  options,
  selectedValues,
  onChange,
}: CheckboxFilterProps) {
  const toggleValue = (value: string) => {
    if (selectedValues.includes(value)) {
      onChange(selectedValues.filter((v) => v !== value));
    } else {
      onChange([...selectedValues, value]);
    }
  };

  return (
    <div className="mb-5">
      <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-2">
        {label}
      </label>
      <div className="space-y-2">
        {options.map((opt) => (
          <label key={opt.value} className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={selectedValues.includes(opt.value)}
              onChange={() => toggleValue(opt.value)}
              className="w-3.5 h-3.5 text-sky-500 rounded border-slate-300 focus:ring-sky-400"
            />
            <span className="text-xs font-medium text-slate-700">{opt.label}</span>
          </label>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// SCORE RANGE FILTER COMPONENT (1-5 scale)
// ============================================================================

export function ScoreRangeFilter({
  label,
  minScore,
  maxScore,
  onMinChange,
  onMaxChange,
}: ScoreRangeFilterProps) {
  return (
    <div className="mb-5">
      <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-3">
        {label}
      </label>
      <div className="flex gap-2">
        <input
          type="number"
          min="1"
          max="5"
          value={minScore ?? ''}
          onChange={(e) => onMinChange(e.target.value ? Number(e.target.value) : undefined)}
          placeholder="Min (1-5)"
          className="flex-1 bg-white border border-slate-200 rounded-lg px-2 py-2 text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-400 shadow-sm"
        />
        <span className="text-slate-300 px-1 py-2">-</span>
        <input
          type="number"
          min="1"
          max="5"
          value={maxScore ?? ''}
          onChange={(e) => onMaxChange(e.target.value ? Number(e.target.value) : undefined)}
          placeholder="Max (1-5)"
          className="flex-1 bg-white border border-slate-200 rounded-lg px-2 py-2 text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-400 shadow-sm"
        />
      </div>
    </div>
  );
}

// ============================================================================
// DATE RANGE FILTER COMPONENT
// ============================================================================

export function DateRangeFilter({
  label,
  dateFrom,
  dateTo,
  onDateFromChange,
  onDateToChange,
}: DateRangeFilterProps) {
  return (
    <div className="mb-5">
      <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-3">
        {label}
      </label>
      <div className="flex gap-2">
        <input
          type="date"
          value={dateFrom ?? ''}
          onChange={(e) => onDateFromChange(e.target.value || undefined)}
          className="flex-1 bg-white border border-slate-200 rounded-lg px-2 py-2 text-xs font-medium text-slate-800 focus:outline-none focus:border-sky-400 shadow-sm"
        />
        <span className="text-slate-300 px-1 py-2">to</span>
        <input
          type="date"
          value={dateTo ?? ''}
          onChange={(e) => onDateToChange(e.target.value || undefined)}
          className="flex-1 bg-white border border-slate-200 rounded-lg px-2 py-2 text-xs font-medium text-slate-800 focus:outline-none focus:border-sky-400 shadow-sm"
        />
      </div>
    </div>
  );
}

// ============================================================================
// SEARCH FILTER COMPONENT
// ============================================================================

export function SearchFilter({
  placeholder = 'Search...',
  value,
  onChange,
}: SearchFilterProps) {
  return (
    <div className="mb-6">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2.5 text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-400 transition-colors shadow-sm"
      />
    </div>
  );
}

// ============================================================================
// FILTER SECTION HEADER WITH COLLAPSE
// ============================================================================

export function FilterSection({
  title,
  children,
  defaultOpen = true,
}: {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border-b border-slate-200 pb-4 mb-4">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between py-2 hover:opacity-70 transition-opacity"
      >
        <h3 className="text-[11px] font-black text-slate-800 uppercase tracking-wide">
          {title}
        </h3>
        <ChevronDown
          className={`w-4 h-4 text-slate-400 transition-transform ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>
      {isOpen && <div className="mt-4">{children}</div>}
    </div>
  );
}

// ============================================================================
// FILTER CLEAR BUTTON
// ============================================================================

export function ClearFiltersButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="w-full bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold py-2 px-3 rounded-lg text-xs transition-colors flex items-center justify-center gap-2"
    >
      <X className="w-3 h-3" />
      Limpiar Filtros
    </button>
  );
}

// ============================================================================
// ACTIVE FILTERS DISPLAY
// ============================================================================

export interface ActiveFilter {
  id: string;
  label: string;
  onRemove: () => void;
}

export function ActiveFilters({ filters }: { filters: ActiveFilter[] }) {
  if (filters.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mb-4">
      {filters.map((filter) => (
        <div
          key={filter.id}
          className="inline-flex items-center gap-2 bg-sky-100 text-sky-700 px-3 py-1 rounded-full text-xs font-semibold"
        >
          {filter.label}
          <button
            onClick={filter.onRemove}
            className="hover:opacity-70 transition-opacity"
          >
            <X className="w-3 h-3" />
          </button>
        </div>
      ))}
    </div>
  );
}

// ============================================================================
// COMPOUND FILTER SIDEBAR COMPONENT
// ============================================================================

interface FilterSidebarProps {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  onClear: () => void;
  maxHeight?: string;
}

export function FilterSidebarContainer({
  title = 'Smart Search',
  subtitle = 'Refine your results',
  children,
  onClear,
  maxHeight = 'calc(100vh - 69px)',
}: FilterSidebarProps) {
  return (
    <aside
      className={`w-64 bg-[#f8fafc] border-r border-slate-200 p-6 flex flex-col justify-between h-[${maxHeight}] overflow-y-auto shrink-0 text-left`}
    >
      <div>
        <h2 className="text-base font-bold text-slate-900 tracking-tight">
          {title}
        </h2>
        <p className="text-xs text-slate-400 mt-0.5 mb-6">{subtitle}</p>

        {children}
      </div>

      <ClearFiltersButton onClick={onClear} />
    </aside>
  );
}

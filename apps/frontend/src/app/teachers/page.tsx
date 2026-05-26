'use client'

import { useState, Suspense, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';
import { Navbar } from "@/components/layout/Navbar";
import TeacherCatalog from "@/components/teachers/TeacherCatalog";
import FilterSidebar from "@/components/teachers/FilterSidebar";
import { ProfessorFilterState } from "@/lib/hooks-filters";

function SearchContent() {
    const searchParams = useSearchParams();
    const initialQuery = searchParams.get('query') ?? '';
    const [searchQuery, setSearchQuery] = useState(initialQuery);
    
    // Filter state
    const [filters, setFilters] = useState<Partial<ProfessorFilterState>>({});

    // Handle filter changes from FilterSidebar
    const handleFiltersChange = useCallback((newFilters: Partial<ProfessorFilterState>) => {
        setFilters(newFilters);
    }, []);

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans selection:bg-sky-100 selection:text-sky-900 overflow-hidden">
            {/* Navbar with active search */}
            <Navbar
                showSearch={true}
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
            />

            {/* Main layout */}
            <div className="flex-1 flex w-full overflow-hidden">
                {/* Left sidebar - Filters */}
                <FilterSidebar onFiltersChange={handleFiltersChange} />

                {/* Center - Catalog */}
                <TeacherCatalog 
                    initialQuery={initialQuery}
                    filters={filters}
                />
            </div>
        </div>
    );
}

export default function TeachersPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-white flex items-center justify-center font-bold text-slate-400">Cargando Buscador Inteligente...</div>}>
            <SearchContent />
        </Suspense>
    );
}
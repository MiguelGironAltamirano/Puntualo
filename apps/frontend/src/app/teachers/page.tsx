'use client'

import { useState, Suspense, useCallback, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Navbar } from "@/components/layout/Navbar";
import TeacherCatalog from "@/components/teachers/TeacherCatalog";
import FilterSidebar from "@/components/teachers/FilterSidebar";
import { ProfessorFilterState } from "@/lib/hooks-filters";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { ChatToggleButton } from "@/components/chat/ChatToggleButton";

function SearchContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const initialQuery = searchParams.get('query') ?? '';

    // Filter and sidebar state — los filtros arrancan ocultos; el usuario los revela con un click.
    const [filters, setFilters] = useState<Partial<ProfessorFilterState>>({});
    const [isFilterOpen, setIsFilterOpen] = useState(false);
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(true);

    useEffect(() => {
        if (!localStorage.getItem('access_token')) {
            router.replace('/login');
        }
    }, [router]);

    // Un solo entry point para abrir filtros: drawer en mobile, sidebar en desktop.
    const handleOpenFilters = useCallback(() => {
        setIsFilterOpen(true);
        setIsSidebarCollapsed(false);
    }, []);

    // Handle filter changes from FilterSidebar
    const handleFiltersChange = useCallback((newFilters: Partial<ProfessorFilterState>) => {
        setFilters(newFilters);
    }, []);

    return (
        <div className="h-screen bg-white flex flex-col font-sans selection:bg-sky-100 selection:text-sky-900 overflow-hidden relative">
            {/* Navbar without active search */}
            <Navbar />

            {/* Main layout */}
            <div className="flex-1 flex flex-col md:flex-row w-full overflow-hidden relative">
                {/* Left sidebar - Filters */}
                <FilterSidebar 
                    onFiltersChange={handleFiltersChange} 
                    isOpen={isFilterOpen}
                    onClose={() => setIsFilterOpen(false)}
                    isCollapsed={isSidebarCollapsed}
                    onCollapseToggle={() => setIsSidebarCollapsed(prev => !prev)}
                />

                {/* Center - Catalog */}
                <div className="flex-1 relative flex flex-col overflow-hidden">
                    <TeacherCatalog
                        initialQuery={initialQuery}
                        filters={filters}
                        isSidebarCollapsed={isSidebarCollapsed}
                        onOpenFilters={handleOpenFilters}
                    />
                </div>

                {/* Right - Chat assistant (empuja en desktop, overlay en mobile) */}
                <ChatPanel />
            </div>

            {/* Floating button to toggle chat assistant */}
            <ChatToggleButton />
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
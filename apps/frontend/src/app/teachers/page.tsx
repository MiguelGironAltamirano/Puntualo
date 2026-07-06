'use client'

import { useState, Suspense, useCallback, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Navbar } from "@/components/layout/Navbar";
import TeacherCatalog from "@/components/teachers/TeacherCatalog";
import FilterSidebar from "@/components/teachers/FilterSidebar";
import { ProfessorFilterState } from "@/lib/hooks-filters";
import { SlidersHorizontal } from "lucide-react";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { ChatToggleButton } from "@/components/chat/ChatToggleButton";

function SearchContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const initialQuery = searchParams.get('query') ?? '';

    // Filter and sidebar state
    const [filters, setFilters] = useState<Partial<ProfessorFilterState>>({});
    const [isFilterOpen, setIsFilterOpen] = useState(false);
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

    useEffect(() => {
        if (!localStorage.getItem('access_token')) {
            router.replace('/login');
        }
    }, [router]);

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
                    {isSidebarCollapsed && (
                        <button
                            type="button"
                            onClick={() => setIsSidebarCollapsed(false)}
                            className="hidden md:flex absolute left-8 top-7 z-30 px-3.5 py-2 bg-white hover:bg-slate-50 border border-slate-200 rounded-xl text-slate-700 hover:text-[#0284c7] shadow-sm transition-all items-center gap-2 text-xs font-bold active:scale-95 cursor-pointer"
                        >
                            <SlidersHorizontal className="w-3.5 h-3.5" />
                            Mostrar Filtros
                        </button>
                    )}
                    <TeacherCatalog
                        initialQuery={initialQuery}
                        filters={filters}
                        isSidebarCollapsed={isSidebarCollapsed}
                    />
                </div>

                {/* Right - Chat assistant (empuja en desktop, overlay en mobile) */}
                <ChatPanel />
            </div>

            {/* Floating button on mobile to toggle filters */}
            <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 md:hidden">
                <button
                    type="button"
                    onClick={() => setIsFilterOpen(true)}
                    className="flex items-center gap-2 px-5 py-3 bg-[#0284c7] hover:bg-[#0270a5] text-white font-bold text-sm rounded-full shadow-lg shadow-sky-500/20 active:scale-95 transition-all cursor-pointer"
                >
                    <SlidersHorizontal className="w-4 h-4" />
                    Filtrar Búsqueda
                </button>
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
'use client'

import { useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Navbar } from "@/components/layout/Navbar";
import FilterSidebar from "@/components/teachers/FilterSidebar";
import TeacherCatalog from "@/components/teachers/TeacherCatalog";

function SearchContent() {
    const searchParams = useSearchParams();
    const initialQuery = searchParams.get('query') ?? '';
    const [searchQuery, setSearchQuery] = useState(initialQuery);

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans selection:bg-sky-100 selection:text-sky-900 overflow-hidden">
            {/* Navbar con el buscador superior activo y sincronizado */}
            <Navbar
                showSearch={true}
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
            />

            {/* Layout principal del Buscador */}
            <div className="flex-1 flex w-full overflow-hidden">
                {/* Barra Lateral Izquierda de Filtros Quirúrgicos */}
                <FilterSidebar />

                {/* Catálogo Central con las tarjetas de los docentes */}
                <TeacherCatalog />
            </div>
        </div>
    );
}

export default function TeachersPage() {
    return (
        // Usamos Suspense porque useSearchParams lo requiere en el nuevo router de Next.js
        <Suspense fallback={<div className="min-h-screen bg-white flex items-center justify-center font-bold text-slate-400">Cargando Buscador Inteligente...</div>}>
            <SearchContent />
        </Suspense>
    );
}
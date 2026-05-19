'use client'

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Navbar } from "@/components/layout/Navbar";
import SidebarFiltros from "./SidebarFiltros";
import CatalogoProfesores from "./CatalogoProfesores";

function BuscadorContenido() {
    const searchParams = useSearchParams();
    const [searchQuery, setSearchQuery] = useState('');

    // Sincroniza el texto que viene desde la Landing Page
    useEffect(() => {
        const queryParam = searchParams.get('query');
        if (queryParam) {
            setSearchQuery(queryParam);
        }
    }, [searchParams]);

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
                <SidebarFiltros />

                {/* Catálogo Central con las tarjetas de los docentes */}
                <CatalogoProfesores />
            </div>
        </div>
    );
}

export default function ProfesoresPage() {
    return (
        // Usamos Suspense porque useSearchParams lo requiere en el nuevo router de Next.js
        <Suspense fallback={<div className="min-h-screen bg-white flex items-center justify-center font-bold text-slate-400">Cargando Buscador Inteligente...</div>}>
            <BuscadorContenido />
        </Suspense>
    );
}
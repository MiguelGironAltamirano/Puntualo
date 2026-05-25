'use client'

import { AlignRight, Filter } from "lucide-react";
import { useRouter } from 'next/navigation';
import { HomeAISummary } from "./HomeAISummary";

interface FeatureCardsProps {
    canAccessBuscador: () => boolean;
}

export function FeatureCards({ canAccessBuscador }: FeatureCardsProps) {
    const router = useRouter();

    const mockSummary = {
        pros: ['Destaca por su claridad al explicar conceptos complejos'],
        contras: ['Sus parciales son conocidos por su alta dificultad']
    };

    return (
        <section className="flex flex-col items-center mt-12 w-full">
            <h2 className="text-xl font-extrabold text-[#0f172a] mb-2">¿Por qué usar Puntualo?</h2>
            <p className="text-[#64748b] text-sm font-medium mb-12 text-center max-w-2xl">
                Nuestra plataforma transforma la incertidumbre en confianza académica.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full mb-6">
                {/* Card 1: HomeAISummary */}
                <HomeAISummary summaryData={mockSummary} />

                {/* Card 2: Comparativa */}
                <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-[0_4px_20px_rgb(0,0,0,0.03)] hover:shadow-md transition-shadow flex flex-col">
                    <div className="w-10 h-10 bg-[#f1f5f9] rounded-xl flex items-center justify-center mb-6">
                        <AlignRight className="w-5 h-5 text-[#475569] transform -rotate-90" strokeWidth={2.5} />
                    </div>
                    <h3 className="text-lg font-extrabold text-[#0f172a] mb-3">Comparativa</h3>
                    <p className="text-[#64748b] mb-10 leading-relaxed text-sm font-medium flex-1">
                        Alinea hasta tres perfiles docentes lado a lado. Compara sus métricas de claridad, dificultad y accesibilidad en un layout paralelo perfecto.
                    </p>

                    <div className="flex gap-2 mt-auto pb-4">
                        <div className="h-2 bg-[#ff8a00] w-[40%] rounded-full"></div>
                        <div className="h-2 bg-[#0ea5e9] w-[35%] rounded-full"></div>
                        <div className="h-2 bg-[#cbd5e1] w-[25%] rounded-full"></div>
                    </div>
                </div>
            </div>

            {/* Full Width Card: Filtros */}
            <div className="bg-white w-full rounded-2xl p-8 border border-gray-100 shadow-[0_4px_20px_rgb(0,0,0,0.03)] hover:shadow-md transition-shadow flex flex-col md:flex-row md:items-center justify-between gap-8">
                <div className="flex items-start md:items-center gap-6">
                    <div className="w-10 h-10 bg-[#f1f5f9] rounded-xl flex items-center justify-center flex-shrink-0">
                        <Filter className="w-5 h-5 text-[#64748b]" strokeWidth={2.5} />
                    </div>
                    <div>
                        <h3 className="text-lg font-extrabold text-[#0f172a] mb-1.5">Filtros Quirúrgicos</h3>
                        <p className="text-[#64748b] text-sm leading-relaxed max-w-2xl font-medium">
                            Refina tu búsqueda a un nivel granular. Filtra no solo por departamento o facultad, sino por metodologías de evaluación, tolerancia a inasistencias o carga de lectura.
                        </p>
                    </div>
                </div>
                <button
                    type="button"
                    onClick={() => {
                        if (canAccessBuscador()) {
                            router.push('/teachers');
                        }
                    }}
                    className="px-6 py-2.5 rounded-full border-2 border-[#bae6fd] text-[#0284c7] font-bold hover:bg-[#f0f9ff] transition-colors whitespace-nowrap text-sm text-center focus:outline-none cursor-pointer"
                >
                    Explorar Buscador
                </button>
            </div>
        </section>
    );
}

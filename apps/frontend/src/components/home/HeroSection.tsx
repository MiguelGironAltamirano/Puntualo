'use client'

import { Search, ShieldCheck, Sparkles, BarChart3 } from "lucide-react";
import { useRouter } from 'next/navigation';

const trustSignals = [
    { icon: ShieldCheck, label: "Reseñas de estudiantes verificados" },
    { icon: Sparkles, label: "Síntesis por IA" },
    { icon: BarChart3, label: "Comparativas con datos" },
];

interface HeroSectionProps {
    searchQuery: string;
    setSearchQuery: (val: string) => void;
    canAccessBuscador: () => boolean;
    handleSearch: (e: React.FormEvent) => void;
}

export function HeroSection({ searchQuery, setSearchQuery, canAccessBuscador, handleSearch }: HeroSectionProps) {
    const router = useRouter();

    return (
        <section className="flex flex-col items-center text-center mt-4 mb-24">
            <div className="pl-reveal inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#f1f5f9] text-[#475569] text-xs font-semibold mb-8">
                <span className="text-[#0284c7]">✨</span> Búsqueda potenciada por Inteligencia Artificial
            </div>

            <h1 className="pl-reveal text-4xl sm:text-5xl md:text-[3.5rem] font-extrabold text-[#0f172a] tracking-tight text-balance max-w-3xl leading-tight mb-6" style={{ animationDelay: '0.05s' }}>
                Elige al docente <span className="text-[#0284c7]">ideal</span> para tu semestre.
            </h1>

            <p className="pl-reveal text-lg text-[#64748b] max-w-2xl mb-10 leading-relaxed font-medium text-pretty" style={{ animationDelay: '0.12s' }}>
                Decisiones académicas respaldadas por datos. Encuentra perfiles detallados, comparativas estructuradas y el consenso real de los estudiantes.
            </p>

            <form onSubmit={handleSearch} className="pl-reveal w-full max-w-3xl relative" style={{ animationDelay: '0.2s' }}>
                <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-slate-500" strokeWidth={2.5} />
                </div>
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    spellCheck={false}
                    className="w-full h-16 pl-14 pr-32 rounded-full border border-gray-200 bg-white shadow-[0_8px_30px_rgb(0,0,0,0.06)] text-base font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-100 focus:border-sky-300 transition-all placeholder:text-slate-500 block"
                    placeholder="Busca por docente, materia o facultad..."
                />
                <button type="submit" className="absolute right-2 top-2 bottom-2 px-8 bg-[#c2410c] hover:bg-[#9a3412] text-white font-bold text-sm rounded-full transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:ring-offset-2">
                    Buscar
                </button>
            </form>

            <div className="flex flex-wrap justify-center gap-3 mt-6">
                {["Cálculo Avanzado", "Ingeniería", "Alta Claridad"].map((tag) => (
                    <button
                        key={tag}
                        type="button"
                        onClick={() => {
                            if (canAccessBuscador()) {
                                router.push(`/teachers?query=${encodeURIComponent(tag)}`);
                            }
                        }}
                        className="px-4 py-1.5 bg-[#f8fafc] border border-gray-200 rounded-full text-xs font-bold text-[#64748b] shadow-sm hover:border-gray-300 cursor-pointer transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:ring-offset-2"
                    >
                        {tag}
                    </button>
                ))}
            </div>

            {/* Microcopy honesto: comunica el muro antes de que el usuario choque con él */}
            <p className="mt-5 text-xs font-medium text-[#64748b]">
                Crea una cuenta gratis para buscar y ver perfiles completos.
            </p>

            {/* Barra de confianza: señales reales, no métricas inventadas */}
            <ul className="mt-10 flex flex-wrap items-center justify-center gap-x-7 gap-y-3">
                {trustSignals.map(({ icon: Icon, label }) => (
                    <li key={label} className="flex items-center gap-2 text-xs sm:text-[13px] font-semibold text-[#475569]">
                        <Icon className="w-4 h-4 text-[#0284c7] shrink-0" strokeWidth={2.5} />
                        {label}
                    </li>
                ))}
            </ul>
        </section>
    );
}

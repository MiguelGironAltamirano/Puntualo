'use client'

import { Search } from "lucide-react";
import { useRouter } from 'next/navigation';

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
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#f1f5f9] text-[#475569] text-xs font-semibold mb-8">
                <span className="text-[#0284c7]">✨</span> Búsqueda potenciada por Inteligencia Artificial
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-[3.5rem] font-extrabold text-[#0f172a] tracking-tight max-w-3xl leading-tight mb-6">
                Elige al docente <span className="text-[#0284c7]">ideal</span> para tu semestre.
            </h1>

            <p className="text-lg text-[#64748b] max-w-2xl mb-10 leading-relaxed font-medium">
                Decisiones académicas respaldadas por datos. Encuentra perfiles detallados, comparativas estructuradas y el consenso real de los estudiantes.
            </p>

            <form onSubmit={handleSearch} className="w-full max-w-3xl relative">
                <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400" strokeWidth={2.5} />
                </div>
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    spellCheck={false}
                    className="w-full h-16 pl-14 pr-32 rounded-full border border-gray-200 bg-white shadow-[0_8px_30px_rgb(0,0,0,0.06)] text-base font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-100 focus:border-sky-300 transition-all placeholder:text-gray-400 block"
                    placeholder="Busca por docente, materia o facultad..."
                />
                <button type="submit" className="absolute right-2 top-2 bottom-2 px-8 bg-[#ff8a00] hover:bg-[#ea580c] text-white font-bold text-sm rounded-full transition-colors">
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
                        className="px-4 py-1.5 bg-[#f8fafc] border border-gray-200 rounded-full text-xs font-bold text-[#64748b] shadow-sm hover:border-gray-300 cursor-pointer transition-colors"
                    >
                        {tag}
                    </button>
                ))}
            </div>
        </section>
    );
}

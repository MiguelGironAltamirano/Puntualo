'use client'

import { AlignRight, Filter } from "lucide-react";
import { useRouter } from 'next/navigation';
import { HomeAISummary } from "./HomeAISummary";
import { Reveal } from "@/components/motion/Reveal";

interface FeatureCardsProps {
    canAccessBuscador: () => boolean;
}

// Datos de ejemplo para el mini-gráfico (ilustrativos).
const comparativa = [
    { name: "García", value: 4.7, color: "bg-[#0284c7]" },
    { name: "López", value: 3.8, color: "bg-[#ff8a00]" },
    { name: "Martínez", value: 3.1, color: "bg-[#cbd5e1]" },
];

const filterChips = [
    { label: "Ingeniería", className: "bg-[#e0f2fe] text-[#0369a1]" },
    { label: "Alta Claridad", className: "bg-[#dcfce7] text-[#15803d]" },
    { label: "Alta Exigencia", className: "bg-[#ffedd5] text-[#c2410c]" },
    { label: "Fac. de Ciencias", className: "bg-[#f8fafc] text-[#475569] border border-gray-200" },
    { label: "Pocos parciales", className: "bg-[#f8fafc] text-[#475569] border border-gray-200" },
    { label: "+12 más", className: "bg-[#f1f5f9] text-[#64748b]" },
];

function Kicker({ children }: { children: React.ReactNode }) {
    return (
        <span className="text-xs font-bold uppercase tracking-[0.18em] text-[#0284c7]">{children}</span>
    );
}

export function FeatureCards({ canAccessBuscador }: FeatureCardsProps) {
    const router = useRouter();

    const goToBuscador = (query?: string) => {
        if (canAccessBuscador()) {
            router.push(query ? `/teachers?query=${encodeURIComponent(query)}` : '/teachers');
        }
    };

    return (
        <section className="flex flex-col items-center mt-24 w-full">
            <Reveal className="w-full">
                <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0f172a] tracking-tight text-balance text-center mb-3">¿Por qué usar Puntualo?</h2>
                <p className="text-[#64748b] text-sm sm:text-base font-medium mb-14 text-center max-w-2xl mx-auto">
                    Nuestra plataforma transforma la incertidumbre en confianza académica.
                </p>
            </Reveal>

            <div className="flex flex-col gap-8 w-full">
                {/* Card 1 — Síntesis IA */}
                <Reveal className="w-full">
                    <article className="rounded-2xl bg-gradient-to-br from-[#f0f9ff] to-[#e0f2fe] border border-[#bae6fd]/60 p-8 sm:p-10 grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-10 items-center">
                        <div>
                            <Kicker>Inteligencia Artificial</Kicker>
                            <h3 className="text-2xl sm:text-3xl font-extrabold text-[#0f172a] tracking-tight text-balance mt-3 mb-4">
                                Síntesis IA de cada docente
                            </h3>
                            <p className="text-[#475569] text-sm sm:text-base leading-relaxed font-medium mb-6 max-w-md">
                                No pierdas tiempo leyendo cientos de comentarios. Nuestro motor procesa todas las evaluaciones y te entrega un resumen ejecutivo sobre metodología, exigencia y trato.
                            </p>
                            <button
                                type="button"
                                onClick={() => goToBuscador()}
                                className="inline-flex items-center gap-1.5 text-sm font-bold text-[#0284c7] hover:gap-2.5 transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:ring-offset-2 rounded"
                            >
                                Ver un ejemplo
                                <span aria-hidden="true">→</span>
                            </button>
                        </div>
                        <HomeAISummary />
                    </article>
                </Reveal>

                {/* Card 2 — Comparativa */}
                <Reveal className="w-full">
                    <article className="rounded-2xl bg-white border border-gray-100 shadow-[0_4px_20px_rgb(0,0,0,0.03)] p-8 sm:p-10 grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-10 items-center">
                        <div>
                            <div className="w-10 h-10 bg-[#f1f5f9] rounded-xl flex items-center justify-center mb-6">
                                <AlignRight className="w-5 h-5 text-[#475569] -rotate-90" strokeWidth={2.5} />
                            </div>
                            <Kicker>Side-by-side</Kicker>
                            <h3 className="text-2xl sm:text-3xl font-extrabold text-[#0f172a] tracking-tight mt-3 mb-4">Comparativa</h3>
                            <p className="text-[#475569] text-sm sm:text-base leading-relaxed font-medium max-w-md">
                                Alinea hasta tres perfiles docentes lado a lado y compara sus métricas de claridad, dificultad y accesibilidad en un panel paralelo.
                            </p>
                        </div>

                        <div className="bg-[#f8fafc] rounded-xl border border-gray-100 p-5 sm:p-6">
                            <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-[#64748b] mb-5">Claridad comparada</p>
                            <div className="flex flex-col gap-4">
                                {comparativa.map((row) => (
                                    <div key={row.name} className="flex items-center gap-3">
                                        <span className="w-16 text-xs font-bold text-[#475569] shrink-0">{row.name}</span>
                                        <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                                            <div className={`h-full rounded-full ${row.color}`} style={{ width: `${(row.value / 5) * 100}%` }} />
                                        </div>
                                        <span className="w-8 text-xs font-extrabold text-[#0f172a] text-right shrink-0">{row.value}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </article>
                </Reveal>

                {/* Card 3 — Filtros Quirúrgicos */}
                <Reveal className="w-full">
                    <article className="rounded-2xl bg-white border border-gray-100 shadow-[0_4px_20px_rgb(0,0,0,0.03)] p-8 sm:p-10 grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-10 items-center">
                        <div>
                            <div className="w-10 h-10 bg-[#f1f5f9] rounded-xl flex items-center justify-center mb-6">
                                <Filter className="w-5 h-5 text-[#64748b]" strokeWidth={2.5} />
                            </div>
                            <Kicker>Granular</Kicker>
                            <h3 className="text-2xl sm:text-3xl font-extrabold text-[#0f172a] tracking-tight mt-3 mb-4">Filtros Quirúrgicos</h3>
                            <p className="text-[#475569] text-sm sm:text-base leading-relaxed font-medium max-w-md mb-6">
                                Refina por metodología de evaluación, tolerancia a inasistencias, carga de lectura, facultad y mucho más. El control es tuyo.
                            </p>
                            <button
                                type="button"
                                onClick={() => goToBuscador()}
                                className="inline-flex items-center gap-1.5 text-sm font-bold text-[#0284c7] hover:gap-2.5 transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:ring-offset-2 rounded"
                            >
                                Explorar el buscador
                                <span aria-hidden="true">→</span>
                            </button>
                        </div>

                        <div className="flex flex-wrap gap-2.5 content-start">
                            {filterChips.map((chip) => (
                                <span key={chip.label} className={`px-3.5 py-1.5 rounded-full text-xs font-bold ${chip.className}`}>
                                    {chip.label}
                                </span>
                            ))}
                        </div>
                    </article>
                </Reveal>
            </div>
        </section>
    );
}

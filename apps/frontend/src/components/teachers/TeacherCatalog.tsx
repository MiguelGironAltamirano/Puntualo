'use client'

import { useState } from "react";
import Link from "next/link";
import { Plus } from "lucide-react";
import { TeacherSummary } from "./types";
import { SearchAIAnalysis } from "./SearchAIAnalysis";
import { RegisterTeacherModal } from "./RegisterTeacherModal";

const TEACHERS_MOCK: TeacherSummary[] = [
    {
        id: 1,
        name: 'Dr. Roberto Sánchez',
        course: 'Ingeniería de Software',
        rating: 4.9,
        claridad: 4.2,
        dificultad: 1.7,
        avatar: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150&auto=format&fit=crop&q=80',
        tags: ['BARCO', 'PROYECTOS']
    },
    {
        id: 2,
        name: 'Dra. Elena Medina',
        course: 'Bases de Datos',
        rating: 4.2,
        claridad: 3.4,
        dificultad: 2.2,
        avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80',
        tags: ['INSPIRADORA']
    },
    {
        id: 3,
        name: 'Mtro. Carlos Vega',
        course: 'Estructuras de Datos',
        rating: 4.5,
        claridad: 3.9,
        dificultad: 2.7,
        avatar: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&auto=format&fit=crop&q=80',
        tags: ['EXIGENTE', 'JUSTO']
    }
];

export default function TeacherCatalog({ initialQuery }: { initialQuery?: string }) {
    const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);

    return (
        <div className="flex-1 p-8 bg-[#f8fafc]/40 text-left overflow-y-auto h-[calc(100vh-69px)]">
            <div className="max-w-[1300px] mx-auto">

                {/* Banner de Análisis de Resultados IA */}
                {TEACHERS_MOCK.length > 0 && (
                    <SearchAIAnalysis analysis={{ matchesText: initialQuery 
                        ? `Hemos encontrado varios docentes relacionados con "${initialQuery}". La mayoría pertenece al departamento de Ingeniería y destacan por perfiles metodológicos afines a tu búsqueda.` 
                        : `Hemos encontrado ${TEACHERS_MOCK.length} docentes que coinciden con tu perfil de "Proyectos Prácticos" y personalidad "Barco". La mayoría pertenece al departamento de Ingeniería.` 
                    }} />
                )}

                {/* Cabecera del Catálogo */}
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
                    <div>
                        <h1 className="text-xl font-black text-slate-900 tracking-tight">Resultados de Búsqueda</h1>
                        <p className="text-xs text-slate-400 mt-1 font-medium">Mostrando 12 de 45 profesores</p>
                    </div>

                    <div className="flex items-center gap-5 self-end sm:self-auto">
                        <button type="button" onClick={() => setIsRegisterModalOpen(true)} className="px-4 py-2.5 bg-[#ff8a00] hover:bg-[#ea580c] text-white text-xs font-bold rounded-xl flex items-center gap-1.5 transition-colors shadow-sm cursor-pointer">
                            <Plus className="w-4 h-4" strokeWidth={3} /> Agregar nuevo profesor
                        </button>

                        <div className="text-xs font-semibold text-slate-500 flex items-center gap-1.5">
                            <span className="text-slate-400 font-medium">Ordenar por:</span>
                            <select className="bg-transparent font-bold text-slate-800 focus:outline-none cursor-pointer">
                                <option>Mayor Puntaje</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Cuadrícula de Tarjetas */}
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {TEACHERS_MOCK.map((prof) => (
                        /* 2. Envolvemos la tarjeta completa con el Link usando backticks `` para inyectar el ID dinámico */
                        <Link
                            key={prof.id}
                            href={`/teachers/${prof.id}`}
                            className="border border-slate-100 bg-white rounded-2xl p-6 shadow-[0_4px_25px_rgba(0,0,0,0.02)] hover:shadow-[0_4px_30px_rgba(0,0,0,0.05)] transition-all flex flex-col justify-between relative min-h-[220px] no-underline group cursor-pointer"
                        >
                            {/* Fila Superior: Foto Real e Info */}
                            <div className="flex items-start justify-between gap-3 mb-5">
                                <div className="flex items-center gap-3.5">
                                    <div className="w-12 h-12 rounded-full border border-slate-100 overflow-hidden bg-slate-50 shrink-0">
                                        <img src={prof.avatar} alt={prof.name} className="w-full h-full object-cover object-top" />
                                    </div>
                                    <div>
                                        <h3 className="text-sm font-black text-slate-900 tracking-tight leading-snug group-hover:text-[#0284c7] transition-colors">{prof.name}</h3>
                                        <p className="text-[11px] font-semibold text-slate-400 mt-0.5">{prof.course}</p>
                                    </div>
                                </div>
                                <div className="bg-[#ff8a00] text-white text-[11px] font-black px-2 py-0.5 rounded-lg flex items-center gap-0.5 shadow-sm shrink-0">
                                    {prof.rating} ★
                                </div>
                            </div>

                            {/* Barras de Métricas */}
                            <div className="space-y-3 mb-6">
                                <div>
                                    <div className="flex justify-between text-[10px] font-bold text-slate-400 mb-1">
                                        <span>Claridad</span>
                                    </div>
                                    <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                                        <div className="bg-[#ff8a00] h-full rounded-full transition-all duration-500" style={{ width: `${(prof.claridad / 5) * 100}%` }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-[10px] font-bold text-slate-400 mb-1">
                                        <span>Dificultad</span>
                                    </div>
                                    <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                                        <div className="bg-slate-300 h-full rounded-full transition-all duration-500" style={{ width: `${(prof.dificultad / 5) * 100}%` }}></div>
                                    </div>
                                </div>
                            </div>

                            {/* Fila Inferior */}
                            <div className="flex items-center justify-between gap-2 pt-4 border-t border-slate-50 mt-auto">
                                <div className="flex flex-wrap gap-1.5">
                                    {prof.tags.map(t => (
                                        <span key={t} className="px-2.5 py-0.5 bg-[#e0f2fe] text-[#0284c7] font-bold text-[9px] rounded-md tracking-wider">
                                            {t}
                                        </span>
                                    ))}
                                </div>
                                <div className="w-7 h-7 border border-slate-200 group-hover:border-sky-400 group-hover:bg-sky-50 rounded-full flex items-center justify-center text-slate-400 group-hover:text-[#0284c7] transition-all text-sm font-bold shadow-none">
                                    +
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>

                {/* Modal de Registro */}
                <RegisterTeacherModal isOpen={isRegisterModalOpen} onClose={() => setIsRegisterModalOpen(false)} />
            </div>
        </div>
    );
}
'use client'
import { useState, useMemo, useCallback, useEffect } from "react";
import Link from "next/link";
import { Plus, AlertCircle, CheckCircle2, User } from "lucide-react";
import { TeacherSummary } from "./types";
import { SearchAIAnalysis } from "./SearchAIAnalysis";
import { RegisterTeacherModal } from "./RegisterTeacherModal";
import { useProfessors } from "@/lib/hooks";
import { ProfessorRead } from "@/lib/api";

type SortBy = 'global_score' | 'total_evaluations' | 'created_at';

/**
 * Maps API ProfessorRead to frontend TeacherSummary
 * Calculates metrics from evaluations data
 */
function mapProfessorToTeacher(professor: ProfessorRead): TeacherSummary {
    return {
        id: professor.id,
        name: professor.full_name,
        course: `${professor.total_evaluations} evaluaciones`, // Placeholder course info
        rating: professor.global_score ?? 0,
        claridad: 3.5, // Default - should come from evaluations API
        dificultad: 2.5, // Default - should come from evaluations API
        puntualidad: 4.0, // Default - should come from evaluations API
        avatar: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150&auto=format&fit=crop&q=80', // Placeholder
        tags: professor.validation_status === 'validated' ? ['VERIFICADO'] : [],
    };
}

export default function TeacherCatalog({ 
    initialQuery, 
    filters = {} 
}: { 
    initialQuery?: string;
    filters?: Record<string, unknown>;
}) {
    const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [sortBy, setSortBy] = useState<SortBy>('global_score');
    const pageSize = 20;

    // Memoize search params to prevent infinite fetch loops
    const searchParams = useMemo(() => ({
        search: initialQuery,
        page: currentPage,
        page_size: pageSize,
        sort_by: sortBy,
        sort_order: 'desc' as const,
        ...filters,
    }), [initialQuery, currentPage, pageSize, sortBy, filters]);

    // Fetch professors from API
    const { data: professorsData, loading, error } = useProfessors(searchParams);

    // Map API response to TeacherSummary type
    const teachers = useMemo(() => {
        return professorsData?.items?.map(mapProfessorToTeacher) ?? [];
    }, [professorsData?.items]);

    // Calculate display info
    const totalProfessors = professorsData?.total ?? 0;
    const startIndex = (currentPage - 1) * pageSize + 1;
    const endIndex = Math.min(currentPage * pageSize, totalProfessors);
    const showingText = totalProfessors > 0 
        ? `Mostrando ${startIndex} a ${endIndex} de ${totalProfessors} profesores`
        : 'Sin resultados';

    return (
        <div className="flex-1 p-8 bg-[#f8fafc]/40 text-left overflow-y-auto h-[calc(100vh-69px)]">
            <div className="max-w-[1300px] mx-auto">

                {/* AI Analysis Banner - Show only if we have results and a query */}
                {teachers.length > 0 && initialQuery && (
                    <SearchAIAnalysis analysis={{ matchesText: `Hemos encontrado ${teachers.length} docentes relacionados con "${initialQuery}".` }} />
                )}

                {/* Loading State */}
                {loading && (
                    <div className="flex flex-col items-center justify-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#ff8a00] mb-4"></div>
                        <p className="text-slate-500 font-medium">Cargando profesores...</p>
                    </div>
                )}

                {/* Error State */}
                {error && !loading && (
                    <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
                        <div>
                            <h3 className="text-sm font-bold text-red-900">Error al cargar profesores</h3>
                            <p className="text-xs text-red-600 mt-1">{error.message}</p>
                        </div>
                    </div>
                )}

               {/* Controles de Acción (Botón y Ordenamiento) */}
                <div className="flex items-center gap-5 self-end sm:self-auto justify-end w-full mb-6">
                    <button
                        type="button"
                        onClick={() => setIsRegisterModalOpen(true)}
                        className="px-4 py-2.5 bg-[#ff8a00] hover:bg-[#ea580c] text-white text-xs font-bold rounded-xl flex items-center gap-1.5 transition-colors shadow-sm cursor-pointer"
                    >
                        <Plus className="w-4 h-4" strokeWidth={3} /> Agregar nuevo profesor
                    </button>

                    <div className="text-xs font-semibold text-slate-500 flex items-center gap-1.5">
                        <span className="text-slate-400 font-medium">Ordenar por:</span>
                        <select
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value as SortBy)}
                            className="bg-transparent font-bold text-slate-800 focus:outline-none cursor-pointer"
                        >
                            <option value="global_score">Mayor puntaje</option>
                            <option value="total_evaluations">Más evaluado</option>
                            <option value="created_at">Más reciente</option>
                        </select>
                    </div>
                </div>

                {/* Empty State - No query yet */}
                {!initialQuery && !loading && teachers.length === 0 && (
                    <div className="flex flex-col items-center justify-center py-16">
                        <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mb-4">
                            <span className="text-2xl">🔍</span>
                        </div>
                        <h2 className="text-lg font-bold text-slate-900 mb-2">Comienza tu búsqueda</h2>
                        <p className="text-sm text-slate-500 text-center max-w-md">
                            Usa el buscador superior o los filtros laterales para encontrar el profesor ideal.
                        </p>
                    </div>
                )}

                {/* Empty Results State */}
                {initialQuery && !loading && teachers.length === 0 && !error && (
                    <div className="flex flex-col items-center justify-center py-16">
                        <div className="w-16 h-16 rounded-full bg-orange-100 flex items-center justify-center mb-4">
                            <span className="text-2xl">😔</span>
                        </div>
                        <h2 className="text-lg font-bold text-slate-900 mb-2">No encontramos profesores</h2>
                        <p className="text-sm text-slate-500 text-center max-w-md">
                            No hay resultados para "<strong>{initialQuery}</strong>". Intenta con otro nombre o código.
                        </p>
                    </div>
                )}

                {/* Results View */}
                {teachers.length > 0 && !loading && (
                    <>
                        {/* Header */}
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
                            <div>
                                <h1 className="text-xl font-black text-slate-900 tracking-tight">Resultados de Búsqueda</h1>
                                <p className="text-xs text-slate-400 mt-1 font-medium">{showingText}</p>
                            </div>

                        </div>

                        {/* Teacher Cards Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                            {teachers.map((prof) => (
                                <Link
                                    key={prof.id}
                                    href={`/teachers/${prof.id}`}
                                    className="border border-slate-100 bg-white rounded-2xl p-6 shadow-[0_4px_25px_rgba(0,0,0,0.02)] hover:shadow-[0_4px_30px_rgba(0,0,0,0.05)] transition-all flex flex-col justify-between relative min-h-[220px] no-underline group cursor-pointer"
                                >
                                    {/* Top Row: Avatar & Info */}
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
                                            {prof.rating.toFixed(1)} ★
                                        </div>
                                    </div>

                                    {/* Metric Bars */}
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

                                    {/* Bottom Row */}
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

                        {/* Pagination */}
                        {professorsData && professorsData.total_pages > 1 && (
                            <div className="flex items-center justify-center gap-2 mt-12">
                                <button
                                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                    disabled={!professorsData.has_prev}
                                    className="px-3 py-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                    Anterior
                                </button>
                                <div className="text-xs text-slate-600 font-medium">
                                    Página {currentPage} de {professorsData.total_pages}
                                </div>
                                <button
                                    onClick={() => setCurrentPage(p => p + 1)}
                                    disabled={!professorsData.has_next}
                                    className="px-3 py-2 border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                    Siguiente
                                </button>
                            </div>
                        )}
                    </>
                )}

                {/* Register Modal */}
                <RegisterTeacherModal isOpen={isRegisterModalOpen} onClose={() => setIsRegisterModalOpen(false)} />
            </div>
        </div>
    );
}

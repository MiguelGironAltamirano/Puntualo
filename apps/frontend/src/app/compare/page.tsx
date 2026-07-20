'use client'

import { useState, useMemo, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Navbar } from '@/components/layout/Navbar';
import { Search, Plus, X, RotateCcw, Loader2, AlertCircle } from 'lucide-react';
import { IASummary } from '@/components/compare/IASummary';
import { CompareMetrics } from '@/components/compare/CompareMetrics';
import { StudentReviews } from '@/components/compare/StudentReviews';
import { useProfessors, useCompareProfessors, useDebounce } from '@/lib/hooks';
import { ProfessorComparisonResponse } from '@/lib/api';
import { useCompareStore, useCompareHydration, mapProfessorToTeacher } from '@/store/useCompareStore';

export default function ComparePage() {
    const router = useRouter();
    useCompareHydration();
    const selectedTeachers = useCompareStore((s) => s.selected);
    const toggleTeacher = useCompareStore((s) => s.toggle);
    const removeTeacher = useCompareStore((s) => s.remove);
    const clearTeachers = useCompareStore((s) => s.clear);

    useEffect(() => {
        if (!localStorage.getItem('access_token')) {
            router.replace('/login');
        }
    }, [router]);

    const [searchQuery, setSearchQuery] = useState('');

    // Debounce search inputs to reduce API calls while typing (300ms delay)
    const debouncedSearch = useDebounce(searchQuery, 300);

    // Memoize search params to prevent infinite fetch loops
    const searchParams = useMemo(() => ({
        search: debouncedSearch,
        page: 1,
        page_size: 10,
    }), [debouncedSearch]);

    // Fetch professors for search
    const { data: results, loading: loadingSearch } = useProfessors(searchParams, !debouncedSearch);

    // Fetch comparison data when 2 or more professors are selected
    const selectedIds = useMemo(
        () => selectedTeachers.map(t => t.id),
        [selectedTeachers]
    );

    const { data: comparison, loading: loadingComparison, error: comparisonError } = useCompareProfessors(
        selectedIds.length >= 2 ? selectedIds : null
    );

    // Map search results, filtering out already selected teachers
    const filteredTeachers = useMemo(
        () => results?.items?.map(mapProfessorToTeacher).filter(t => !selectedIds.includes(t.id)) ?? [],
        [results?.items, selectedIds]
    );

    // Update selected teachers with real comparison data when available
    const displayTeachers = useMemo(() => {
        if (!comparison || !comparison.professors) return selectedTeachers;

        return selectedTeachers.map(teacher => {
            const apiData = comparison.professors.find(p => p.id === teacher.id);
            if (!apiData) return teacher;

            return {
                ...teacher,
                rating: apiData.global_score ?? 0,
                clarity: apiData.avg_clarity ?? 0,
                difficulty: apiData.avg_easiness !== null ? (5 - apiData.avg_easiness) : 0,
                helpfulness: apiData.avg_helpfulness ?? 0,
                punctuality: apiData.avg_punctuality ?? 0,
                course: apiData.common_courses?.[0]?.name || 'Ver en perfil',
                reviews: apiData.recent_comments?.map((c: any) => ({
                    text: c.text,
                    course: c.course_name || 'Curso general',
                    date: new Date(c.created_at).toLocaleDateString(),
                })) || [],
                aiSummary: apiData.ai_summary ? {
                    pros: apiData.ai_summary.pros || [],
                    contras: apiData.ai_summary.cons || []
                } : { pros: [], contras: [] }
            };
        });
    }, [selectedTeachers, comparison]);

    const gridColsClass = 
        Math.min(4, displayTeachers.length + (displayTeachers.length < 4 ? 1 : 0)) === 2 ? 'md:grid-cols-2' : 
        Math.min(4, displayTeachers.length + (displayTeachers.length < 4 ? 1 : 0)) === 3 ? 'md:grid-cols-3' : 
        'md:grid-cols-4';

    return (
        <div className="min-h-screen bg-white font-sans text-slate-900">
            <Navbar />

            <div className="mx-auto max-w-[1400px] px-4 md:px-8 py-8">

                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10 pb-6 border-b border-slate-100">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-black text-[#0284c7] tracking-tight">Versus</h1>
                        <p className="text-sm text-slate-500 mt-1 font-medium">
                            Comparando docentes en paralelo. Contrasta sus métricas y opiniones (máximo 4).
                        </p>
                    </div>
                    {displayTeachers.length > 0 && (
                        <button
                            onClick={() => { clearTeachers(); }}
                            className="flex items-center gap-2 px-4 py-2 justify-center border border-slate-200 bg-white hover:bg-slate-50 rounded-xl text-sm font-bold text-slate-700 transition-colors shadow-sm cursor-pointer w-full sm:w-auto shrink-0"
                        >
                            <RotateCcw className="w-4 h-4 text-slate-400" />
                            Limpiar Comparación
                        </button>
                    )}
                </div>

                {/* Comparison error */}
                {comparisonError && selectedIds.length >= 2 && (
                    <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
                        <div>
                            <h3 className="text-sm font-bold text-red-900">Error al cargar comparación</h3>
                            <p className="text-xs text-red-600 mt-1">{comparisonError.message}</p>
                        </div>
                    </div>
                )}

                {/* Main dynamic grid layout */}
                <div className={`grid grid-cols-1 ${gridColsClass} gap-8`}>

                    {/* Render Selected Teachers */}
                    {displayTeachers.map((teacher, index) => (
                        <div key={teacher.id} className="relative">
                            <div className="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm relative h-full">
                                <button 
                                    onClick={() => {
                                        removeTeacher(teacher.id);
                                    }}
                                    className="absolute right-4 top-4 p-1.5 bg-slate-50 hover:bg-red-50 hover:text-red-500 rounded-xl transition-all"
                                >
                                    <X size={16} />
                                </button>
                                <div className="flex flex-col items-center text-center py-4">
                                    <div className="w-16 h-16 rounded-full bg-sky-50 border border-sky-100 flex items-center justify-center text-2xl mb-3 shrink-0">
                                        {index === 0 ? '👨‍🏫' : index === 1 ? '👩‍🏫' : index === 2 ? '🧑‍🏫' : '👩‍🎓'}
                                    </div>
                                    <h2 className="text-lg font-black text-slate-900 leading-tight truncate w-full" title={teacher.name}>{teacher.name}</h2>
                                    <p className="text-xs font-bold text-slate-400 mt-1">{teacher.school}</p>
                                </div>
                            </div>
                        </div>
                    ))}

                    {/* Placeholder Slot to Add Teacher */}
                    {displayTeachers.length < 4 && (
                        <div className="relative">
                            <div className="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm flex flex-col justify-between h-full min-h-[220px]">
                                <div>
                                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
                                        {displayTeachers.length === 0 ? 'Seleccionar Primer Docente' : 
                                         displayTeachers.length === 1 ? 'Seleccionar Segundo Docente' : 
                                         displayTeachers.length === 2 ? 'Agregar Tercer Docente' : 
                                         'Agregar Cuarto Docente'}
                                    </h3>
                                    <div className="relative">
                                        <Search className="absolute left-4 top-3.5 text-slate-400" size={18} />
                                        <input
                                            type="text"
                                            placeholder="Escribe el nombre del profesor..."
                                            value={searchQuery}
                                            onChange={(e) => setSearchQuery(e.target.value)}
                                            className="w-full pl-11 pr-4 py-3 bg-white border border-slate-200 rounded-2xl text-sm text-slate-900 font-medium placeholder-slate-400 focus:outline-none focus:border-sky-500 transition-all shadow-sm"
                                        />
                                        {searchQuery && (
                                            <div className="absolute left-0 right-0 top-full mt-2 z-50 bg-white border border-slate-200 rounded-2xl shadow-xl max-h-60 overflow-y-auto p-2">
                                                {loadingSearch && (
                                                    <div className="p-3 flex items-center justify-center gap-2 text-slate-400">
                                                        <Loader2 size={16} className="animate-spin" />
                                                        <span className="text-xs font-medium">Buscando...</span>
                                                    </div>
                                                )}
                                                {!loadingSearch && filteredTeachers.length > 0 ? (
                                                    filteredTeachers.map(t => (
                                                        <div
                                                            key={t.id}
                                                            onClick={() => {
                                                                toggleTeacher(t);
                                                                setSearchQuery('');
                                                            }}
                                                            className="p-3 hover:bg-sky-50 rounded-xl cursor-pointer text-sm font-bold text-slate-800 transition-all text-left"
                                                        >
                                                            {t.name}
                                                            <span className="block text-xs font-semibold text-slate-400 mt-0.5">{t.school}</span>
                                                        </div>
                                                    ))
                                                ) : (
                                                    !loadingSearch && <div className="p-3 text-xs font-bold text-slate-400 text-center">No se encontraron docentes</div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </div>
                                <div className="h-28 border-2 border-dashed border-slate-200 rounded-2xl flex flex-col items-center justify-center text-slate-400 text-sm mt-4 bg-slate-50/50">
                                    <Plus size={20} className="mb-1 text-slate-300" /> Usa el buscador
                                </div>
                            </div>
                        </div>
                    )}

                </div>

                {/* Comparison sections */}
                {displayTeachers.length >= 1 && (
                    <>
                        {loadingComparison && selectedIds.length >= 2 && (
                            <div className="flex items-center justify-center py-12">
                                <div className="text-center">
                                    <Loader2 className="w-8 h-8 animate-spin text-[#ff8a00] mx-auto mb-2" />
                                    <p className="text-slate-500 font-medium">Cargando comparación...</p>
                                </div>
                            </div>
                        )}
                        {!loadingComparison && selectedIds.length >= 2 && (
                            <>
                                <IASummary teachers={displayTeachers} />
                                <CompareMetrics teachers={displayTeachers} />
                                <StudentReviews teachers={displayTeachers} />
                            </>
                        )}
                        {!loadingComparison && selectedIds.length < 2 && (
                            <div className="text-center py-16 text-slate-400 font-medium text-sm border border-dashed border-slate-200 rounded-3xl bg-slate-50/50 mt-8">
                                Agrega al menos 2 profesores para ver la comparación detallada de métricas e IA.
                            </div>
                        )}
                    </>
                )}

            </div>
        </div>
    );
}
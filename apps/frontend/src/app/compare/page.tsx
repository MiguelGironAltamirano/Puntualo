'use client'

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Navbar } from '@/components/layout/Navbar';
import { Search, Plus, X, RotateCcw, Loader2, AlertCircle } from 'lucide-react';
import { Teacher } from '@/components/compare/types';
import { IASummary } from '@/components/compare/IASummary';
import { CompareMetrics } from '@/components/compare/CompareMetrics';
import { StudentReviews } from '@/components/compare/StudentReviews';
import { useProfessors, useCompareProfessors, useDebounce } from '@/lib/hooks';
import { ProfessorRead, ProfessorComparisonResponse } from '@/lib/api';

/**
 * Maps API ProfessorRead to compare Teacher type
 */
function mapProfessorToTeacher(professor: ProfessorRead): Teacher {
    return {
        id: professor.id,
        name: professor.full_name,
        course: 'Ver en perfil',
        school: `${professor.total_evaluations} evaluaciones`,
        rating: professor.global_score ?? 0,
        difficulty: 3.0, // Placeholder
        clarity: 3.5, // Placeholder
        takeAgain: '75%', // Placeholder
        avatar: '', // Will use default emoji
        tags: professor.validation_status === 'validated' ? ['Verificado'] : [],
        reviews: [],
        aiSummary: {
            pros: [],
            contras: []
        }
    };
}

export default function ComparePage() {
    const router = useRouter();
    const [slotA, setSlotA] = useState<Teacher | null>(null);
    const [slotB, setSlotB] = useState<Teacher | null>(null);
    const [searchA, setSearchA] = useState('');
    const [searchB, setSearchB] = useState('');

    // Debounce search inputs to reduce API calls while typing (300ms delay)
    const debouncedSearchA = useDebounce(searchA, 300);
    const debouncedSearchB = useDebounce(searchB, 300);

    // Memoize search params to prevent infinite fetch loops
    const paramsA = useMemo(() => ({
        search: debouncedSearchA,
        page: 1,
        page_size: 10,
    }), [debouncedSearchA]);

    const paramsB = useMemo(() => ({
        search: debouncedSearchB,
        page: 1,
        page_size: 10,
    }), [debouncedSearchB]);

    // Fetch professors for search A (uses debounced search)
    const { data: resultsA, loading: loadingA } = useProfessors(paramsA, !debouncedSearchA);

    // Fetch professors for search B (uses debounced search)
    const { data: resultsB, loading: loadingB } = useProfessors(paramsB, !debouncedSearchB);

    // Fetch comparison data when both professors are selected
    const selectedIds = useMemo(
        () => [slotA?.id, slotB?.id].filter((id): id is string => !!id),
        [slotA?.id, slotB?.id]
    );
    const { data: comparison, loading: loadingComparison, error: comparisonError } = useCompareProfessors(
        selectedIds.length === 2 ? selectedIds : null
    );

    // Map search results to Teacher type
    const filteredTeachersA = useMemo(
        () => resultsA?.items?.map(mapProfessorToTeacher).filter(t => t.id !== slotB?.id) ?? [],
        [resultsA?.items, slotB?.id]
    );

    const filteredTeachersB = useMemo(
        () => resultsB?.items?.map(mapProfessorToTeacher).filter(t => t.id !== slotA?.id) ?? [],
        [resultsB?.items, slotA?.id]
    );

    // Update slots with real comparison data when available
    const displaySlotA = slotA && comparison?.professors[0]
        ? {
            ...slotA,
            rating: comparison.professors[0].global_score ?? 0,
            clarity: comparison.professors[0].avg_clarity,
            difficulty: 5 - (comparison.professors[0].avg_easiness || 0),
            course: comparison.professors[0].common_courses?.[0]?.name || 'Ver en perfil',
        }
        : slotA;

    const displaySlotB = slotB && comparison?.professors[1]
        ? {
            ...slotB,
            rating: comparison.professors[1].global_score ?? 0,
            clarity: comparison.professors[1].avg_clarity,
            difficulty: 5 - (comparison.professors[1].avg_easiness || 0),
            course: comparison.professors[1].common_courses?.[0]?.name || 'Ver en perfil',
        }
        : slotB;

    return (
        <div className="min-h-screen bg-white font-sans text-slate-900">
            <Navbar />

            <div className="mx-auto max-w-[1400px] px-4 md:px-8 py-8">

                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10 pb-6 border-b border-slate-100">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-black text-[#0284c7] tracking-tight">Versus</h1>
                        <p className="text-sm text-slate-500 mt-1 font-medium">
                            Comparando docentes en paralelo. Contrasta sus métricas y opiniones.
                        </p>
                    </div>
                    {(displaySlotA || displaySlotB) && (
                        <button
                            onClick={() => { setSlotA(null); setSlotB(null); }}
                            className="flex items-center gap-2 px-4 py-2 justify-center border border-slate-200 bg-white hover:bg-slate-50 rounded-xl text-sm font-bold text-slate-700 transition-colors shadow-sm cursor-pointer w-full sm:w-auto shrink-0"
                        >
                            <RotateCcw className="w-4 h-4 text-slate-400" />
                            Limpiar Comparación
                        </button>
                    )}
                </div>

                {/* Comparison error */}
                {comparisonError && selectedIds.length === 2 && (
                    <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
                        <div>
                            <h3 className="text-sm font-bold text-red-900">Error al cargar comparación</h3>
                            <p className="text-xs text-red-600 mt-1">{comparisonError.message}</p>
                        </div>
                    </div>
                )}

                {/* Main 2-column layout */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-12">

                    {/* COLUMN A */}
                    <div className="relative">
                        {!displaySlotA ? (
                            <div className="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm">
                                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Seleccionar Primer Docente</h3>
                                <div className="relative">
                                    <Search className="absolute left-4 top-3.5 text-slate-400" size={18} />
                                    <input
                                        type="text"
                                        placeholder="Escribe el nombre del profesor..."
                                        value={searchA}
                                        onChange={(e) => setSearchA(e.target.value)}
                                        className="w-full pl-11 pr-4 py-3 bg-white border border-slate-200 rounded-2xl text-sm text-slate-900 font-medium placeholder-slate-400 focus:outline-none focus:border-sky-500 transition-all shadow-sm"
                                    />
                                    {searchA && (
                                        <div className="absolute left-0 right-0 top-full mt-2 z-50 bg-white border border-slate-200 rounded-2xl shadow-xl max-h-60 overflow-y-auto p-2">
                                            {loadingA && (
                                                <div className="p-3 flex items-center justify-center gap-2 text-slate-400">
                                                    <Loader2 size={16} className="animate-spin" />
                                                    <span className="text-xs font-medium">Buscando...</span>
                                                </div>
                                            )}
                                            {!loadingA && filteredTeachersA.length > 0 ? (
                                                filteredTeachersA.map(t => (
                                                    <div
                                                        key={t.id}
                                                        onClick={() => { setSlotA(t); setSearchA(''); }}
                                                        className="p-3 hover:bg-sky-50 rounded-xl cursor-pointer text-sm font-bold text-slate-800 transition-all"
                                                    >
                                                        {t.name}
                                                        <span className="block text-xs font-semibold text-slate-400 mt-0.5">{t.school}</span>
                                                    </div>
                                                ))
                                            ) : (
                                                !loadingA && <div className="p-3 text-xs font-bold text-slate-400 text-center">No se encontraron docentes</div>
                                            )}
                                        </div>
                                    )}
                                </div>
                                <div className="h-48 border-2 border-dashed border-slate-200 rounded-2xl flex flex-col items-center justify-center text-slate-400 text-sm mt-4 bg-slate-50/50">
                                    <Plus size={24} className="mb-2 text-slate-300" /> Usa el buscador
                                </div>
                            </div>
                        ) : (
                            <div className="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm relative">
                                <button onClick={() => setSlotA(null)} className="absolute right-4 top-4 p-1.5 bg-slate-50 hover:bg-red-50 hover:text-red-500 rounded-xl transition-all">
                                    <X size={16} />
                                </button>
                                <div className="flex flex-col items-center text-center py-4">
                                    {displaySlotA.avatar ? (
                                        <Image src={displaySlotA.avatar} alt={displaySlotA.name} width={64} height={64} className="w-16 h-16 rounded-full object-cover border border-slate-200 shadow-sm mb-3" />
                                    ) : (
                                        <div className="w-16 h-16 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-xl mb-3">👨‍🏫</div>
                                    )}
                                    <h2 className="text-lg font-black text-slate-900 leading-tight">{displaySlotA.name}</h2>
                                    <p className="text-xs font-bold text-slate-400 mt-1">{displaySlotA.school}</p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* COLUMN B */}
                    <div className="relative">
                        {!displaySlotB ? (
                            <div className="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm">
                                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Seleccionar Segundo Docente</h3>
                                <div className="relative">
                                    <Search className="absolute left-4 top-3.5 text-slate-400" size={18} />
                                    <input
                                        type="text"
                                        placeholder="Escribe el nombre del profesor..."
                                        value={searchB}
                                        onChange={(e) => setSearchB(e.target.value)}
                                        className="w-full pl-11 pr-4 py-3 bg-white border border-slate-200 rounded-2xl text-sm text-slate-900 font-medium placeholder-slate-400 focus:outline-none focus:border-sky-500 transition-all shadow-sm"
                                    />
                                    {searchB && (
                                        <div className="absolute left-0 right-0 top-full mt-2 z-50 bg-white border border-slate-200 rounded-2xl shadow-xl max-h-60 overflow-y-auto p-2">
                                            {loadingB && (
                                                <div className="p-3 flex items-center justify-center gap-2 text-slate-400">
                                                    <Loader2 size={16} className="animate-spin" />
                                                    <span className="text-xs font-medium">Buscando...</span>
                                                </div>
                                            )}
                                            {!loadingB && filteredTeachersB.length > 0 ? (
                                                filteredTeachersB.map(t => (
                                                    <div
                                                        key={t.id}
                                                        onClick={() => { setSlotB(t); setSearchB(''); }}
                                                        className="p-3 hover:bg-sky-50 rounded-xl cursor-pointer text-sm font-bold text-slate-800 transition-all"
                                                    >
                                                        {t.name}
                                                        <span className="block text-xs font-semibold text-slate-400 mt-0.5">{t.school}</span>
                                                    </div>
                                                ))
                                            ) : (
                                                !loadingB && <div className="p-3 text-xs font-bold text-slate-400 text-center">No se encontraron docentes</div>
                                            )}
                                        </div>
                                    )}
                                </div>
                                <div className="h-48 border-2 border-dashed border-slate-200 rounded-2xl flex flex-col items-center justify-center text-slate-400 text-sm mt-4 bg-slate-50/50">
                                    <Plus size={24} className="mb-2 text-slate-300" /> Usa el buscador
                                </div>
                            </div>
                        ) : (
                            <div className="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm relative">
                                <button onClick={() => setSlotB(null)} className="absolute right-4 top-4 p-1.5 bg-slate-50 hover:bg-red-50 hover:text-red-500 rounded-xl transition-all">
                                    <X size={16} />
                                </button>
                                <div className="flex flex-col items-center text-center py-4">
                                    {displaySlotB.avatar ? (
                                        <Image src={displaySlotB.avatar} alt={displaySlotB.name} width={64} height={64} className="w-16 h-16 rounded-full object-cover border border-slate-200 shadow-sm mb-3" />
                                    ) : (
                                        <div className="w-16 h-16 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-xl mb-3">👩‍🏫</div>
                                    )}
                                    <h2 className="text-lg font-black text-slate-900 leading-tight">{displaySlotB.name}</h2>
                                    <p className="text-xs font-bold text-slate-400 mt-1">{displaySlotB.school}</p>
                                </div>
                            </div>
                        )}
                    </div>

                </div>

                {/* Comparison sections */}
                {(displaySlotA || displaySlotB) && (
                    <>
                        {loadingComparison && selectedIds.length === 2 && (
                            <div className="flex items-center justify-center py-12">
                                <div className="text-center">
                                    <Loader2 className="w-8 h-8 animate-spin text-[#ff8a00] mx-auto mb-2" />
                                    <p className="text-slate-500 font-medium">Cargando comparación...</p>
                                </div>
                            </div>
                        )}
                        {!loadingComparison && selectedIds.length === 2 && (
                            <>
                                <IASummary slotA={displaySlotA} slotB={displaySlotB} />
                                <CompareMetrics slotA={displaySlotA} slotB={displaySlotB} />
                                <StudentReviews slotA={displaySlotA} slotB={displaySlotB} />
                            </>
                        )}
                    </>
                )}

            </div>
        </div>
    );
}
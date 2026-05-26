'use client'

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { CheckCircle2, Plus, User } from "lucide-react";
import { SearchAIAnalysis } from "./SearchAIAnalysis";
import { RegisterTeacherModal } from "./RegisterTeacherModal";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const PAGE_SIZE = 12;

type SortBy = "global_score" | "total_evaluations" | "created_at";

interface ProfessorOut {
    id: string;
    full_name: string;
    university_id: number;
    faculty_id: number;
    validation_status: "pending_validation" | "validated" | "not_found" | "rejected";
    global_score: number | null;
    total_evaluations: number;
    is_active: boolean;
    is_provisional: boolean;
    created_at: string;
    updated_at: string;
}

interface PaginatedProfessors {
    items: ProfessorOut[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
}

function ScoreBadge({ score }: { score: number | null }) {
    if (score === null) {
        return (
            <div className="bg-slate-100 text-slate-500 text-[11px] font-black px-2 py-0.5 rounded-lg shrink-0">
                Sin evaluaciones
            </div>
        );
    }
    return (
        <div className="bg-[#ff8a00] text-white text-[11px] font-black px-2 py-0.5 rounded-lg flex items-center gap-0.5 shadow-sm shrink-0">
            {score.toFixed(1)} ★
        </div>
    );
}

export default function TeacherCatalog({ initialQuery }: { initialQuery?: string }) {
    const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);
    const [items, setItems] = useState<ProfessorOut[]>([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [hasNext, setHasNext] = useState(false);
    const [sortBy, setSortBy] = useState<SortBy>("global_score");
    const [loading, setLoading] = useState(false);
    const [loadingMore, setLoadingMore] = useState(false);
    const [error, setError] = useState('');

    const fetchPage = useCallback(async (
        targetPage: number,
        replace: boolean,
        signal?: AbortSignal,
    ) => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            setError('Tu sesión expiró. Iniciá sesión de nuevo.');
            setItems([]);
            setTotal(0);
            return;
        }

        if (replace) setLoading(true); else setLoadingMore(true);
        setError('');

        const params = new URLSearchParams({
            page: String(targetPage),
            page_size: String(PAGE_SIZE),
            sort_by: sortBy,
            sort_order: 'desc',
        });
        if (initialQuery && initialQuery.trim()) {
            params.set('search', initialQuery.trim());
        }

        try {
            const res = await fetch(`${API_URL}/professors/?${params.toString()}`, {
                headers: { 'Authorization': `Bearer ${token}` },
                signal,
            });

            if (!res.ok) {
                if (res.status === 401) {
                    setError('Tu sesión expiró. Iniciá sesión de nuevo.');
                } else {
                    setError('No se pudo cargar el catálogo de profesores.');
                }
                if (replace) {
                    setItems([]);
                    setTotal(0);
                }
                return;
            }

            const data: PaginatedProfessors = await res.json();
            setItems((prev) => replace ? data.items : [...prev, ...data.items]);
            setTotal(data.total);
            setPage(data.page);
            setHasNext(data.has_next);
        } catch (err) {
            if ((err as Error).name === 'AbortError') return;
            setError('Error de conexión con el servidor');
            if (replace) {
                setItems([]);
                setTotal(0);
            }
        } finally {
            if (replace) setLoading(false); else setLoadingMore(false);
        }
    }, [initialQuery, sortBy]);

    useEffect(() => {
        const controller = new AbortController();
        fetchPage(1, true, controller.signal);
        return () => controller.abort();
    }, [fetchPage]);

    const handleLoadMore = () => {
        if (hasNext && !loadingMore) {
            fetchPage(page + 1, false);
        }
    };

    const handleProfessorCreated = () => {
        fetchPage(1, true);
    };

    const analysisText = initialQuery && initialQuery.trim()
        ? `Mostrando profesores que coinciden con "${initialQuery}".`
        : items.length > 0
            ? `Mostrando ${items.length} de ${total} profesores del catálogo.`
            : '';

    return (
        <div className="flex-1 p-8 bg-[#f8fafc]/40 text-left overflow-y-auto h-[calc(100vh-69px)]">
            <div className="max-w-[1300px] mx-auto">

                {analysisText && (
                    <SearchAIAnalysis analysis={{ matchesText: analysisText }} />
                )}

                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
                    <div>
                        <h1 className="text-xl font-black text-slate-900 tracking-tight">Resultados de búsqueda</h1>
                        <p className="text-xs text-slate-400 mt-1 font-medium">
                            {loading
                                ? 'Cargando...'
                                : total === 0
                                    ? 'Sin resultados'
                                    : `Mostrando ${items.length} de ${total} profesores`}
                        </p>
                    </div>

                    <div className="flex items-center gap-5 self-end sm:self-auto">
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
                </div>

                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm font-medium">
                        {error}
                    </div>
                )}

                {!error && !loading && items.length === 0 && (
                    <div className="bg-white border border-dashed border-slate-200 rounded-2xl p-12 text-center">
                        <p className="text-sm text-slate-500 font-medium">
                            {initialQuery
                                ? `No encontramos profesores que coincidan con "${initialQuery}".`
                                : 'Aún no hay profesores en el catálogo.'}
                        </p>
                        <p className="text-xs text-slate-400 mt-1">
                            Probá registrar uno con el botón de arriba.
                        </p>
                    </div>
                )}

                {loading && items.length === 0 && (
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                        {Array.from({ length: 6 }).map((_, i) => (
                            <div
                                key={i}
                                className="border border-slate-100 bg-white rounded-2xl p-6 min-h-[180px] animate-pulse"
                            >
                                <div className="flex items-center gap-3.5">
                                    <div className="w-12 h-12 rounded-full bg-slate-100" />
                                    <div className="flex-1 space-y-2">
                                        <div className="h-3 bg-slate-100 rounded w-3/4" />
                                        <div className="h-2 bg-slate-100 rounded w-1/2" />
                                    </div>
                                </div>
                                <div className="mt-6 h-2 bg-slate-100 rounded w-1/3" />
                            </div>
                        ))}
                    </div>
                )}

                {items.length > 0 && (
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                        {items.map((prof) => (
                            <Link
                                key={prof.id}
                                href={`/teachers/${prof.id}`}
                                className="border border-slate-100 bg-white rounded-2xl p-6 shadow-[0_4px_25px_rgba(0,0,0,0.02)] hover:shadow-[0_4px_30px_rgba(0,0,0,0.05)] transition-all flex flex-col justify-between relative min-h-[180px] no-underline group cursor-pointer"
                            >
                                <div className="flex items-start justify-between gap-3 mb-5">
                                    <div className="flex items-center gap-3.5">
                                        <div className="w-12 h-12 rounded-full border border-slate-100 bg-slate-50 shrink-0 flex items-center justify-center text-slate-400">
                                            <User className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <h3 className="text-sm font-black text-slate-900 tracking-tight leading-snug group-hover:text-[#0284c7] transition-colors">
                                                {prof.full_name}
                                            </h3>
                                            <p className="text-[11px] font-semibold text-slate-400 mt-0.5 flex items-center gap-1">
                                                {prof.validation_status === "validated" && (
                                                    <CheckCircle2 className="w-3 h-3 text-sky-500" />
                                                )}
                                                {prof.is_provisional
                                                    ? 'Pendiente de validación'
                                                    : prof.validation_status === "validated"
                                                        ? 'Validado'
                                                        : prof.validation_status === "not_found"
                                                            ? 'No encontrado en fuentes'
                                                            : prof.validation_status}
                                            </p>
                                        </div>
                                    </div>
                                    <ScoreBadge score={prof.global_score} />
                                </div>

                                <div className="flex items-center justify-between gap-2 pt-4 border-t border-slate-50 mt-auto">
                                    <div className="text-[11px] font-semibold text-slate-500">
                                        {prof.total_evaluations === 0
                                            ? 'Sin evaluaciones aún'
                                            : `${prof.total_evaluations} evaluación${prof.total_evaluations === 1 ? '' : 'es'}`}
                                    </div>
                                    {prof.is_provisional && (
                                        <span className="px-2 py-0.5 bg-amber-50 text-amber-700 border border-amber-200 font-bold text-[9px] rounded-md tracking-wider uppercase">
                                            Provisional
                                        </span>
                                    )}
                                </div>
                            </Link>
                        ))}
                    </div>
                )}

                {hasNext && items.length > 0 && (
                    <div className="mt-8 flex justify-center">
                        <button
                            type="button"
                            onClick={handleLoadMore}
                            disabled={loadingMore}
                            className="px-6 py-2.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-bold rounded-xl transition-colors shadow-sm cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loadingMore ? 'Cargando...' : 'Cargar más'}
                        </button>
                    </div>
                )}

                <RegisterTeacherModal
                    isOpen={isRegisterModalOpen}
                    onClose={() => setIsRegisterModalOpen(false)}
                    onCreated={handleProfessorCreated}
                />
            </div>
        </div>
    );
}

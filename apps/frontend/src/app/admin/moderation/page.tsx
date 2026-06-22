'use client'

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { AlertCircle, CheckCircle, Trash2, Eye, EyeOff, Loader2 } from 'lucide-react';
import { adminAPI, PendingModerationItem, PaginatedResponse } from '@/lib/api';

interface ModerationItem extends PendingModerationItem {
    expanded?: boolean;
}

export default function ModerationDashboard() {
    const router = useRouter();
    const [items, setItems] = useState<ModerationItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [decidingComment, setDecidingComment] = useState<string | null>(null);
    const [decisionLoading, setDecisionLoading] = useState(false);

    const fetchPending = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await adminAPI.getPendingModerations({
                page,
                page_size: 20,
            }) as PaginatedResponse<PendingModerationItem>;
            
            setItems(response.items.map(item => ({ ...item, expanded: false })));
            setTotalPages(response.total_pages);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Error fetching pending moderations');
        } finally {
            setLoading(false);
        }
    }, [page]);

    useEffect(() => {
        fetchPending();
    }, [fetchPending]);

    const handleDecision = async (
        commentId: string,
        decision: 'allow' | 'remove',
        reason?: string
    ) => {
        setDecidingComment(commentId);
        setDecisionLoading(true);

        try {
            await adminAPI.submitDecision(commentId, {
                comment_id: commentId,
                decision,
                reason,
            });

            // Remove from list
            setItems(items.filter(item => item.comment_id !== commentId));
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Error submitting decision');
        } finally {
            setDecidingComment(null);
            setDecisionLoading(false);
        }
    };

    const toggleExpanded = (commentId: string) => {
        setItems(items.map(item =>
            item.comment_id === commentId
                ? { ...item, expanded: !item.expanded }
                : item
        ));
    };

    if (loading && items.length === 0) {
        return (
            <div className="min-h-screen bg-slate-50 flex items-center justify-center">
                <div className="flex flex-col items-center gap-3">
                    <Loader2 className="w-8 h-8 animate-spin text-[#ff8a00]" />
                    <p className="text-slate-600 font-medium">Cargando comentarios pendientes...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50 p-8">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-black text-slate-900 mb-2">Panel de Moderación</h1>
                    <p className="text-slate-600">Revisa y toma decisiones sobre comentarios reportados o marcados como spam.</p>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-4 mb-8">
                    <div className="bg-white rounded-xl border border-slate-200 p-4">
                        <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Pendientes</p>
                        <p className="text-2xl font-black text-slate-900">{items.length}</p>
                    </div>
                    <div className="bg-white rounded-xl border border-slate-200 p-4">
                        <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Página</p>
                        <p className="text-2xl font-black text-slate-900">{page}/{totalPages}</p>
                    </div>
                    <div className="bg-white rounded-xl border border-slate-200 p-4">
                        <p className="text-xs font-semibold text-slate-500 uppercase mb-1">Estado</p>
                        <p className="text-2xl font-black text-orange-600">Activo</p>
                    </div>
                </div>

                {/* Error */}
                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-red-700">{error}</p>
                    </div>
                )}

                {/* Empty State */}
                {!loading && items.length === 0 && (
                    <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
                        <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
                        <h2 className="text-xl font-black text-slate-900 mb-2">¡Sin pendientes!</h2>
                        <p className="text-slate-600">No hay comentarios pendientes de revisar en este momento.</p>
                    </div>
                )}

                {/* Items List */}
                <div className="space-y-4">
                    {items.map((item) => (
                        <div
                            key={item.comment_id}
                            className="bg-white rounded-xl border border-slate-200 overflow-hidden transition-all hover:border-slate-300"
                        >
                            {/* Summary */}
                            <div className="p-4 flex items-start justify-between gap-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-3">
                                        <button
                                            onClick={() => toggleExpanded(item.comment_id)}
                                            className="text-slate-400 hover:text-slate-600"
                                        >
                                            {item.expanded ? (
                                                <EyeOff className="w-4 h-4" />
                                            ) : (
                                                <Eye className="w-4 h-4" />
                                            )}
                                        </button>
                                        <div>
                                            <p className="text-xs font-semibold text-slate-500">
                                                Comentario ID: <code className="text-slate-700">{item.comment_id.substring(0, 8)}...</code>
                                            </p>
                                            <p className="text-xs text-slate-400 mt-0.5">
                                                {new Date(item.created_at).toLocaleDateString('es-PE', {
                                                    year: 'numeric',
                                                    month: 'short',
                                                    day: 'numeric',
                                                    hour: '2-digit',
                                                    minute: '2-digit',
                                                })}
                                            </p>
                                        </div>
                                    </div>

                                    {/* Flags & Scores */}
                                    <div className="space-y-2">
                                        {item.heuristic_flags.length > 0 && (
                                            <div className="flex flex-wrap gap-1.5">
                                                {item.heuristic_flags.map((flag) => (
                                                    <span
                                                        key={flag}
                                                        className="px-2 py-1 bg-red-50 text-red-700 border border-red-200 text-[10px] font-semibold rounded-md"
                                                    >
                                                        {flag}
                                                    </span>
                                                ))}
                                            </div>
                                        )}
                                        <div className="flex items-center gap-4 text-[11px]">
                                            <div>
                                                <span className="text-slate-500">Reportes:</span>
                                                <span className="font-bold text-slate-900 ml-1">{item.report_count}</span>
                                            </div>
                                            <div>
                                                <span className="text-slate-500">Puntuación:</span>
                                                <span className="font-bold text-slate-900 ml-1">{item.weighted_score.toFixed(2)}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Quick Actions */}
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => handleDecision(item.comment_id, 'allow')}
                                        disabled={decisionLoading && decidingComment === item.comment_id}
                                        className="px-3 py-2 bg-green-100 hover:bg-green-200 text-green-700 font-semibold text-xs rounded-lg transition-colors disabled:opacity-50 flex items-center gap-1"
                                    >
                                        <CheckCircle className="w-3.5 h-3.5" />
                                        Permitir
                                    </button>
                                    <button
                                        onClick={() => handleDecision(item.comment_id, 'remove')}
                                        disabled={decisionLoading && decidingComment === item.comment_id}
                                        className="px-3 py-2 bg-red-100 hover:bg-red-200 text-red-700 font-semibold text-xs rounded-lg transition-colors disabled:opacity-50 flex items-center gap-1"
                                    >
                                        <Trash2 className="w-3.5 h-3.5" />
                                        Remover
                                    </button>
                                </div>
                            </div>

                            {/* Expanded Content */}
                            {item.expanded && (
                                <div className="border-t border-slate-100 p-4 bg-slate-50">
                                    <div className="bg-white p-3 rounded-lg border border-slate-200">
                                        <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-wrap">
                                            {item.text}
                                        </p>
                                    </div>
                                    <div className="mt-3 grid grid-cols-2 gap-2 text-[10px]">
                                        <div>
                                            <span className="text-slate-500">Usuario:</span>
                                            <p className="font-mono text-slate-700">{item.user_id.substring(0, 8)}...</p>
                                        </div>
                                        <div>
                                            <span className="text-slate-500">Profesor:</span>
                                            <p className="font-mono text-slate-700">{item.professor_id.substring(0, 8)}...</p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                    <div className="mt-8 flex items-center justify-between">
                        <button
                            onClick={() => setPage(Math.max(1, page - 1))}
                            disabled={page === 1 || loading}
                            className="px-4 py-2 bg-white border border-slate-200 rounded-lg font-semibold text-sm hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            ← Anterior
                        </button>
                        <p className="text-sm text-slate-600 font-medium">
                            Página {page} de {totalPages}
                        </p>
                        <button
                            onClick={() => setPage(Math.min(totalPages, page + 1))}
                            disabled={page === totalPages || loading}
                            className="px-4 py-2 bg-white border border-slate-200 rounded-lg font-semibold text-sm hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Siguiente →
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

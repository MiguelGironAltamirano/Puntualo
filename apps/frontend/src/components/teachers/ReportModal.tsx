'use client'

import { useState } from 'react';
import { X, Flag, AlertCircle, Loader2 } from 'lucide-react';

interface ReportModalProps {
    isOpen: boolean;
    onClose: () => void;
    commentId?: string;
    professorId?: string;
    onReportSubmitted?: () => void;
}

export type ReportReason = 
    | 'spam'
    | 'hate_speech'
    | 'harassment'
    | 'off_topic'
    | 'false_information'
    | 'impersonation'
    | 'privacy_violation'
    | 'other';

const REASON_LABELS: Record<ReportReason, string> = {
    'spam': 'Spam',
    'hate_speech': 'Contenido ofensivo / Discurso de odio',
    'harassment': 'Acoso o intimidación',
    'off_topic': 'No es sobre el docente',
    'false_information': 'Información falsa o engañosa',
    'impersonation': 'Suplantación de identidad',
    'privacy_violation': 'Violación de privacidad',
    'other': 'Otro',
};

export function ReportModal({ 
    isOpen, 
    onClose, 
    commentId, 
    professorId,
    onReportSubmitted 
}: ReportModalProps) {
    const [reason, setReason] = useState<ReportReason | null>(null);
    const [details, setDetails] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    if (!isOpen) return null;

    const reasons: ReportReason[] = [
        'spam',
        'hate_speech',
        'harassment',
        'off_topic',
        'false_information',
        'impersonation',
        'privacy_violation',
        'other'
    ];

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!reason) return;

        setIsSubmitting(true);
        setError(null);

        try {
            const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

            const response = await fetch(`${API_BASE_URL}/evaluations/${commentId}/report`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
                },
                body: JSON.stringify({
                    reason,
                    details: details.trim() || undefined,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                
                if (response.status === 429) {
                    throw new Error('Has enviado demasiados reportes. Intenta más tarde.');
                } else if (response.status === 403) {
                    throw new Error('Has sido marcado como usuario abusivo y no puedes reportar.');
                } else if (response.status === 400) {
                    throw new Error(errorData?.detail?.message || 'Error al enviar el reporte.');
                } else {
                    throw new Error('Error al enviar el reporte. Intenta de nuevo.');
                }
            }

            setSuccess(true);
            setTimeout(() => {
                onReportSubmitted?.();
                onClose();
            }, 1500);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Error desconocido');
        } finally {
            setIsSubmitting(false);
        }
    };

    if (success) {
        return (
            <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4 overflow-y-auto animate-fadeIn">
                <div className="bg-white rounded-3xl border border-slate-100 w-full max-w-sm p-6 relative shadow-2xl my-auto text-center">
                    <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
                        <Flag className="w-6 h-6 text-green-600" />
                    </div>
                    <h2 className="text-lg font-black text-[#0f172a] tracking-tight mb-2">¡Reporte enviado!</h2>
                    <p className="text-xs text-slate-500 font-medium">Gracias por ayudarnos a mantener la comunidad segura.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4 overflow-y-auto animate-fadeIn">
            <div className="bg-white rounded-3xl border border-slate-100 w-full max-w-sm p-4 sm:p-6 relative shadow-2xl my-auto text-left">
                <button onClick={onClose} className="absolute right-4 top-4 text-slate-400 hover:text-slate-600 hover:bg-slate-50 rounded-xl transition-all p-1.5 cursor-pointer focus:outline-none">
                    <X className="w-5 h-5" />
                </button>
                
                <div className="mb-6 border-b border-slate-100 pb-4">
                    <h2 className="text-lg font-black text-[#0f172a] tracking-tight mb-1">Reportar Comentario</h2>
                    <p className="text-xs text-slate-500 font-medium leading-relaxed">Ayúdanos a mantener la comunidad segura y respetuosa.</p>
                </div>

                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl flex items-start gap-2">
                        <AlertCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                        <p className="text-xs font-medium text-red-700">{error}</p>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="text-[11px] font-black text-slate-700 uppercase tracking-wider block mb-3">¿Por qué reportas este comentario?</label>
                        <div className="space-y-2.5">
                            {reasons.map((r) => (
                                <label key={r} className={`flex items-center gap-3 p-3.5 rounded-xl border cursor-pointer transition-all ${reason === r ? 'border-[#0284c7] bg-sky-50' : 'border-slate-200 hover:border-slate-300'}`}>
                                    <input 
                                        type="radio" 
                                        name="reportReason" 
                                        value={r} 
                                        checked={reason === r} 
                                        onChange={() => setReason(r)} 
                                        className="w-4 h-4 text-[#0284c7] border-gray-300 focus:ring-[#0284c7] cursor-pointer"
                                    />
                                    <span className="text-xs font-semibold text-slate-700">{REASON_LABELS[r]}</span>
                                </label>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="text-[11px] font-black text-slate-700 uppercase tracking-wider block mb-2">Detalles adicionales (opcional)</label>
                        <textarea
                            rows={3}
                            value={details}
                            onChange={(e) => setDetails(e.target.value)}
                            placeholder="Proporciona más contexto para ayudarnos a revisar el reporte..."
                            disabled={isSubmitting}
                            className="w-full bg-white border border-slate-200 rounded-xl p-3 text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-[#ff8a00] focus:ring-2 focus:ring-orange-50 transition-all resize-none shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                        />
                    </div>

                    {/* Footer Actions */}
                    <div className="flex items-center justify-end gap-3 pt-2">
                        <button type="button" onClick={onClose} className="px-5 py-3 text-xs font-bold text-slate-600 bg-white border border-slate-200 hover:bg-slate-50 rounded-xl transition-colors cursor-pointer">
                            Cancelar
                        </button>
                        <button type="submit" disabled={!reason} className="px-5 py-3 bg-[#ff8a00] hover:bg-[#ea580c] disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-xs rounded-xl transition-all shadow-sm flex items-center gap-1.5 cursor-pointer">
                            <Flag className="w-3.5 h-3.5" /> Enviar Reporte
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

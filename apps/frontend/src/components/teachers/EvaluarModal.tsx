'use client'

import { useState } from 'react';
import { X, Star, ChevronDown, Play, User } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const MODALITIES = [
    { value: 'presencial', label: 'Presencial' },
    { value: 'virtual', label: 'Virtual' },
    { value: 'ambas', label: 'Ambas (híbrida)' },
] as const;

type Modality = typeof MODALITIES[number]['value'];

interface CourseOption {
    id: number;
    name: string;
}

export interface EvaluationCreated {
    id: string;
    professor_id: string;
    course_id: number;
    clarity: number;
    easiness: number;
    helpfulness: number;
    punctuality: number;
    modality: string;
    created_at: string;
    comment: {
        id: string;
        text: string | null;
        modality: string;
        like_count: number;
        dislike_count: number;
        created_at: string;
    } | null;
    hashtags: string[];
}

interface EvaluarModalProps {
    isOpen: boolean;
    onClose: () => void;
    professorId: string;
    professorName: string;
    facultyName?: string | null;
    courses: CourseOption[];
    isValidated: boolean;
    onCreated?: (evaluation: EvaluationCreated) => void;
}

function extractErrorMessage(detail: unknown, fallback: string): string {
    if (typeof detail === 'string') return detail;
    if (detail && typeof detail === 'object' && 'message' in detail) {
        const msg = (detail as { message?: unknown }).message;
        if (typeof msg === 'string') return msg;
    }
    return fallback;
}

function StarRating({ value, onChange, disabled }: { value: number, onChange: (val: number) => void, disabled?: boolean }) {
    return (
        <div className="flex items-center justify-center gap-2 mt-2">
            {[1, 2, 3, 4, 5].map((star) => (
                <button
                    key={star}
                    type="button"
                    onClick={() => !disabled && onChange(star)}
                    disabled={disabled}
                    className="p-2 transition-all focus:outline-none hover:scale-110 disabled:hover:scale-100 disabled:cursor-not-allowed cursor-pointer"
                >
                    <Star className={`w-8 h-8 ${star <= value ? 'fill-[#ff8a00] text-[#ff8a00]' : 'text-slate-200'}`} />
                </button>
            ))}
        </div>
    );
}

export function EvaluarModal({
    isOpen,
    onClose,
    professorId,
    professorName,
    facultyName,
    courses,
    isValidated,
    onCreated,
}: EvaluarModalProps) {
    const [clarity, setClarity] = useState(0);
    const [easiness, setEasiness] = useState(0);
    const [helpfulness, setHelpfulness] = useState(0);
    const [punctuality, setPunctuality] = useState(0);

    const [courseId, setCourseId] = useState<string>('');
    const [modality, setModality] = useState<Modality | ''>('');

    const [commentText, setCommentText] = useState('');
    const [hashtagsInput, setHashtagsInput] = useState('');

    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    const resetAndClose = () => {
        setClarity(0);
        setEasiness(0);
        setHelpfulness(0);
        setPunctuality(0);
        setCourseId('');
        setModality('');
        setCommentText('');
        setHashtagsInput('');
        setSubmitting(false);
        setError('');
        setSuccess(false);
        onClose();
    };

    if (!isOpen) return null;

    const hashtags = hashtagsInput
        .split(/[,\s]+/)
        .map((h) => h.trim().replace(/^#/, ''))
        .filter(Boolean);

    const hashtagsValid = hashtags.length <= 5;
    const commentValid = commentText.length === 0 || commentText.trim().length >= 20;

    const canSubmit =
        isValidated &&
        courses.length > 0 &&
        !submitting &&
        !success &&
        clarity > 0 &&
        easiness > 0 &&
        helpfulness > 0 &&
        punctuality > 0 &&
        Boolean(courseId) &&
        Boolean(modality) &&
        hashtagsValid &&
        commentValid;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!isValidated) {
            setError('No podés evaluar a un profesor aún no validado.');
            return;
        }
        if (courses.length === 0) {
            setError('Este profesor no tiene cursos asignados todavía.');
            return;
        }
        if (!commentValid) {
            setError('El comentario debe tener al menos 20 caracteres (o dejalo vacío).');
            return;
        }
        if (!hashtagsValid) {
            setError('Máximo 5 hashtags.');
            return;
        }

        const token = localStorage.getItem('access_token');
        if (!token) {
            setError('Tu sesión expiró. Iniciá sesión de nuevo.');
            return;
        }

        const trimmedComment = commentText.trim();
        const body: Record<string, unknown> = {
            professor_id: professorId,
            course_id: Number(courseId),
            clarity,
            easiness,
            helpfulness,
            punctuality,
            modality,
        };
        if (trimmedComment.length > 0) {
            body.comment_text = trimmedComment;
        }
        if (hashtags.length > 0) {
            body.hashtags = hashtags;
        }

        setSubmitting(true);

        try {
            const res = await fetch(`${API_URL}/evaluations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(body),
            });

            if (!res.ok) {
                const data = await res.json().catch(() => null);
                const detail = data?.detail;

                if (res.status === 401) {
                    setError('Tu sesión expiró. Iniciá sesión de nuevo.');
                } else if (res.status === 403) {
                    const code = detail && typeof detail === 'object' && 'code' in detail
                        ? (detail as { code?: string }).code
                        : '';
                    if (code === 'PROFESSOR_NOT_VALIDATED') {
                        setError('Este profesor todavía no fue validado, no se puede evaluar.');
                    } else {
                        setError('Necesitás verificar tu identidad para evaluar profesores.');
                    }
                } else if (res.status === 404) {
                    setError(extractErrorMessage(detail, 'Profesor o curso no encontrado.'));
                } else if (res.status === 409) {
                    setError('Ya evaluaste a este profesor para ese curso en este semestre.');
                } else if (res.status === 422) {
                    setError(extractErrorMessage(detail, 'Datos inválidos. Revisá los campos.'));
                } else {
                    setError(extractErrorMessage(detail, 'No se pudo registrar la evaluación.'));
                }
                setSubmitting(false);
                return;
            }

            const data = await res.json() as EvaluationCreated;
            setSuccess(true);
            setSubmitting(false);
            onCreated?.(data);
            setTimeout(() => {
                resetAndClose();
            }, 1200);
        } catch {
            setError('Error de conexión con el servidor');
            setSubmitting(false);
        }
    };

    const interactionsDisabled = !isValidated || courses.length === 0 || submitting || success;

    return (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4 overflow-y-auto animate-fadeIn">
            <div className="bg-white rounded-3xl w-full max-w-2xl relative shadow-2xl my-auto text-left flex flex-col h-full sm:h-auto max-h-[95vh] sm:max-h-[90vh]">

                {/* Header */}
                <div className="p-4 sm:p-6 border-b border-slate-100 flex items-center gap-4 shrink-0 relative">
                    <button onClick={resetAndClose} className="absolute right-4 top-4 sm:right-6 sm:top-6 text-slate-400 hover:text-slate-600 transition-colors p-1.5 cursor-pointer focus:outline-none hover:bg-slate-50 rounded-xl">
                        <X className="w-5 h-5" />
                    </button>

                    <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-slate-100 border border-slate-200 shrink-0 flex items-center justify-center text-slate-400">
                        <User className="w-5 h-5 sm:w-6 sm:h-6" />
                    </div>
                    <div>
                        <h2 className="text-base sm:text-lg font-black text-slate-900 leading-tight">{professorName}</h2>
                        {facultyName && (
                            <p className="text-[10px] sm:text-xs font-semibold text-slate-500 mt-0.5">{facultyName}</p>
                        )}
                    </div>
                </div>

                {/* Banners */}
                {!isValidated && (
                    <div className="px-4 sm:px-8 pt-4 sm:pt-6">
                        <div className="p-3 bg-amber-50 border border-amber-200 text-amber-800 rounded-lg text-xs font-medium">
                            Este profesor todavía está en validación. Podrás evaluarlo cuando quede aprobado por el pipeline.
                        </div>
                    </div>
                )}
                {isValidated && courses.length === 0 && (
                    <div className="px-4 sm:px-8 pt-4 sm:pt-6">
                        <div className="p-3 bg-amber-50 border border-amber-200 text-amber-800 rounded-lg text-xs font-medium">
                            Este profesor todavía no tiene cursos asignados. No es posible evaluarlo.
                        </div>
                    </div>
                )}

                {/* Scrollable content */}
                <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto">
                    <div className="p-4 sm:p-8 space-y-8 sm:space-y-10 custom-scrollbar">

                        {error && (
                            <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-xs font-medium">
                                {error}
                            </div>
                        )}
                        {success && (
                            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-lg text-xs font-medium">
                                Evaluación registrada. ¡Gracias por tu aporte!
                            </div>
                        )}

                        {/* Calificaciones */}
                        <div>
                            <h3 className="text-xs font-black text-[#0284c7] uppercase tracking-wider mb-4 flex items-center gap-2">
                                <Star className="w-4 h-4" /> Calificaciones generales
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100 text-center shadow-sm">
                                    <span className="text-[9px] font-black text-slate-700 uppercase tracking-widest block">Claridad de las clases</span>
                                    <StarRating value={clarity} onChange={setClarity} disabled={interactionsDisabled} />
                                </div>
                                <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100 text-center shadow-sm">
                                    <span className="text-[9px] font-black text-slate-700 uppercase tracking-widest block">Nivel de facilidad</span>
                                    <StarRating value={easiness} onChange={setEasiness} disabled={interactionsDisabled} />
                                </div>
                                <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100 text-center shadow-sm">
                                    <span className="text-[9px] font-black text-slate-700 uppercase tracking-widest block">Disposición para ayudar</span>
                                    <StarRating value={helpfulness} onChange={setHelpfulness} disabled={interactionsDisabled} />
                                </div>
                                <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100 text-center shadow-sm">
                                    <span className="text-[9px] font-black text-slate-700 uppercase tracking-widest block">Puntualidad</span>
                                    <StarRating value={punctuality} onChange={setPunctuality} disabled={interactionsDisabled} />
                                </div>
                            </div>
                        </div>

                        {/* Curso y modalidad */}
                        <div>
                            <h3 className="text-xs font-black text-[#0284c7] uppercase tracking-wider mb-4">
                                Curso y modalidad
                            </h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="text-[9px] font-black text-slate-700 uppercase tracking-widest block mb-2">Curso</label>
                                    <div className="relative">
                                        <select
                                            value={courseId}
                                            onChange={(e) => setCourseId(e.target.value)}
                                            disabled={interactionsDisabled || courses.length === 0}
                                            required
                                            className="w-full bg-white border border-slate-200 text-xs font-medium text-slate-600 rounded-xl pl-4 pr-10 py-3.5 appearance-none focus:outline-none focus:border-sky-300 transition-colors shadow-sm cursor-pointer disabled:bg-slate-50 disabled:cursor-not-allowed"
                                        >
                                            <option value="" disabled>
                                                {courses.length === 0 ? 'Sin cursos disponibles' : 'Elegí el curso que tomaste...'}
                                            </option>
                                            {courses.map((c) => (
                                                <option key={c.id} value={c.id}>{c.name}</option>
                                            ))}
                                        </select>
                                        <ChevronDown className="w-4 h-4 absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                                    </div>
                                </div>
                                <div>
                                    <label className="text-[9px] font-black text-slate-700 uppercase tracking-widest block mb-2">Modalidad</label>
                                    <div className="relative">
                                        <select
                                            value={modality}
                                            onChange={(e) => setModality(e.target.value as Modality)}
                                            disabled={interactionsDisabled}
                                            required
                                            className="w-full bg-white border border-slate-200 text-xs font-medium text-slate-600 rounded-xl pl-4 pr-10 py-3.5 appearance-none focus:outline-none focus:border-sky-300 transition-colors shadow-sm cursor-pointer disabled:bg-slate-50 disabled:cursor-not-allowed"
                                        >
                                            <option value="" disabled>Seleccioná modalidad</option>
                                            {MODALITIES.map((m) => (
                                                <option key={m.value} value={m.value}>{m.label}</option>
                                            ))}
                                        </select>
                                        <ChevronDown className="w-4 h-4 absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                                    </div>
                                </div>
                            </div>
                            <p className="text-[10px] font-medium text-slate-400 mt-2">
                                El semestre lo asigna automáticamente el sistema.
                            </p>
                        </div>

                        {/* Reseña */}
                        <div>
                            <h3 className="text-xs font-black text-[#0284c7] uppercase tracking-wider mb-4">
                                Tu reseña (opcional)
                            </h3>

                            <div className="space-y-4">
                                <div>
                                    <label className="text-[9px] font-black text-slate-700 uppercase tracking-widest block mb-2">Comentario</label>
                                    <textarea
                                        rows={4}
                                        value={commentText}
                                        onChange={(e) => setCommentText(e.target.value)}
                                        disabled={interactionsDisabled}
                                        maxLength={2000}
                                        placeholder="Describí tu experiencia. Si dejás comentario, debe tener al menos 20 caracteres."
                                        className="w-full bg-white border border-slate-200 rounded-xl p-4 text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-300 transition-all resize-none shadow-sm disabled:bg-slate-50 disabled:cursor-not-allowed"
                                    />
                                    <div className="flex justify-between mt-1.5">
                                        {!commentValid && (
                                            <span className="text-[9px] font-bold text-red-500">Min. 20 caracteres</span>
                                        )}
                                        <span className="text-[9px] font-bold text-slate-400 ml-auto">{commentText.length} / 2000</span>
                                    </div>
                                </div>
                                <div>
                                    <label className="text-[9px] font-black text-slate-700 uppercase tracking-widest block mb-2">
                                        Hashtags <span className="text-slate-400 font-medium normal-case">(máximo 5, separados por coma)</span>
                                    </label>
                                    <div className="relative shadow-sm rounded-xl">
                                        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-black text-sm">#</span>
                                        <input
                                            type="text"
                                            value={hashtagsInput}
                                            onChange={(e) => setHashtagsInput(e.target.value)}
                                            disabled={interactionsDisabled}
                                            placeholder="practico, exigente, claro"
                                            className="w-full bg-white border border-slate-200 rounded-xl pl-8 pr-4 py-3 text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-300 transition-all disabled:bg-slate-50 disabled:cursor-not-allowed"
                                        />
                                    </div>
                                    {!hashtagsValid && (
                                        <span className="text-[9px] font-bold text-red-500 mt-1 block">Máximo 5 hashtags</span>
                                    )}
                                    {hashtags.length > 0 && hashtagsValid && (
                                        <div className="flex flex-wrap gap-1.5 mt-2">
                                            {hashtags.map((h) => (
                                                <span key={h} className="px-2 py-0.5 bg-[#e0f2fe] text-[#0284c7] font-bold text-[9px] rounded-md">
                                                    #{h}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Footer Actions */}
                    <div className="p-4 sm:p-6 border-t border-slate-100 flex items-center justify-end gap-4 sm:gap-6 shrink-0 bg-white rounded-b-3xl sticky bottom-0">
                        <button
                            type="button"
                            onClick={resetAndClose}
                            disabled={submitting}
                            className="px-4 py-2.5 sm:px-5 sm:py-3 text-[11px] font-bold uppercase tracking-wider text-slate-500 hover:text-slate-800 hover:bg-slate-50 rounded-xl transition-all focus:outline-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            disabled={!canSubmit}
                            className={`px-5 py-2.5 sm:px-6 sm:py-3 font-bold text-[11px] uppercase tracking-wider rounded-xl transition-all shadow-sm flex items-center gap-2 focus:outline-none ${
                                canSubmit
                                    ? 'bg-[#ff8a00] hover:bg-[#ea580c] text-white cursor-pointer'
                                    : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                            }`}
                        >
                            <Play className="w-3.5 h-3.5 fill-current" />
                            {submitting ? 'Publicando...' : 'Publicar'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

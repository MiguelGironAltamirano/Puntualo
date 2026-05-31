'use client'

import { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Navbar } from "@/components/layout/Navbar";
import { CommentList, CommentRead, ReactionType } from "@/components/teachers/CommentList";
import { EvaluarModal, EvaluationCreated } from "@/components/teachers/EvaluarModal";
import { ArrowLeft, Bookmark, ClipboardList, GraduationCap, MessageSquare, User } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface CourseRef {
    id: number;
    name: string;
    faculty_id: number;
}

interface DegreeRef {
    id: number;
    name: string;
    level: string;
    institution: string | null;
    year_obtained: number | null;
}

interface EvidenceRef {
    source: string;
    role: string;
    affiliation_confirmed: boolean;
    confidence: number | null;
    fetched_at: string;
}

interface ProfessorDetail {
    id: string;
    full_name: string;
    university_id: number;
    faculty_id: number;
    university_name: string | null;
    faculty_name: string | null;
    validation_status: "pending_validation" | "validated" | "not_found" | "rejected";
    global_score: number | null;
    total_evaluations: number;
    is_active: boolean;
    is_provisional: boolean;
    created_at: string;
    updated_at: string;
    courses: CourseRef[];
    degrees: DegreeRef[];
    evidence: EvidenceRef[];
    executive_summary: string | null;
}

interface PaginatedComments {
    items: CommentRead[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
}

export default function TeacherProfilePage() {
    const params = useParams();
    const router = useRouter();
    const id = params?.id as string;

    const [professor, setProfessor] = useState<ProfessorDetail | null>(null);
    const [comments, setComments] = useState<CommentRead[]>([]);
    const [loading, setLoading] = useState(true);
    const [loadingComments, setLoadingComments] = useState(true);
    const [error, setError] = useState('');
    const [notFound, setNotFound] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [refreshTick, setRefreshTick] = useState(0);
    const [userReactions, setUserReactions] = useState<Record<string, ReactionType | null>>({});
    const [pendingReactions, setPendingReactions] = useState<Set<string>>(new Set());
    const [hasToken, setHasToken] = useState(false);

    useEffect(() => {
        // Lectura hidratación-segura: leemos localStorage tras el mount para que
        // server y cliente coincidan en el primer render.
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setHasToken(Boolean(localStorage.getItem('access_token')));
    }, []);

    useEffect(() => {
        if (!id) return;

        const controller = new AbortController();

        const run = async () => {
            const token = localStorage.getItem('access_token');
            if (!token) {
                setError('Tu sesión expiró. Iniciá sesión de nuevo.');
                setLoading(false);
                setLoadingComments(false);
                return;
            }

            const detailPromise = fetch(`${API_URL}/professors/${id}`, {
                headers: { 'Authorization': `Bearer ${token}` },
                signal: controller.signal,
            }).then(async (res) => {
                if (res.status === 404) {
                    setNotFound(true);
                    return null;
                }
                if (!res.ok) {
                    throw new Error(`HTTP ${res.status}`);
                }
                return res.json() as Promise<ProfessorDetail>;
            }).then((data) => {
                if (data) setProfessor(data);
            }).catch((err: Error) => {
                if (err.name !== 'AbortError') {
                    setError('No se pudo cargar el profesor.');
                }
            }).finally(() => setLoading(false));

            const commentsPromise = fetch(
                `${API_URL}/professors/${id}/comments?page=1&page_size=20&order_by=recent`,
                { signal: controller.signal },
            )
                .then((res) => res.ok ? res.json() : Promise.reject(res))
                .then((data: PaginatedComments) => setComments(data.items))
                .catch(() => {
                    // Silencioso: si falla, solo se muestra "sin comentarios"
                })
                .finally(() => setLoadingComments(false));

            await Promise.all([detailPromise, commentsPromise]);
        };

        run();
        return () => controller.abort();
    }, [id, refreshTick]);

    // Poll while validation is pending (silent refetch, max ~2 min).
    const validationPollsRef = useRef(0);
    useEffect(() => {
        if (professor?.validation_status !== 'pending_validation') {
            validationPollsRef.current = 0;
            return;
        }
        if (validationPollsRef.current >= 24) return;
        const t = setTimeout(() => {
            validationPollsRef.current += 1;
            setRefreshTick((v) => v + 1);
        }, 5000);
        return () => clearTimeout(t);
    }, [professor?.validation_status, refreshTick]);

    const handleReact = async (commentId: string, type: ReactionType) => {
        if (pendingReactions.has(commentId)) return;

        const token = localStorage.getItem('access_token');
        if (!token) {
            setError('Iniciá sesión para reaccionar.');
            return;
        }

        const currentReaction = userReactions[commentId] ?? null;
        const nextReaction: ReactionType | null = currentReaction === type ? null : type;

        let likeDelta = 0;
        let dislikeDelta = 0;
        if (currentReaction === 'like') likeDelta -= 1;
        if (currentReaction === 'dislike') dislikeDelta -= 1;
        if (nextReaction === 'like') likeDelta += 1;
        if (nextReaction === 'dislike') dislikeDelta += 1;

        const previousComments = comments;
        const previousReaction = currentReaction;

        setUserReactions((prev) => ({ ...prev, [commentId]: nextReaction }));
        setComments((prev) => prev.map((c) =>
            c.id === commentId
                ? { ...c, like_count: c.like_count + likeDelta, dislike_count: c.dislike_count + dislikeDelta }
                : c,
        ));
        setPendingReactions((prev) => {
            const next = new Set(prev);
            next.add(commentId);
            return next;
        });

        try {
            const res = await fetch(`${API_URL}/comments/${commentId}/reactions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({ type }),
            });

            if (!res.ok) {
                throw new Error(`HTTP ${res.status}`);
            }

            const data = await res.json() as {
                comment_id: string;
                user_reaction: ReactionType | null;
                like_count: number;
                dislike_count: number;
            };

            setUserReactions((prev) => ({ ...prev, [commentId]: data.user_reaction }));
            setComments((prev) => prev.map((c) =>
                c.id === commentId
                    ? { ...c, like_count: data.like_count, dislike_count: data.dislike_count }
                    : c,
            ));
        } catch {
            setUserReactions((prev) => ({ ...prev, [commentId]: previousReaction }));
            setComments(previousComments);
        } finally {
            setPendingReactions((prev) => {
                const next = new Set(prev);
                next.delete(commentId);
                return next;
            });
        }
    };

    const handleEvaluationCreated = (evaluation: EvaluationCreated) => {
        // Optimistic update: el backend recalcula global_score vía Celery,
        // así que actualizamos localmente con la fórmula exacta (pesos 0.25 c/u)
        // y refetch 1500ms después para confirmar contra DB.
        setProfessor((prev) => {
            if (!prev) return prev;
            const oldTotal = prev.total_evaluations;
            const newEvalAvg = (evaluation.clarity + evaluation.easiness + evaluation.helpfulness + evaluation.punctuality) / 4;
            const newTotal = oldTotal + 1;
            const newScore = oldTotal === 0 || prev.global_score === null
                ? newEvalAvg
                : (prev.global_score * oldTotal + newEvalAvg) / newTotal;
            return {
                ...prev,
                total_evaluations: newTotal,
                global_score: Number(newScore.toFixed(2)),
            };
        });

        if (evaluation.comment) {
            const newComment: CommentRead = {
                id: evaluation.comment.id,
                professor_id: evaluation.professor_id,
                course_id: evaluation.course_id,
                text: evaluation.comment.text,
                modality: evaluation.comment.modality,
                like_count: evaluation.comment.like_count,
                dislike_count: evaluation.comment.dislike_count,
                created_at: evaluation.comment.created_at,
                hashtags: evaluation.hashtags,
            };
            setComments((prev) => [newComment, ...prev]);
        }

        // Confirmación contra DB cuando el worker Celery ya terminó.
        const t = setTimeout(() => setRefreshTick((tick) => tick + 1), 1500);
        return () => clearTimeout(t);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-white flex flex-col font-sans">
                <Navbar showSearch={false} />
                <main className="flex-1 w-full max-w-[1000px] mx-auto px-4 py-8">
                    <div className="bg-white border border-slate-100 rounded-2xl p-6 animate-pulse">
                        <div className="flex items-center gap-5">
                            <div className="w-16 h-16 rounded-full bg-slate-100" />
                            <div className="flex-1 space-y-2">
                                <div className="h-4 bg-slate-100 rounded w-1/2" />
                                <div className="h-3 bg-slate-100 rounded w-1/3" />
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        );
    }

    if (notFound) {
        return (
            <div className="min-h-screen bg-white flex flex-col font-sans">
                <Navbar showSearch={false} />
                <main className="flex-1 w-full max-w-[1000px] mx-auto px-4 py-12 text-center">
                    <h1 className="text-xl font-black text-slate-900">Profesor no encontrado</h1>
                    <p className="text-sm text-slate-500 mt-2">El profesor que buscás no existe o fue eliminado.</p>
                    <button
                        type="button"
                        onClick={() => router.push('/teachers')}
                        className="mt-6 px-4 py-2 bg-[#ff8a00] hover:bg-[#ea580c] text-white text-xs font-bold rounded-xl"
                    >
                        Volver al catálogo
                    </button>
                </main>
            </div>
        );
    }

    if (error || !professor) {
        return (
            <div className="min-h-screen bg-white flex flex-col font-sans">
                <Navbar showSearch={false} />
                <main className="flex-1 w-full max-w-[1000px] mx-auto px-4 py-12">
                    <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm font-medium">
                        {error || 'No se pudo cargar el profesor.'}
                    </div>
                </main>
            </div>
        );
    }

    const ratingDisplay = professor.global_score !== null
        ? `${professor.global_score.toFixed(1)} / 5.0`
        : 'Sin evaluaciones';

    const courseNames: Record<number, string> = Object.fromEntries(
        professor.courses.map((c) => [c.id, c.name]),
    );

    const canEvaluate =
        professor.validation_status === 'validated' && professor.courses.length > 0;

    const evaluateDisabledReason = professor.validation_status !== 'validated'
        ? 'El profesor aún no fue validado'
        : professor.courses.length === 0
            ? 'Sin cursos asignados todavía'
            : null;

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans text-left selection:bg-sky-100 selection:text-sky-900 relative">
            <Navbar showSearch={false} />

            <main className="flex-1 w-full max-w-[1000px] mx-auto px-4 py-8 space-y-6 bg-white">

                <button
                    onClick={() => router.push('/teachers')}
                    className="flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-slate-800 transition-colors mb-2 focus:outline-none cursor-pointer"
                >
                    <ArrowLeft className="w-4 h-4" /> Volver a resultados
                </button>

                {/* HEADER */}
                <div className="bg-white border border-slate-100 rounded-2xl p-6 flex flex-col sm:flex-row items-center justify-between gap-6 shadow-sm">
                    <div className="flex flex-col sm:flex-row items-center gap-5 text-center sm:text-left">
                        <div className="w-16 h-16 rounded-full bg-slate-100 border border-slate-200 shrink-0 flex items-center justify-center text-slate-400">
                            <User className="w-7 h-7" />
                        </div>
                        <div className="space-y-1">
                            <div className="flex flex-col sm:flex-row sm:items-center gap-3 justify-center sm:justify-start">
                                <h1 className="text-xl font-black text-slate-900 tracking-tight">{professor.full_name}</h1>
                                <span
                                    className={`text-[10px] font-black px-2 py-0.5 rounded-md shadow-sm ${
                                        professor.global_score !== null
                                            ? 'bg-[#ff8a00] text-white'
                                            : 'bg-slate-100 text-slate-500'
                                    }`}
                                >
                                    {ratingDisplay}
                                </span>
                                {professor.is_provisional && (
                                    <span className="px-2 py-0.5 bg-amber-50 text-amber-700 border border-amber-200 font-bold text-[9px] rounded-md tracking-wider uppercase">
                                        Provisional
                                    </span>
                                )}
                            </div>
                            <p className="text-xs font-semibold text-slate-500 flex flex-wrap items-center justify-center sm:justify-start gap-1">
                                <ClipboardList className="w-3.5 h-3.5 text-slate-400" />
                                {professor.faculty_name ?? '—'}
                                {professor.university_name && <> • {professor.university_name}</>}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0 w-full sm:w-auto justify-center">
                        <button
                            type="button"
                            className="px-4 py-2 border border-slate-200 text-slate-400 text-xs font-bold rounded-xl flex items-center gap-1.5 cursor-not-allowed opacity-60"
                            disabled
                            title="Próximamente"
                        >
                            <Bookmark className="w-3.5 h-3.5" /> Guardar
                        </button>
                        <button
                            onClick={() => setIsModalOpen(true)}
                            disabled={!canEvaluate}
                            title={evaluateDisabledReason ?? ''}
                            className={`px-4 py-2 text-xs font-black rounded-xl flex items-center gap-1.5 transition-colors shadow-sm ${
                                canEvaluate
                                    ? 'bg-[#ff8a00] hover:bg-[#ea580c] text-white cursor-pointer'
                                    : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                            }`}
                        >
                            <MessageSquare className="w-3.5 h-3.5" /> Evaluar
                        </button>
                    </div>
                </div>

                {/* SÍNTESIS IA */}
                {professor.executive_summary && (
                    <div className="bg-[#e0f2fe]/40 border border-sky-100 rounded-2xl p-6 shadow-sm">
                        <div className="flex gap-4 items-start">
                            <div className="w-9 h-9 bg-white rounded-xl flex items-center justify-center text-sky-600 shadow-sm border border-sky-100 shrink-0 text-base">🧠</div>
                            <div className="space-y-1 flex-1">
                                <div className="flex items-center gap-2">
                                    <h3 className="text-xs font-black text-sky-950 tracking-wider uppercase">Síntesis del perfil</h3>
                                    <span className="bg-sky-500/10 text-sky-700 text-[8px] font-black px-1.5 py-0.5 rounded-md tracking-widest">IA</span>
                                </div>
                                <p className="text-xs text-slate-600 font-medium leading-relaxed">
                                    {professor.executive_summary}
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {/* HOJA DE VIDA — solo Educación */}
                {professor.degrees.length > 0 && (
                    <div className="bg-white border border-slate-100 rounded-2xl p-6 text-xs font-medium shadow-sm">
                        <div className="flex items-center gap-2 mb-5">
                            <GraduationCap className="w-4 h-4 text-[#0284c7]" />
                            <h3 className="text-xs font-black text-slate-900 tracking-wider uppercase">Formación académica</h3>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-slate-600">
                            {professor.degrees.map((d) => (
                                <div key={d.id} className="border border-slate-100 rounded-xl p-4 bg-slate-50/40">
                                    <span className="text-[9px] font-bold text-slate-400 uppercase block tracking-wider">{d.level}</span>
                                    <p className="font-bold text-slate-800 mt-0.5">{d.name}</p>
                                    {(d.institution || d.year_obtained) && (
                                        <p className="text-[11px] text-slate-400 mt-0.5">
                                            {d.institution}
                                            {d.institution && d.year_obtained && ' • '}
                                            {d.year_obtained}
                                        </p>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* MÉTRICAS + CURSOS + COMENTARIOS */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">

                    <div className="space-y-4">
                        <div className="bg-white border border-slate-100 rounded-2xl p-5 space-y-3 shadow-sm">
                            <h4 className="text-xs font-black text-slate-900 uppercase tracking-wider">Puntaje</h4>
                            <div className="flex items-baseline gap-2">
                                <span className="text-3xl font-black text-[#ff8a00]">
                                    {professor.global_score !== null ? professor.global_score.toFixed(1) : '—'}
                                </span>
                                <span className="text-xs font-bold text-slate-400">/ 5.0</span>
                            </div>
                            <p className="text-[10px] font-medium text-slate-400 pt-1">
                                {professor.total_evaluations === 0
                                    ? 'Sin evaluaciones todavía'
                                    : `Basado en ${professor.total_evaluations} evaluación${professor.total_evaluations === 1 ? '' : 'es'}`}
                            </p>
                        </div>

                        {professor.courses.length > 0 && (
                            <div className="bg-sky-50/40 border border-sky-100/60 rounded-2xl p-5">
                                <h4 className="text-[10px] font-black text-[#0284c7] uppercase tracking-wider mb-3">Cursos que dicta</h4>
                                <ul className="space-y-1.5 text-xs font-semibold text-slate-600">
                                    {professor.courses.map((c) => (
                                        <li key={c.id} className="flex items-center gap-2">
                                            <span className="text-sky-500">✓</span> {c.name}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>

                    <CommentList
                        comments={comments}
                        courseNames={courseNames}
                        loading={loadingComments}
                        userReactions={userReactions}
                        pendingReactions={pendingReactions}
                        onReact={handleReact}
                        canReact={hasToken}
                    />

                </div>
            </main>

            <EvaluarModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                professorId={professor.id}
                professorName={professor.full_name}
                facultyName={professor.faculty_name}
                courses={professor.courses.map((c) => ({ id: c.id, name: c.name }))}
                isValidated={professor.validation_status === 'validated'}
                onCreated={handleEvaluationCreated}
            />

        </div>
    );
}

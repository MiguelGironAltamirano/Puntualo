'use client'

import { useState } from "react";
import { Award, ThumbsDown, ThumbsUp, Flag } from "lucide-react";
import { ReportModal } from "./ReportModal";

export interface CommentRead {
    id: string;
    professor_id: string;
    course_id: number;
    text: string | null;
    modality: string;
    like_count: number;
    dislike_count: number;
    created_at: string;
    hashtags: string[];
}

export type ReactionType = 'like' | 'dislike';

interface CommentListProps {
    comments: CommentRead[];
    courseNames: Record<number, string>;
    loading?: boolean;
    userReactions: Record<string, ReactionType | null>;
    pendingReactions: Set<string>;
    onReact: (commentId: string, type: ReactionType) => void;
    canReact: boolean;
    stickyCommentId?: string | null;
}

function formatModality(modality: string): string {
    if (!modality) return '';
    return modality.charAt(0).toUpperCase() + modality.slice(1);
}

function formatDate(iso: string): string {
    try {
        return new Date(iso).toLocaleDateString('es-PE', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        });
    } catch {
        return '';
    }
}

interface CommentCardProps {
    comment: CommentRead;
    courseName: string;
    userReaction: ReactionType | null;
    pending: boolean;
    onReact: (type: ReactionType) => void;
    canReact: boolean;
    isSticky?: boolean;
}

function CommentCard({ comment, courseName, userReaction, pending, onReact, canReact, isSticky }: CommentCardProps) {
    const [reportModalOpen, setReportModalOpen] = useState(false);
    const likeActive = userReaction === 'like';
    const dislikeActive = userReaction === 'dislike';
    const disabled = pending || !canReact;

    return (
        <div className={`rounded-2xl p-5 shadow-sm space-y-4 text-left transition-all ${
            isSticky
                ? 'bg-amber-50/60 border border-amber-200'
                : 'bg-white border border-slate-100'
        }`}>
            <ReportModal 
                isOpen={reportModalOpen}
                onClose={() => setReportModalOpen(false)}
                commentId={comment.id}
                onReportSubmitted={() => setReportModalOpen(false)}
            />

            <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                    <h4 className="text-sm font-black text-slate-900 tracking-tight mb-1">
                        {courseName}
                    </h4>
                    <p className="text-[10px] font-medium text-slate-400">
                        {formatDate(comment.created_at)}
                        {comment.modality && (
                            <>
                                <span className="text-slate-200 mx-0.5">•</span> {formatModality(comment.modality)}
                            </>
                        )}
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    {isSticky && (
                        <span className="flex items-center gap-1 px-2 py-0.5 bg-amber-100 text-amber-700 border border-amber-200 rounded-lg text-[9px] font-black tracking-wide shrink-0">
                            <Award className="w-3 h-3" />
                            Más apoyado
                        </span>
                    )}
                    <button
                        type="button"
                        onClick={() => setReportModalOpen(true)}
                        title="Reportar comentario"
                        className="text-slate-400 hover:text-red-600 hover:bg-red-50 p-1.5 rounded-lg transition-colors"
                    >
                        <Flag className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {comment.text && (
                <p className="text-xs text-slate-600 font-medium leading-relaxed">{comment.text}</p>
            )}

            {comment.hashtags.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                    {comment.hashtags.map((tag) => (
                        <span key={tag} className="px-2 py-0.5 bg-[#e0f2fe] text-[#0284c7] font-bold text-[9px] rounded-md">
                            #{tag}
                        </span>
                    ))}
                </div>
            )}

            <div className="flex items-center gap-4 pt-3.5 border-t border-slate-100 text-[11px] font-bold">
                <button
                    type="button"
                    onClick={() => onReact('like')}
                    disabled={disabled}
                    title={!canReact ? 'Iniciá sesión para reaccionar' : ''}
                    className={`flex items-center gap-1 transition-colors px-2 py-1 rounded-md ${
                        likeActive
                            ? 'text-[#ff8a00] bg-orange-50'
                            : 'text-slate-400 hover:text-slate-700 hover:bg-slate-50'
                    } ${disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'}`}
                >
                    <ThumbsUp className={`w-3.5 h-3.5 ${likeActive ? 'fill-[#ff8a00]' : ''}`} />
                    {comment.like_count}
                </button>
                <button
                    type="button"
                    onClick={() => onReact('dislike')}
                    disabled={disabled}
                    title={!canReact ? 'Iniciá sesión para reaccionar' : ''}
                    className={`flex items-center gap-1 transition-colors px-2 py-1 rounded-md ${
                        dislikeActive
                            ? 'text-slate-700 bg-slate-100'
                            : 'text-slate-400 hover:text-slate-700 hover:bg-slate-50'
                    } ${disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'}`}
                >
                    <ThumbsDown className={`w-3.5 h-3.5 ${dislikeActive ? 'fill-slate-700' : ''}`} />
                    {comment.dislike_count}
                </button>
            </div>
        </div>
    );
}

export function CommentList({
    comments,
    courseNames,
    loading,
    userReactions,
    pendingReactions,
    onReact,
    canReact,
    stickyCommentId,
}: CommentListProps) {
    return (
        <div className="md:col-span-2 space-y-4">
            <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider text-left">
                    Comentarios de alumnos
                </h3>
                <span className="text-[10px] font-bold text-slate-400">
                    {loading
                        ? 'Cargando...'
                        : comments.length === 0
                            ? 'Sin comentarios'
                            : `${comments.length} comentario${comments.length === 1 ? '' : 's'}`}
                </span>
            </div>

            {loading && comments.length === 0 && (
                <div className="bg-white border border-slate-100 rounded-2xl p-5 animate-pulse">
                    <div className="h-3 bg-slate-100 rounded w-1/3 mb-3" />
                    <div className="h-2 bg-slate-100 rounded w-full mb-1" />
                    <div className="h-2 bg-slate-100 rounded w-5/6" />
                </div>
            )}

            {!loading && comments.length === 0 && (
                <div className="bg-white border border-dashed border-slate-200 rounded-2xl p-8 text-center">
                    <p className="text-xs font-medium text-slate-500">
                        Todavía no hay comentarios para este profesor.
                    </p>
                </div>
            )}

            {comments.map((comment) => (
                <CommentCard
                    key={comment.id}
                    comment={comment}
                    courseName={courseNames[comment.course_id] ?? `Curso #${comment.course_id}`}
                    userReaction={userReactions[comment.id] ?? null}
                    pending={pendingReactions.has(comment.id)}
                    onReact={(type) => onReact(comment.id, type)}
                    canReact={canReact}
                    isSticky={!!stickyCommentId && comment.id === stickyCommentId}
                />
            ))}
        </div>
    );
}

'use client'

import { useState } from 'react';
import { SlidersHorizontal, Flag, CheckCircle2, ThumbsUp, ThumbsDown } from "lucide-react";

import { TeacherComment } from "./types";
import { ReportModal } from "./ReportModal";
import { FilterDropdown } from "./FilterDropdown";

interface CommentListProps {
    comments: TeacherComment[];
}

function CommentCard({ comment, onReport }: { comment: TeacherComment, onReport: () => void }) {
    const [likes, setLikes] = useState(comment.reactions.likes || 0);
    const [dislikes, setDislikes] = useState(comment.reactions.dislikes || 0);
    const [liked, setLiked] = useState(false);
    const [disliked, setDisliked] = useState(false);

    const [heart, setHeart] = useState({ count: comment.reactions.heart || 0, active: false });
    const [fire, setFire] = useState({ count: comment.reactions.fire || 0, active: false });
    const [lightbulb, setLightbulb] = useState({ count: comment.reactions.lightbulb || 0, active: false });
    const [droplet, setDroplet] = useState({ count: comment.reactions.droplet || 0, active: false });
    const [chart, setChart] = useState({ count: comment.reactions.chart || 0, active: false });

    const handleLike = () => {
        if (liked) {
            setLikes(likes - 1);
            setLiked(false);
        } else {
            setLikes(likes + 1);
            setLiked(true);
            if (disliked) {
                setDislikes(dislikes - 1);
                setDisliked(false);
            }
        }
    };

    const handleDislike = () => {
        if (disliked) {
            setDislikes(dislikes - 1);
            setDisliked(false);
        } else {
            setDislikes(dislikes + 1);
            setDisliked(true);
            if (liked) {
                setLikes(likes - 1);
                setLiked(false);
            }
        }
    };

    const emojis = [
        { icon: '❤️', state: heart, setter: setHeart },
        { icon: '🔥', state: fire, setter: setFire },
        { icon: '💡', state: lightbulb, setter: setLightbulb },
        { icon: '💧', state: droplet, setter: setDroplet },
        { icon: '📈', state: chart, setter: setChart },
    ];

    return (
        <div className="bg-white border border-slate-100 rounded-2xl p-5 shadow-sm space-y-4 text-left">
            <div className="flex items-start justify-between">
                <div>
                    <h4 className="text-sm font-black text-slate-900 tracking-tight mb-1">{comment.course}</h4>
                    <p className="text-[10px] font-medium text-slate-400">
                        {comment.semester} <span className="text-slate-200 mx-0.5">•</span> {comment.mode}
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <button type="button" onClick={onReport} className="text-slate-300 hover:text-slate-500 p-0.5 transition-colors cursor-pointer focus:outline-none">
                        <Flag className="w-3.5 h-3.5" />
                    </button>
                    <div className="flex items-center gap-1 bg-slate-50 border border-slate-200/60 rounded-md px-2 py-0.5 text-[10px] font-bold text-slate-700">
                        <span>★ {comment.score}</span>
                        {comment.verified && <CheckCircle2 className="w-3 h-3 text-sky-500 shrink-0" />}
                    </div>
                </div>
            </div>

            <p className="text-xs text-slate-600 font-medium leading-relaxed">{comment.text}</p>

            <div className="flex flex-wrap gap-1.5">
                {comment.tags.map((tag) => (
                    <span key={tag} className="px-2 py-0.5 bg-[#e0f2fe] text-[#0284c7] font-bold text-[9px] rounded-md">
                        {tag}
                    </span>
                ))}
            </div>

            <div className="flex flex-wrap items-center justify-between gap-4 pt-3.5 border-t border-slate-100 text-[11px] font-bold text-slate-400">
                <div className="flex items-center gap-3">
                    <button type="button" onClick={handleLike} className={`flex items-center gap-1 cursor-pointer transition-colors ${liked ? 'text-[#ff8a00]' : 'hover:text-sky-600'}`}>
                        <ThumbsUp className={`w-3.5 h-3.5 ${liked ? 'fill-[#ff8a00]' : ''}`} /> {likes}
                    </button>
                    <button type="button" onClick={handleDislike} className={`flex items-center gap-1 cursor-pointer transition-colors ${disliked ? 'text-slate-700' : 'hover:text-slate-600'}`}>
                        <ThumbsDown className={`w-3.5 h-3.5 ${disliked ? 'fill-slate-700' : ''}`} /> {dislikes}
                    </button>
                    <button type="button" onClick={onReport} className="flex items-center gap-1 text-[10px] hover:text-red-500 cursor-pointer transition-colors ml-2 font-semibold">
                        Reportar
                    </button>
                </div>
                <div className="flex items-center gap-1.5">
                    {emojis.map((emojiObj, idx) => (
                        <button 
                            key={idx} 
                            type="button"
                            onClick={() => {
                                if (emojiObj.state.active) {
                                    emojiObj.setter({ count: emojiObj.state.count - 1, active: false });
                                } else {
                                    emojiObj.setter({ count: emojiObj.state.count + 1, active: true });
                                }
                            }}
                            className={`rounded-full px-2 py-0.5 cursor-pointer flex items-center gap-1 text-slate-700 select-none transition-all ${emojiObj.state.active ? 'bg-orange-50 border border-[#ff8a00] text-[#ff8a00]' : 'bg-slate-50 border border-slate-200 hover:bg-slate-100'}`}
                        >
                            <span>{emojiObj.icon}</span>
                            <span className={`text-[10px] font-bold ${emojiObj.state.active ? 'text-[#ff8a00]' : 'text-slate-500'}`}>{emojiObj.state.count}</span>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}

export function CommentList({ comments }: CommentListProps) {
    const [isReportOpen, setIsReportOpen] = useState(false);
    const [isFilterOpen, setIsFilterOpen] = useState(false);
    return (
        <div className="md:col-span-2 space-y-4">
            {/* Cabecera de la sección */}
            <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider text-left">
                    Comentarios de Alumnos
                </h3>
                <div className="relative">
                    <button type="button" onClick={() => setIsFilterOpen(!isFilterOpen)} className="px-3 py-1.5 border border-slate-200 text-slate-500 text-[10px] font-bold rounded-lg flex items-center gap-1 hover:bg-slate-50 transition-colors cursor-pointer focus:outline-none">
                        <SlidersHorizontal className="w-3 h-3" /> Filtrar
                    </button>
                    <FilterDropdown isOpen={isFilterOpen} onClose={() => setIsFilterOpen(false)} />
                </div>
            </div>

            {/* Renderizado de cada tarjeta de opinión */}
            {comments.map((comment) => (
                <CommentCard key={comment.id} comment={comment} onReport={() => setIsReportOpen(true)} />
            ))}

            {/* Botón de paginación */}
            <button type="button" className="w-full py-2.5 bg-slate-50 hover:bg-slate-100/80 border border-slate-200 text-[#0284c7] font-bold text-[11px] rounded-xl transition-colors text-center cursor-pointer focus:outline-none">
                Cargar más comentarios
            </button>

            {/* Modales globales de la lista */}
            <ReportModal isOpen={isReportOpen} onClose={() => setIsReportOpen(false)} />
        </div>
    );
}
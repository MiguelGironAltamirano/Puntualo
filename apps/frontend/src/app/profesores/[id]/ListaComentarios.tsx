'use client'

import { SlidersHorizontal, Flag, CheckCircle2, ThumbsUp, ThumbsDown } from "lucide-react";

interface Reaccion {
    icon: string;
    count: number;
}

interface Comentario {
    id: number;
    course: string;
    semester: string;
    mode: string;
    score: string;
    verified: boolean;
    text: string;
    tags: string[];
    likes: number;
    dislikes: number;
    reactions: Reaccion[];
}

interface ListaComentariosProps {
    comments: Comentario[];
}

export function ListaComentarios({ comments }: ListaComentariosProps) {
    return (
        <div className="md:col-span-2 space-y-4">
            {/* Cabecera de la sección */}
            <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider text-left">
                    Comentarios de Alumnos
                </h3>
                <button type="button" className="px-3 py-1.5 border border-slate-200 text-slate-500 text-[10px] font-bold rounded-lg flex items-center gap-1 hover:bg-slate-50 transition-colors cursor-pointer">
                    <SlidersHorizontal className="w-3 h-3" /> Filtrar
                </button>
            </div>

            {/* Renderizado de cada tarjeta de opinión */}
            {comments.map((comment) => (
                <div key={comment.id} className="bg-white border border-slate-100 rounded-2xl p-5 shadow-sm space-y-4 text-left">
                    <div className="flex items-start justify-between">
                        <div>
                            <h4 className="text-sm font-black text-slate-900 tracking-tight mb-1">{comment.course}</h4>
                            <p className="text-[10px] font-medium text-slate-400">
                                {comment.semester} <span className="text-slate-200 mx-0.5">•</span> {comment.mode}
                            </p>
                        </div>
                        <div className="flex items-center gap-2">
                            <button type="button" className="text-slate-300 hover:text-slate-500 p-0.5 transition-colors cursor-pointer">
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

                    {/* Barra de Reacciones del Figma */}
                    <div className="flex flex-wrap items-center justify-between gap-4 pt-3.5 border-t border-slate-100 text-[11px] font-bold text-slate-400">
                        <div className="flex items-center gap-3">
                            <button type="button" className="flex items-center gap-1 hover:text-sky-600 cursor-pointer text-sky-600/90 transition-colors">
                                <ThumbsUp className="w-3.5 h-3.5" /> {comment.likes}
                            </button>
                            <button type="button" className="flex items-center gap-1 hover:text-slate-600 cursor-pointer transition-colors">
                                <ThumbsDown className="w-3.5 h-3.5" /> {comment.dislikes}
                            </button>
                        </div>
                        <div className="flex items-center gap-1.5">
                            {comment.reactions.map((react) => (
                                <span key={react.icon} className="bg-slate-50 border border-slate-200 rounded-full px-2 py-0.5 hover:bg-slate-100 cursor-pointer flex items-center gap-1 text-slate-700 select-none transition-colors">
                                    <span>{react.icon}</span>
                                    <span className="text-[10px] font-bold text-slate-500">{react.count}</span>
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            ))}

            {/* Botón de paginación */}
            <button type="button" className="w-full py-2.5 bg-slate-50 hover:bg-slate-100/80 border border-slate-200 text-[#0284c7] font-bold text-[11px] rounded-xl transition-colors text-center cursor-pointer focus:outline-none">
                Cargar más comentarios
            </button>
        </div>
    );
}
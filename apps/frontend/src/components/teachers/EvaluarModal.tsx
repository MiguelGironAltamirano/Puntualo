'use client'

import { useState } from 'react';
import { X, Star, ChevronDown, Play } from 'lucide-react';
import { TeacherData } from "./types";

interface EvaluarModalProps {
    isOpen: boolean;
    onClose: () => void;
    teacher: TeacherData;
}

export function EvaluarModal({ isOpen, onClose, teacher }: EvaluarModalProps) {
    const [claridad, setClaridad] = useState(0);
    const [facilidad, setFacilidad] = useState(0);
    const [ayuda, setAyuda] = useState(0);
    const [puntualidad, setPuntualidad] = useState(0);
    
    const [curso, setCurso] = useState('');
    const [semestre, setSemestre] = useState('');
    const [modalidad, setModalidad] = useState('');
    

    const [comment, setComment] = useState('');
    const [hashtags, setHashtags] = useState('');

    if (!isOpen) return null;



    const StarRating = ({ value, onChange }: { value: number, onChange: (val: number) => void }) => (
        <div className="flex items-center justify-center gap-1 mt-2">
            {[1, 2, 3, 4, 5].map((star) => (
                <button
                    key={star}
                    type="button"
                    onClick={() => onChange(star)}
                    className="p-0.5 transition-all focus:outline-none hover:scale-110"
                >
                    <Star className={`w-5 h-5 ${star <= value ? 'fill-[#ff8a00] text-[#ff8a00]' : 'text-slate-200'}`} />
                </button>
            ))}
        </div>
    );

    return (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4 overflow-y-auto animate-fadeIn">
            <div className="bg-white rounded-3xl w-full max-w-2xl relative shadow-2xl my-auto text-left flex flex-col max-h-[90vh]">
                
                {/* Fixed Header */}
                <div className="p-6 border-b border-slate-100 flex items-center gap-4 shrink-0 relative">
                    <button onClick={onClose} className="absolute right-6 top-6 text-slate-400 hover:text-slate-600 transition-colors p-1.5 cursor-pointer focus:outline-none hover:bg-slate-50 rounded-xl">
                        <X className="w-5 h-5" />
                    </button>
                    
                    <div className="w-14 h-14 rounded-full overflow-hidden bg-slate-100 shrink-0 border border-slate-200">
                        <img src={teacher.avatar} alt={teacher.name} className="w-full h-full object-cover object-top" />
                    </div>
                    <div>
                        <h2 className="text-lg font-black text-slate-900 leading-tight">{teacher.name}</h2>
                        <p className="text-xs font-semibold text-slate-500 mt-0.5 flex items-center gap-1">
                            <svg className="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
                            {teacher.department}
                        </p>
                    </div>
                </div>

                {/* Scrollable Content */}
                <div className="p-8 overflow-y-auto flex-1 space-y-10 custom-scrollbar">
                    
                    {/* Calificaciones Generales */}
                    <div>
                        <h3 className="text-xs font-black text-[#0284c7] uppercase tracking-wider mb-4 flex items-center gap-2">
                            <Star className="w-4 h-4" /> Calificaciones Generales
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100 text-center shadow-sm">
                                <span className="text-[9px] font-black text-slate-700 uppercase tracking-widest block">Claridad de las clases</span>
                                <StarRating value={claridad} onChange={setClaridad} />
                            </div>
                            <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100 text-center shadow-sm">
                                <span className="text-[9px] font-black text-slate-700 uppercase tracking-widest block">Nivel de facilidad</span>
                                <StarRating value={facilidad} onChange={setFacilidad} />
                            </div>
                            <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100 text-center shadow-sm">
                                <span className="text-[9px] font-black text-slate-700 uppercase tracking-widest block">Disposición para ayudar</span>
                                <StarRating value={ayuda} onChange={setAyuda} />
                            </div>
                            <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100 text-center shadow-sm">
                                <span className="text-[9px] font-black text-slate-700 uppercase tracking-widest block">Puntualidad</span>
                                <StarRating value={puntualidad} onChange={setPuntualidad} />
                            </div>
                        </div>
                    </div>

                    {/* Curso y Logística */}
                    <div>
                        <h3 className="text-xs font-black text-[#0284c7] uppercase tracking-wider mb-4 flex items-center gap-2">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
                            Curso y Logística
                        </h3>
                        <div className="space-y-4">
                            <div>
                                <label className="text-[9px] font-black text-slate-700 uppercase tracking-widest block mb-2">Seleccionar Curso</label>
                                <div className="relative">
                                    <select value={curso} onChange={e => setCurso(e.target.value)} className="w-full bg-white border border-slate-200 text-xs font-medium text-slate-600 rounded-xl pl-4 pr-10 py-3.5 appearance-none focus:outline-none focus:border-sky-300 transition-colors shadow-sm cursor-pointer">
                                        <option value="" disabled>Elige el curso que tomaste...</option>
                                        {teacher.research.map(c => <option key={c} value={c}>{c}</option>)}
                                    </select>
                                    <ChevronDown className="w-4 h-4 absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                                </div>
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div>
                                    <label className="text-[9px] font-black text-slate-700 uppercase tracking-widest block mb-2">Semestre</label>
                                    <div className="relative">
                                        <select value={semestre} onChange={e => setSemestre(e.target.value)} className="w-full bg-white border border-slate-200 text-xs font-medium text-slate-600 rounded-xl pl-4 pr-10 py-3.5 appearance-none focus:outline-none focus:border-sky-300 transition-colors shadow-sm cursor-pointer">
                                            <option value="" disabled>2023-2</option>
                                            <option value="2023-2">2023-2</option>
                                            <option value="2023-1">2023-1</option>
                                        </select>
                                        <ChevronDown className="w-4 h-4 absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                                    </div>
                                </div>
                                <div>
                                    <label className="text-[9px] font-black text-slate-700 uppercase tracking-widest block mb-2">Modalidad</label>
                                    <div className="relative">
                                        <select value={modalidad} onChange={e => setModalidad(e.target.value)} className="w-full bg-white border border-slate-200 text-xs font-medium text-slate-600 rounded-xl pl-4 pr-10 py-3.5 appearance-none focus:outline-none focus:border-sky-300 transition-colors shadow-sm cursor-pointer">
                                            <option value="" disabled>Presencial</option>
                                            <option value="Presencial">Presencial</option>
                                            <option value="Virtual">Virtual</option>
                                            <option value="Híbrido">Híbrido</option>
                                        </select>
                                        <ChevronDown className="w-4 h-4 absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>



                    {/* Tu Reseña */}
                    <div>
                        <h3 className="text-xs font-black text-[#0284c7] uppercase tracking-wider mb-4 flex items-center gap-2">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                            Tu Reseña
                        </h3>
                        
                        <div className="space-y-4">
                            <div>
                                <label className="text-[9px] font-black text-slate-700 uppercase tracking-widest block mb-2">Comentario Principal</label>
                                <textarea
                                    rows={4}
                                    value={comment}
                                    onChange={(e) => setComment(e.target.value)}
                                    placeholder="Describe tu experiencia detalladamente. ¿Qué fue lo mejor del curso? ¿Qué podría mejorar?"
                                    className="w-full bg-white border border-slate-200 rounded-xl p-4 text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-300 transition-all resize-none shadow-sm"
                                />
                                <div className="text-right mt-1.5">
                                    <span className="text-[9px] font-bold text-slate-400">{comment.length} / 1500 caracteres</span>
                                </div>
                            </div>
                            <div>
                                <label className="text-[9px] font-black text-slate-700 uppercase tracking-widest block mb-2">Añadir Hashtags</label>
                                <div className="relative shadow-sm rounded-xl">
                                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-black text-sm">#</span>
                                    <input 
                                        type="text" 
                                        value={hashtags}
                                        onChange={(e) => setHashtags(e.target.value)}
                                        placeholder="Ej: Accesible, Examenes_dificiles"
                                        className="w-full bg-white border border-slate-200 rounded-xl pl-8 pr-4 py-3 text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-300 transition-all"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer Actions */}
                <div className="p-6 border-t border-slate-100 flex items-center justify-end gap-6 shrink-0 bg-white rounded-b-3xl">
                    <button type="button" onClick={onClose} className="text-[11px] font-bold text-slate-500 hover:text-slate-800 transition-colors focus:outline-none cursor-pointer">
                        Cancelar
                    </button>
                    <button type="button" onClick={() => { onClose(); }} className="px-6 py-3 bg-[#ff8a00] hover:bg-[#ea580c] text-white font-bold text-[11px] uppercase tracking-wider rounded-xl transition-all shadow-sm flex items-center gap-2 focus:outline-none cursor-pointer">
                        <Play className="w-3.5 h-3.5 fill-white" />
                        Publicar Evaluación
                    </button>
                </div>

            </div>
        </div>
    );
}

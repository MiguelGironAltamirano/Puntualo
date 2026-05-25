'use client'

import { useState } from 'react';
import { X, Star } from 'lucide-react';

interface FilterDropdownProps {
    isOpen: boolean;
    onClose: () => void;
}

export function FilterDropdown({ isOpen, onClose }: FilterDropdownProps) {
    const [dificultad, setDificultad] = useState(50);
    const [rating, setRating] = useState(4);
    const [modalidades, setModalidades] = useState<string[]>(['Presencial', 'Virtual']);

    if (!isOpen) return null;

    const toggleModalidad = (mod: string) => {
        setModalidades(prev => prev.includes(mod) ? prev.filter(m => m !== mod) : [...prev, mod]);
    };

    return (
        <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-3xl border border-slate-100 shadow-[0_10px_40px_rgba(0,0,0,0.08)] z-50 animate-fadeIn text-left cursor-default">
            <div className="flex items-center justify-between p-5 border-b border-slate-100">
                <h3 className="text-sm font-black text-[#0284c7]">Filtrar Comentarios</h3>
                <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors focus:outline-none">
                    <X className="w-4 h-4" />
                </button>
            </div>
            
            <div className="p-5 space-y-6 max-h-[400px] overflow-y-auto">
                {/* Curso */}
                <div>
                    <label className="text-[11px] font-black text-slate-800 block mb-1.5">Curso</label>
                    <select className="w-full bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-600 rounded-xl px-3 py-2.5 outline-none focus:border-sky-300">
                        <option>Selecciona un curso</option>
                        <option>Ingeniería de Software</option>
                        <option>Base de Datos</option>
                    </select>
                </div>

                {/* Semestre & Fecha */}
                <div className="flex gap-3">
                    <div className="flex-1">
                        <label className="text-[11px] font-black text-slate-800 block mb-1.5">Semestre</label>
                        <select className="w-full bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-600 rounded-xl px-3 py-2.5 outline-none focus:border-sky-300">
                            <option>Todos</option>
                            <option>2023-2</option>
                        </select>
                    </div>
                    <div className="flex-1">
                        <label className="text-[11px] font-black text-slate-800 block mb-1.5">Fecha</label>
                        <select className="w-full bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-600 rounded-xl px-3 py-2.5 outline-none focus:border-sky-300">
                            <option>Cualquier momento</option>
                            <option>Último mes</option>
                        </select>
                    </div>
                </div>

                {/* Calificación */}
                <div>
                    <label className="text-[11px] font-black text-slate-800 block mb-1.5">Calificación</label>
                    <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 flex items-center justify-between">
                        <div className="flex items-center gap-1">
                            {[1, 2, 3, 4, 5].map((star) => (
                                <Star key={star} onClick={() => setRating(star)} className={`w-4 h-4 cursor-pointer transition-colors ${star <= rating ? 'text-[#ff8a00] fill-[#ff8a00]' : 'text-slate-300'}`} />
                            ))}
                        </div>
                        <span className="text-[10px] text-slate-500 font-semibold">{rating} estrellas o más</span>
                    </div>
                </div>

                {/* Modalidad */}
                <div>
                    <label className="text-[11px] font-black text-slate-800 block mb-2">Modalidad</label>
                    <div className="flex items-center gap-4">
                        {['Presencial', 'Virtual', 'Híbrido'].map(mod => (
                            <label key={mod} className="flex items-center gap-1.5 cursor-pointer">
                                <input type="checkbox" checked={modalidades.includes(mod)} onChange={() => toggleModalidad(mod)} className="w-3.5 h-3.5 text-[#0284c7] rounded border-slate-300 focus:ring-[#0284c7]" />
                                <span className="text-xs font-semibold text-slate-600">{mod}</span>
                            </label>
                        ))}
                    </div>
                </div>

                {/* Dificultad */}
                <div>
                    <div className="flex items-center justify-between mb-2">
                        <label className="text-[11px] font-black text-slate-800">Nivel de Dificultad</label>
                        <span className="bg-sky-100 text-[#0284c7] text-[9px] font-black px-2 py-0.5 rounded uppercase">Cualquiera</span>
                    </div>
                    <input type="range" min="0" max="100" value={dificultad} onChange={(e) => setDificultad(Number(e.target.value))} className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#0284c7]" />
                    <div className="flex justify-between text-[10px] font-bold text-slate-400 mt-1">
                        <span>Fácil</span>
                        <span>Difícil</span>
                    </div>
                </div>
            </div>

            <div className="p-4 border-t border-slate-100 flex items-center justify-between gap-3 bg-slate-50/50 rounded-b-3xl">
                <button type="button" onClick={onClose} className="px-4 py-2 text-xs font-bold text-slate-500 hover:text-slate-800 transition-colors focus:outline-none">
                    Limpiar filtros
                </button>
                <button type="button" onClick={onClose} className="px-5 py-2.5 bg-[#ff8a00] hover:bg-[#ea580c] text-white font-bold text-xs rounded-xl shadow-sm transition-all focus:outline-none">
                    Aplicar Filtros
                </button>
            </div>
        </div>
    );
}

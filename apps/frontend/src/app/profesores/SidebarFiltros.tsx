'use client'

import { useState } from 'react';

export default function SidebarFiltros() {
    const [nombreProfesor, setNombreProfesor] = useState('');
    const [facilidad, setFacilidad] = useState(50);

    // Estado para manejar la multiselección de etiquetas
    const [etiquetasSeleccionadas, setEtiquetasSeleccionadas] = useState<string[]>(['Barco']);

    // Función interactiva para prender/apagar las etiquetas
    const toggleEtiqueta = (tagName: string) => {
        if (etiquetasSeleccionadas.includes(tagName)) {
            // Si ya está seleccionada, la quitamos
            setEtiquetasSeleccionadas(etiquetasSeleccionadas.filter(t => t !== tagName));
        } else {
            // Si no está, la agregamos al array
            setEtiquetasSeleccionadas([...etiquetasSeleccionadas, tagName]);
        }
    };

    return (
        <aside className="w-64 bg-[#f8fafc] border-r border-slate-200 p-6 flex flex-col justify-between h-[calc(100vh-69px)] overflow-y-auto shrink-0 text-left">
            <div>
                <h2 className="text-base font-bold text-slate-900 tracking-tight">Búsqueda Inteligente</h2>
                <p className="text-xs text-slate-400 mt-0.5 mb-6">Refina tus resultados</p>

                {/* Sección Nombre del Profesor */}
                <div className="mb-5">
                    <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-2">
                        👤 Nombre del Profesor
                    </label>
                    <input
                        type="text"
                        value={nombreProfesor}
                        onChange={(e) => setNombreProfesor(e.target.value)}
                        placeholder="Ej: Roberto Sánchez"
                        className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-400 transition-colors shadow-sm"
                    />
                </div>

                {/* Sección Institución */}
                <div className="mb-5">
                    <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-2">
                        🎓 Institución
                    </label>
                    <div className="space-y-2">
                        <div>
                            <span className="text-[9px] font-bold text-slate-400 block mb-1">UNIVERSIDAD</span>
                            <select className="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 font-medium focus:outline-none focus:border-sky-400 shadow-sm cursor-pointer">
                                <option>Universidad Nacional</option>
                            </select>
                        </div>
                        <div>
                            <span className="text-[9px] font-bold text-slate-400 block mb-1">FACULTAD</span>
                            <select className="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 font-medium focus:outline-none focus:border-sky-400 shadow-sm cursor-pointer">
                                <option>Ingeniería y Sistemas</option>
                            </select>
                        </div>
                        <div>
                            <span className="text-[9px] font-bold text-slate-400 block mb-1">CARRERA</span>
                            <select className="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 font-medium focus:outline-none focus:border-sky-400 shadow-sm cursor-pointer">
                                <option>Ingeniería Civil</option>
                            </select>
                        </div>
                        <div>
                            <span className="text-[9px] font-bold text-slate-400 block mb-1">CURSO</span>
                            <select className="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 font-medium focus:outline-none focus:border-sky-400 shadow-sm cursor-pointer">
                                <option>Algoritmos 1</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Sección Facilidad */}
                <div className="mb-5">
                    <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-2">
                        ⭐ Facilidad
                    </label>
                    <input
                        type="range"
                        min="0"
                        max="100"
                        value={facilidad}
                        onChange={(e) => setFacilidad(Number(e.target.value))}
                        className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#ff8a00]"
                    />
                    <div className="flex justify-between text-[10px] font-bold text-slate-400 mt-1">
                        <span>Fácil</span>
                        <span>Exigente</span>
                    </div>
                </div>

                {/* Sección Evaluación */}
                <div className="mb-5">
                    <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-2">
                        📝 Evaluación
                    </label>
                    <div className="space-y-2">
                        {[
                            { id: 'eval_teoricos', label: 'Exámenes Teóricos' },
                            { id: 'eval_practicos', label: 'Proyectos Prácticos', defaultChecked: true },
                            { id: 'eval_clase', label: 'Participación en clase' }
                        ].map((item) => (
                            <label key={item.id} className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    id={item.id}
                                    defaultChecked={item.defaultChecked}
                                    className="w-3.5 h-3.5 rounded border-slate-300 text-[#ff8a00] focus:ring-[#ff8a00]/20 cursor-pointer accent-[#ff8a00]"
                                />
                                <span className="text-xs font-medium text-slate-600">{item.label}</span>
                            </label>
                        ))}
                    </div>
                </div>

                {/* Sección Etiquetas (Corregida con Multiselección Activa) */}
                <div className="mb-6">
                    <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-2">
                        🏷️ Etiquetas
                    </label>
                    <div className="flex flex-wrap gap-1.5">
                        {['Barco', 'Exigente', 'Inspirador', 'Teórico'].map((tagName) => {
                            const isSelected = etiquetasSeleccionadas.includes(tagName);
                            return (
                                <button
                                    key={tagName}
                                    type="button"
                                    onClick={() => toggleEtiqueta(tagName)}
                                    className={`px-2.5 py-1 rounded-full text-[10px] font-bold transition-all duration-150 border cursor-pointer select-none ${isSelected
                                            ? 'bg-sky-100 text-sky-700 border-sky-300 shadow-sm'
                                            : 'bg-white text-slate-400 border-slate-200 hover:border-slate-300 hover:text-slate-600'
                                        }`}
                                >
                                    {tagName}
                                </button>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* Botón Aplicar abajo */}
            <div className="pt-4 border-t border-slate-200/60">
                <button
                    type="button"
                    className="w-full py-2.5 bg-[#ff8a00] hover:bg-[#ea580c] text-white font-bold text-xs rounded-lg transition-colors shadow-sm text-center cursor-pointer"
                >
                    Aplicar Filtros
                </button>
            </div>
        </aside>
    );
}
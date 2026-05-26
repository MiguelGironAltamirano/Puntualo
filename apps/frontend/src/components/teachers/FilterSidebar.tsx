'use client'

import { useState, useCallback, useEffect } from 'react';
import { ProfessorFilterState } from '@/lib/hooks-filters';
import { useUniversities, useFaculties, useCourses } from '@/lib/hooks-catalogs';

interface FilterSidebarProps {
    onFiltersChange?: (filters: Partial<ProfessorFilterState>) => void;
}

export default function FilterSidebar({ onFiltersChange }: FilterSidebarProps) {
    const [teacherName, setTeacherName] = useState('');
    const [difficulty, setDifficulty] = useState(50);
    const [selectedTags, setSelectedTags] = useState<string[]>(['Barco']);
    const [minScore, setMinScore] = useState(0);
    const [maxScore, setMaxScore] = useState(5);
    
    // Dropdown state
    const [selectedUniversity, setSelectedUniversity] = useState<number | null>(1);
    const [selectedFaculty, setSelectedFaculty] = useState<number | null>(null);
    const [selectedCourse, setSelectedCourse] = useState<number | null>(null);

    // Fetch dropdown data
    const { data: universities } = useUniversities();
    const { data: faculties } = useFaculties(selectedUniversity);
    const { data: courses } = useCourses(selectedFaculty);

    // Toggle tag selection
    const toggleTag = (tagName: string) => {
        setSelectedTags(prev => 
            prev.includes(tagName)
                ? prev.filter(t => t !== tagName)
                : [...prev, tagName]
        );
    };

    // Call parent callback when filters change
    useEffect(() => {
        if (onFiltersChange) {
            const filters: Partial<ProfessorFilterState> = {
                search: teacherName || undefined,
                min_global_score: minScore > 0 ? minScore : undefined,
                max_global_score: maxScore < 5 ? maxScore : undefined,
                min_easiness: difficulty > 50 ? 5 - (difficulty / 100) * 5 : undefined,
            };
            onFiltersChange(filters);
        }
    }, [teacherName, difficulty, minScore, maxScore, selectedTags, onFiltersChange]);

    return (
        <aside className="w-64 bg-[#f8fafc] border-r border-slate-200 p-6 flex flex-col justify-between h-[calc(100vh-69px)] overflow-y-auto shrink-0 text-left">
            <div>
                <h2 className="text-base font-bold text-slate-900 tracking-tight">Búsqueda Inteligente</h2>
                <p className="text-xs text-slate-400 mt-0.5 mb-6">Refina tus resultados</p>

                {/* Professor Name Section */}
                <div className="mb-5">
                    <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-2">
                        👤 Nombre del Profesor
                    </label>
                    <input
                        type="text"
                        value={teacherName}
                        onChange={(e) => setTeacherName(e.target.value)}
                        placeholder="Ej: Roberto Sánchez"
                        className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-400 transition-colors shadow-sm"
                    />
                </div>

                {/* Institution Section */}
                <div className="mb-5">
                    <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-2">
                        🎓 Institución
                    </label>
                    <div className="space-y-2">
                        <div>
                            <span className="text-[9px] font-bold text-slate-400 block mb-1">UNIVERSIDAD</span>
                            <select 
                                value={selectedUniversity || ''}
                                onChange={(e) => {
                                    const val = Number(e.target.value);
                                    setSelectedUniversity(val || null);
                                    setSelectedFaculty(null);
                                    setSelectedCourse(null);
                                }}
                                className="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 font-medium focus:outline-none focus:border-sky-400 shadow-sm cursor-pointer"
                            >
                                <option value="">Seleccionar universidad...</option>
                                {universities?.map(u => (
                                    <option key={u.id} value={u.id}>{u.name}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <span className="text-[9px] font-bold text-slate-400 block mb-1">FACULTAD</span>
                            <select 
                                value={selectedFaculty || ''}
                                onChange={(e) => {
                                    const val = Number(e.target.value);
                                    setSelectedFaculty(val || null);
                                    setSelectedCourse(null);
                                }}
                                disabled={!selectedUniversity}
                                className="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 font-medium focus:outline-none focus:border-sky-400 shadow-sm cursor-pointer disabled:bg-slate-100 disabled:text-slate-400"
                            >
                                <option value="">
                                    {!selectedUniversity ? 'Seleccionar universidad primero' : 'Seleccionar facultad...'}
                                </option>
                                {faculties?.map(f => (
                                    <option key={f.id} value={f.id}>{f.name}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <span className="text-[9px] font-bold text-slate-400 block mb-1">CARRERA</span>
                            <select 
                                value={selectedCourse || ''}
                                onChange={(e) => {
                                    const val = Number(e.target.value);
                                    setSelectedCourse(val || null);
                                }}
                                disabled={!selectedFaculty}
                                className="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 font-medium focus:outline-none focus:border-sky-400 shadow-sm cursor-pointer disabled:bg-slate-100 disabled:text-slate-400"
                            >
                                <option value="">
                                    {!selectedFaculty ? 'Seleccionar facultad primero' : 'Seleccionar curso...'}
                                </option>
                                {courses?.items?.map(c => (
                                    <option key={c.id} value={c.id}>{c.name}</option>
                                ))}
                            </select>
                        </div>
                        {/* CURSO placeholder (kept for future use) */}
                        <div>
                            <span className="text-[9px] font-bold text-slate-400 block mb-1">CURSO</span>
                            <select className="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 font-medium focus:outline-none focus:border-sky-400 shadow-sm cursor-pointer" disabled>
                                <option>Seleccionar curso primero</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Difficulty Section */}
                <div className="mb-5">
                    <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-2">
                        ⭐ Facilidad
                    </label>
                    <input
                        type="range"
                        min="0"
                        max="100"
                        value={difficulty}
                        onChange={(e) => setDifficulty(Number(e.target.value))}
                        className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#ff8a00]"
                    />
                    <div className="flex justify-between text-[10px] font-bold text-slate-400 mt-1">
                        <span>Fácil</span>
                        <span>Exigente</span>
                    </div>
                </div>

                {/* Score Range Section */}
                <div className="mb-5">
                    <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-2">
                        🌟 Calificación Mínima
                    </label>
                    <div className="space-y-2">
                        <div>
                            <div className="flex justify-between text-[9px] font-bold text-slate-400 mb-1">
                                <span>Min: {minScore.toFixed(1)}</span>
                                <span>Max: {maxScore.toFixed(1)}</span>
                            </div>
                            <div className="flex gap-2">
                                <input
                                    type="range"
                                    min="0"
                                    max="5"
                                    step="0.5"
                                    value={minScore}
                                    onChange={(e) => setMinScore(Math.min(Number(e.target.value), maxScore))}
                                    className="flex-1 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#ff8a00]"
                                />
                                <input
                                    type="range"
                                    min="0"
                                    max="5"
                                    step="0.5"
                                    value={maxScore}
                                    onChange={(e) => setMaxScore(Math.max(Number(e.target.value), minScore))}
                                    className="flex-1 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#ff8a00]"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Evaluation Section */}
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

                {/* Tags Section */}
                <div className="mb-6">
                    <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-2">
                        🏷️ Etiquetas
                    </label>
                    <div className="flex flex-wrap gap-1.5">
                        {['Barco', 'Exigente', 'Inspirador', 'Teórico'].map((tagName) => {
                            const isSelected = selectedTags.includes(tagName);
                            return (
                                <button
                                    key={tagName}
                                    type="button"
                                    onClick={() => toggleTag(tagName)}
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

            {/* Apply Filters Button */}
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
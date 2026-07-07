import { useState, useCallback, useEffect } from 'react';
import { ProfessorFilterState } from '@/lib/hooks-filters';
import { useUniversities, useFaculties, useCourses } from '@/lib/hooks-catalogs';
import { X, ChevronLeft } from 'lucide-react';

interface FilterSidebarProps {
    onFiltersChange?: (filters: Partial<ProfessorFilterState>) => void;
    isOpen?: boolean;
    onClose?: () => void;
    isCollapsed?: boolean;
    onCollapseToggle?: () => void;
}

export default function FilterSidebar({ 
    onFiltersChange, 
    isOpen, 
    onClose,
    isCollapsed = false,
    onCollapseToggle
}: FilterSidebarProps) {
    const [selectedUniversity, setSelectedUniversity] = useState<number | null>(1);
    const [selectedFaculty, setSelectedFaculty] = useState<number | null>(null);
    const [selectedCourse, setSelectedCourse] = useState<number | null>(null);
    const [minEvaluations, setMinEvaluations] = useState<number | ''>('');
    const [minScore, setMinScore] = useState(1.0);
    const [minClarity, setMinClarity] = useState(1.0);
    const [minEasiness, setMinEasiness] = useState(1.0);
    const [minHelpfulness, setMinHelpfulness] = useState(1.0);
    const [minPunctuality, setMinPunctuality] = useState(1.0);
    
    // Fetch dropdown data
    const { data: universities } = useUniversities();
    const { data: faculties } = useFaculties(selectedUniversity);
    const { data: courses } = useCourses(selectedFaculty);

    // Reset filters
    const handleReset = () => {
        setSelectedUniversity(1);
        setSelectedFaculty(null);
        setSelectedCourse(null);
        setMinEvaluations('');
        setMinScore(1.0);
        setMinClarity(1.0);
        setMinEasiness(1.0);
        setMinHelpfulness(1.0);
        setMinPunctuality(1.0);
    };

    // Call parent callback when filters change
    useEffect(() => {
        if (onFiltersChange) {
            const filters: Partial<ProfessorFilterState> = {
                university_id: selectedUniversity || undefined,
                faculty_id: selectedFaculty || undefined,
                course_id: selectedCourse || undefined,
                min_global_score: minScore > 1.0 ? minScore : undefined,
                min_clarity: minClarity > 1.0 ? minClarity : undefined,
                min_easiness: minEasiness > 1.0 ? minEasiness : undefined,
                min_helpfulness: minHelpfulness > 1.0 ? minHelpfulness : undefined,
                min_punctuality: minPunctuality > 1.0 ? minPunctuality : undefined,
                min_evaluations: minEvaluations !== '' && minEvaluations > 0 ? Number(minEvaluations) : undefined,
            };
            onFiltersChange(filters);
        }
    }, [
        selectedUniversity,
        selectedFaculty,
        selectedCourse,
        minScore,
        minClarity,
        minEasiness,
        minHelpfulness,
        minPunctuality,
        minEvaluations,
        onFiltersChange
    ]);

    return (
        <>
            {/* Mobile Drawer Overlay */}
            <div 
                onClick={onClose}
                className={`fixed inset-0 bg-black/50 backdrop-blur-sm z-45 transition-opacity duration-300 md:hidden ${
                    isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
                }`}
            />

            <aside className={`
                bg-[#f8fafc] border-r border-slate-200 p-6 flex flex-col justify-between text-left
                /* Mobile Drawer positioning */
                fixed inset-y-0 left-0 z-50 w-[80%] max-w-[320px] h-full shadow-2xl transition-all duration-300 transform overflow-y-auto
                ${isOpen ? 'translate-x-0' : '-translate-x-full'}
                /* Desktop positioning overrides */
                md:relative md:inset-auto md:z-0 md:flex md:h-[calc(100vh-69px)] md:shadow-none md:translate-x-0 md:overflow-y-auto md:shrink-0
                ${isCollapsed ? 'md:w-0 md:p-0 md:border-r-0 md:opacity-0 md:overflow-hidden' : 'md:w-64 md:opacity-100'}
            `}>
                <div>
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h2 className="text-base font-bold text-slate-900 tracking-tight">Búsqueda Inteligente</h2>
                            <p className="text-xs text-slate-400 mt-0.5">Refina tus resultados</p>
                        </div>
                        <div className="flex items-center gap-1">
                            {onCollapseToggle && (
                                <button
                                    type="button"
                                    onClick={onCollapseToggle}
                                    className="hidden md:flex p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
                                    aria-label="Colapsar filtros"
                                >
                                    <ChevronLeft className="w-5 h-5" />
                                </button>
                            )}
                            <button
                                type="button"
                                onClick={onClose}
                                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors md:hidden cursor-pointer"
                                aria-label="Cerrar filtros"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                {/* Institution Section */}
                <div className="mb-4">
                    <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-1.5">
                        🎓 Institución y Cursos
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
                            <span className="text-[9px] font-bold text-slate-400 block mb-1">CURSO</span>
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
                    </div>
                </div>

                {/* Score and Metrics Section */}
                <div className="mb-4 space-y-3">
                    <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-0.5">
                        ⭐ Métricas Mínimas
                    </label>

                    {/* Global Score Slider */}
                    <div>
                        <div className="flex justify-between text-[9px] font-bold text-slate-400 mb-1">
                            <span>CALIFICACIÓN GLOBAL</span>
                            <span>{minScore > 1.0 ? `${minScore.toFixed(1)} +` : 'Cualquiera'}</span>
                        </div>
                        <input
                            type="range"
                            min="1.0"
                            max="5.0"
                            step="0.5"
                            value={minScore}
                            onChange={(e) => setMinScore(Number(e.target.value))}
                            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#ff8a00]"
                        />
                    </div>

                    {/* Clarity Slider */}
                    <div>
                        <div className="flex justify-between text-[9px] font-bold text-slate-400 mb-1">
                            <span>CLARIDAD AL EXPLICAR</span>
                            <span>{minClarity > 1.0 ? `${minClarity.toFixed(1)} +` : 'Cualquiera'}</span>
                        </div>
                        <input
                            type="range"
                            min="1.0"
                            max="5.0"
                            step="0.5"
                            value={minClarity}
                            onChange={(e) => setMinClarity(Number(e.target.value))}
                            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#ff8a00]"
                        />
                    </div>

                    {/* Easiness Slider */}
                    <div>
                        <div className="flex justify-between text-[9px] font-bold text-slate-400 mb-1">
                            <span>FACILIDAD</span>
                            <span>{minEasiness > 1.0 ? `${minEasiness.toFixed(1)} +` : 'Cualquiera'}</span>
                        </div>
                        <input
                            type="range"
                            min="1.0"
                            max="5.0"
                            step="0.5"
                            value={minEasiness}
                            onChange={(e) => setMinEasiness(Number(e.target.value))}
                            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#ff8a00]"
                        />
                    </div>

                    {/* Helpfulness Slider */}
                    <div>
                        <div className="flex justify-between text-[9px] font-bold text-slate-400 mb-1">
                            <span>AYUDA AL ALUMNO</span>
                            <span>{minHelpfulness > 1.0 ? `${minHelpfulness.toFixed(1)} +` : 'Cualquiera'}</span>
                        </div>
                        <input
                            type="range"
                            min="1.0"
                            max="5.0"
                            step="0.5"
                            value={minHelpfulness}
                            onChange={(e) => setMinHelpfulness(Number(e.target.value))}
                            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#ff8a00]"
                        />
                    </div>

                    {/* Punctuality Slider */}
                    <div>
                        <div className="flex justify-between text-[9px] font-bold text-slate-400 mb-1">
                            <span>PUNTUALIDAD</span>
                            <span>{minPunctuality > 1.0 ? `${minPunctuality.toFixed(1)} +` : 'Cualquiera'}</span>
                        </div>
                        <input
                            type="range"
                            min="1.0"
                            max="5.0"
                            step="0.5"
                            value={minPunctuality}
                            onChange={(e) => setMinPunctuality(Number(e.target.value))}
                            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#ff8a00]"
                        />
                    </div>
                </div>

                {/* Evaluations Count Section */}
                <div className="mb-6">
                    <label className="text-[10px] font-black text-slate-700 uppercase tracking-wider block mb-1.5">
                        📝 Cantidad de Evaluaciones
                    </label>
                    <div>
                        <div className="flex justify-between text-[9px] font-bold text-slate-400 mb-1">
                            <span>EVALUACIONES MÍNIMAS</span>
                            <span>{minEvaluations || 'Cualquiera'}</span>
                        </div>
                        <input
                            type="number"
                            min="0"
                            value={minEvaluations}
                            onChange={(e) => {
                                const val = e.target.value;
                                setMinEvaluations(val === '' ? '' : Math.max(0, parseInt(val) || 0));
                            }}
                            placeholder="Ej: 3"
                            className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-400 transition-colors shadow-sm"
                        />
                    </div>
                </div>
            </div>

            {/* Apply and Reset Buttons */}
            <div className="pt-4 border-t border-slate-200/60 space-y-2">
                <button
                    type="button"
                    onClick={onClose}
                    className="w-full py-2.5 bg-[#ff8a00] hover:bg-[#ea580c] text-white font-bold text-xs rounded-lg transition-colors shadow-sm text-center cursor-pointer"
                >
                    Aplicar Filtros
                </button>
                <button
                    type="button"
                    onClick={handleReset}
                    className="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold text-xs rounded-lg transition-colors shadow-sm text-center cursor-pointer"
                >
                    Limpiar Filtros
                </button>
            </div>
        </aside>
        </>
    );
}
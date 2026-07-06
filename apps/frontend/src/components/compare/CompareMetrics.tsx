import { Teacher } from './types';

interface CompareMetricsProps {
    slotA: Teacher | null;
    slotB: Teacher | null;
}

const ProgressBar = ({ value, max = 5, colorClass = "bg-orange-500" }: { value: number, max?: number, colorClass?: string }) => {
    const percentage = (value / max) * 100;
    return (
        <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden mt-2">
            <div className={`h-full ${colorClass} transition-all duration-500`} style={{ width: `${percentage}%` }}></div>
        </div>
    );
};

const getGenericLabel = (value: number) => {
    if (value >= 4.5) return 'Excelente';
    if (value >= 3.5) return 'Bueno';
    if (value >= 2.5) return 'Aceptable';
    if (value > 0) return 'Por mejorar';
    return '—';
};

const getDifficultyLabel = (value: number) => {
    if (value >= 4.0) return 'Muy difícil';
    if (value >= 3.0) return 'Difícil';
    if (value >= 2.0) return 'Moderado';
    if (value > 0) return 'Fácil';
    return '—';
};

export function CompareMetrics({ slotA, slotB }: CompareMetricsProps) {
    if (!slotA && !slotB) return null;

    return (
        <div className="mt-12 border-t border-slate-100 pt-10 animate-fadeIn">
            <h2 className="text-xl font-black text-[#0284c7] mb-8 tracking-tight">Comparativa de Métricas</h2>

            <div className="space-y-10">
                {/* 1. Nivel de Aprendizaje (Rating) */}
                <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Nivel de Aprendizaje</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-6">
                        <div>
                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5">
                                {slotA ? slotA.name : 'Docente A'}
                            </div>
                            <div className="flex justify-between text-xs font-bold text-slate-700">
                                <span>{slotA ? slotA.rating.toFixed(1) : '—'}</span>
                                <span className="text-slate-400 font-medium">{slotA ? getGenericLabel(slotA.rating) : '—'}</span>
                            </div>
                            <ProgressBar value={slotA ? slotA.rating : 0} colorClass="bg-orange-500" />
                        </div>
                        <div>
                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5">
                                {slotB ? slotB.name : 'Docente B'}
                            </div>
                            <div className="flex justify-between text-xs font-bold text-slate-700">
                                <span>{slotB ? slotB.rating.toFixed(1) : '—'}</span>
                                <span className="text-slate-400 font-medium">{slotB ? getGenericLabel(slotB.rating) : '—'}</span>
                            </div>
                            <ProgressBar value={slotB ? slotB.rating : 0} colorClass="bg-orange-500" />
                        </div>
                    </div>
                </div>

                {/* 2. Nivel de Dificultad */}
                <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Nivel de Dificultad</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-6">
                        <div>
                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5">
                                {slotA ? slotA.name : 'Docente A'}
                            </div>
                            <div className="flex justify-between text-xs font-bold text-slate-700">
                                <span>{slotA ? slotA.difficulty.toFixed(1) : '—'}</span>
                                <span className="text-slate-400 font-medium">{slotA ? getDifficultyLabel(slotA.difficulty) : '—'}</span>
                            </div>
                            <ProgressBar value={slotA ? slotA.difficulty : 0} colorClass="bg-[#0e4e6c]" />
                        </div>
                        <div>
                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5">
                                {slotB ? slotB.name : 'Docente B'}
                            </div>
                            <div className="flex justify-between text-xs font-bold text-slate-700">
                                <span>{slotB ? slotB.difficulty.toFixed(1) : '—'}</span>
                                <span className="text-slate-400 font-medium">{slotB ? getDifficultyLabel(slotB.difficulty) : '—'}</span>
                            </div>
                            <ProgressBar value={slotB ? slotB.difficulty : 0} colorClass="bg-[#0e4e6c]" />
                        </div>
                    </div>
                </div>

                {/* 3. Claridad al Explicar */}
                <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Claridad al Explicar</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-6">
                        <div>
                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5">
                                {slotA ? slotA.name : 'Docente A'}
                            </div>
                            <div className="flex justify-between text-xs font-bold text-slate-700">
                                <span>{slotA ? slotA.clarity.toFixed(1) : '—'}</span>
                                <span className="text-slate-400 font-medium">{slotA ? getGenericLabel(slotA.clarity) : '—'}</span>
                            </div>
                            <ProgressBar value={slotA ? slotA.clarity : 0} colorClass="bg-orange-500" />
                        </div>
                        <div>
                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5">
                                {slotB ? slotB.name : 'Docente B'}
                            </div>
                            <div className="flex justify-between text-xs font-bold text-slate-700">
                                <span>{slotB ? slotB.clarity.toFixed(1) : '—'}</span>
                                <span className="text-slate-400 font-medium">{slotB ? getGenericLabel(slotB.clarity) : '—'}</span>
                            </div>
                            <ProgressBar value={slotB ? slotB.clarity : 0} colorClass="bg-orange-500" />
                        </div>
                    </div>
                </div>

                {/* 4. Ayuda al Alumno / Utilidad */}
                <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Ayuda al Alumno</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-6">
                        <div>
                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5">
                                {slotA ? slotA.name : 'Docente A'}
                            </div>
                            <div className="flex justify-between text-xs font-bold text-slate-700">
                                <span>{slotA ? slotA.helpfulness.toFixed(1) : '—'}</span>
                                <span className="text-slate-400 font-medium">{slotA ? getGenericLabel(slotA.helpfulness) : '—'}</span>
                            </div>
                            <ProgressBar value={slotA ? slotA.helpfulness : 0} colorClass="bg-orange-500" />
                        </div>
                        <div>
                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5">
                                {slotB ? slotB.name : 'Docente B'}
                            </div>
                            <div className="flex justify-between text-xs font-bold text-slate-700">
                                <span>{slotB ? slotB.helpfulness.toFixed(1) : '—'}</span>
                                <span className="text-slate-400 font-medium">{slotB ? getGenericLabel(slotB.helpfulness) : '—'}</span>
                            </div>
                            <ProgressBar value={slotB ? slotB.helpfulness : 0} colorClass="bg-orange-500" />
                        </div>
                    </div>
                </div>

                {/* 5. Puntualidad */}
                <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Puntualidad</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-6">
                        <div>
                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5">
                                {slotA ? slotA.name : 'Docente A'}
                            </div>
                            <div className="flex justify-between text-xs font-bold text-slate-700">
                                <span>{slotA ? slotA.punctuality.toFixed(1) : '—'}</span>
                                <span className="text-slate-400 font-medium">{slotA ? getGenericLabel(slotA.punctuality) : '—'}</span>
                            </div>
                            <ProgressBar value={slotA ? slotA.punctuality : 0} colorClass="bg-orange-500" />
                        </div>
                        <div>
                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5">
                                {slotB ? slotB.name : 'Docente B'}
                            </div>
                            <div className="flex justify-between text-xs font-bold text-slate-700">
                                <span>{slotB ? slotB.punctuality.toFixed(1) : '—'}</span>
                                <span className="text-slate-400 font-medium">{slotB ? getGenericLabel(slotB.punctuality) : '—'}</span>
                            </div>
                            <ProgressBar value={slotB ? slotB.punctuality : 0} colorClass="bg-orange-500" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

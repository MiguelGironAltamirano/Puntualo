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

export function CompareMetrics({ slotA, slotB }: CompareMetricsProps) {
    if (!slotA && !slotB) return null;

    return (
        <div className="mt-12 border-t border-slate-100 pt-10 animate-fadeIn">
            <h2 className="text-xl font-black text-[#0284c7] mb-8 tracking-tight">Comparativa de Métricas</h2>

            <div className="space-y-10">
                {/* 1. Nivel de Aprendizaje */}
                <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Nivel de Aprendizaje</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-6">
                        <div>
                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5">
                                {slotA ? slotA.name : 'Docente A'}
                            </div>
                            <div className="flex justify-between text-xs font-bold text-slate-700">
                                <span>{slotA ? slotA.rating : '—'}</span>
                                <span className="text-slate-400 font-medium">Alto</span>
                            </div>
                            <ProgressBar value={slotA ? slotA.rating : 0} colorClass="bg-orange-500" />
                        </div>
                        <div>
                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5">
                                {slotB ? slotB.name : 'Docente B'}
                            </div>
                            <div className="flex justify-between text-xs font-bold text-slate-700">
                                <span>{slotB ? slotB.rating : '—'}</span>
                                <span className="text-slate-400 font-medium">Excelente</span>
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
                                <span>{slotA ? slotA.difficulty : '—'}</span>
                                <span className="text-slate-400 font-medium">Moderado</span>
                            </div>
                            <ProgressBar value={slotA ? slotA.difficulty : 0} colorClass="bg-[#0e4e6c]" />
                        </div>
                        <div>
                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5">
                                {slotB ? slotB.name : 'Docente B'}
                            </div>
                            <div className="flex justify-between text-xs font-bold text-slate-700">
                                <span>{slotB ? slotB.difficulty : '—'}</span>
                                <span className="text-slate-400 font-medium">Alto</span>
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
                                <span>{slotA ? slotA.clarity : '—'}</span>
                                <span className="text-slate-400 font-medium">Muy Claro</span>
                            </div>
                            <ProgressBar value={slotA ? slotA.clarity : 0} colorClass="bg-orange-500" />
                        </div>
                        <div>
                            <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5">
                                {slotB ? slotB.name : 'Docente B'}
                            </div>
                            <div className="flex justify-between text-xs font-bold text-slate-700">
                                <span>{slotB ? slotB.clarity : '—'}</span>
                                <span className="text-slate-400 font-medium">Perfecto</span>
                            </div>
                            <ProgressBar value={slotB ? slotB.clarity : 0} colorClass="bg-orange-500" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

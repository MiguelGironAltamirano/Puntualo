import { Teacher } from './types';
import { Sparkles, CheckCircle2, Info } from 'lucide-react';

interface IASummaryProps {
    slotA: Teacher | null;
    slotB: Teacher | null;
}

export function IASummary({ slotA, slotB }: IASummaryProps) {
    if (!slotA && !slotB) return null;
    
    return (
        <div className="mt-12 border-t border-slate-100 pt-10 animate-fadeIn">
            {/* Cabecera Estilizada de IA */}
            <div className="flex gap-4 items-start mb-8">
                <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center text-sky-600 shadow-sm border border-sky-100 shrink-0">
                    <Sparkles className="w-5 h-5 text-[#0284c7]" />
                </div>
                <div className="space-y-1">
                    <div className="flex items-center gap-2">
                        <h3 className="text-sm font-black text-sky-950 tracking-wider uppercase">Síntesis de IA</h3>
                        <span className="bg-sky-500/10 text-sky-700 text-[9px] font-black px-1.5 py-0.5 rounded-md tracking-widest">BETA</span>
                    </div>
                    <p className="text-xs text-slate-500 font-medium leading-relaxed">
                        Comparación automatizada de metodologías y opiniones en base a reseñas.
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* DOCENTE A */}
                <div>
                    {slotA ? (
                        <div className="bg-[#e0f2fe]/40 border border-sky-100 p-6 rounded-2xl shadow-sm h-full">
                            <h3 className="text-sm font-black text-slate-900 mb-6 pb-4 border-b border-sky-200/50">{slotA.name}</h3>
                            <div className="space-y-6">
                                <div>
                                    <h4 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-3">
                                        Pros
                                    </h4>
                                    <ul className="space-y-2.5">
                                        <li className="flex items-start gap-2.5 text-xs text-slate-700 font-medium">
                                            <CheckCircle2 className="w-4 h-4 text-[#0284c7] shrink-0 mt-0.5" />
                                            <span>Metodología clara y estructurada.</span>
                                        </li>
                                    </ul>
                                </div>
                                <div>
                                    <h4 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-3">
                                        Contras
                                    </h4>
                                    <ul className="space-y-2.5">
                                        <li className="flex items-start gap-2.5 text-xs text-slate-700 font-medium">
                                            <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                                            <span>Exigencia alta en evaluaciones.</span>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="bg-slate-50 border border-slate-100 border-dashed p-6 rounded-2xl h-full flex items-center justify-center text-xs font-medium text-slate-400">
                            Esperando docente...
                        </div>
                    )}
                </div>

                {/* DOCENTE B */}
                <div>
                    {slotB ? (
                        <div className="bg-[#e0f2fe]/40 border border-sky-100 p-6 rounded-2xl shadow-sm h-full">
                            <h3 className="text-sm font-black text-slate-900 mb-6 pb-4 border-b border-sky-200/50">{slotB.name}</h3>
                            <div className="space-y-6">
                                <div>
                                    <h4 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-3">
                                        Pros
                                    </h4>
                                    <ul className="space-y-2.5">
                                        <li className="flex items-start gap-2.5 text-xs text-slate-700 font-medium">
                                            <CheckCircle2 className="w-4 h-4 text-[#0284c7] shrink-0 mt-0.5" />
                                            <span>Excelente dominio de los temas.</span>
                                        </li>
                                    </ul>
                                </div>
                                <div>
                                    <h4 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-3">
                                        Contras
                                    </h4>
                                    <ul className="space-y-2.5">
                                        <li className="flex items-start gap-2.5 text-xs text-slate-700 font-medium">
                                            <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                                            <span>Mucha carga de trabajo adicional.</span>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="bg-slate-50 border border-slate-100 border-dashed p-6 rounded-2xl h-full flex items-center justify-center text-xs font-medium text-slate-400">
                            Esperando docente...
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

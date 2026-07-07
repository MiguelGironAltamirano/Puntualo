import { Teacher } from './types';
import { Sparkles, CheckCircle2, Info } from 'lucide-react';

interface IASummaryProps {
    teachers: Teacher[];
}

export function IASummary({ teachers }: IASummaryProps) {
    if (!teachers || teachers.length === 0) return null;
    
    const gridColsClass = 
        teachers.length === 2 ? 'md:grid-cols-2' : 
        teachers.length === 3 ? 'md:grid-cols-3' : 
        'md:grid-cols-4';

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

            <div className={`grid grid-cols-1 ${gridColsClass} gap-8`}>
                {teachers.map((teacher) => (
                    <div key={teacher.id}>
                        <div className="bg-[#e0f2fe]/40 border border-sky-100 p-6 rounded-2xl shadow-sm h-full">
                            <h3 className="text-sm font-black text-slate-900 mb-6 pb-4 border-b border-sky-200/50 truncate">{teacher.name}</h3>
                            <div className="space-y-6">
                                <div>
                                    <h4 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-3">
                                        Pros
                                    </h4>
                                    <ul className="space-y-2.5">
                                        {teacher.aiSummary?.pros && teacher.aiSummary.pros.length > 0 ? (
                                            teacher.aiSummary.pros.map((pro, idx) => (
                                                <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-700 font-medium">
                                                    <CheckCircle2 className="w-4 h-4 text-[#0284c7] shrink-0 mt-0.5" />
                                                    <span>{pro}</span>
                                                </li>
                                            ))
                                        ) : (
                                            <li className="text-xs text-slate-400">Sin datos de pros</li>
                                        )}
                                    </ul>
                                </div>
                                <div>
                                    <h4 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-3">
                                        Contras
                                    </h4>
                                    <ul className="space-y-2.5">
                                        {teacher.aiSummary?.contras && teacher.aiSummary.contras.length > 0 ? (
                                            teacher.aiSummary.contras.map((contra, idx) => (
                                                <li key={idx} className="flex items-start gap-2.5 text-xs text-slate-700 font-medium">
                                                    <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                                                    <span>{contra}</span>
                                                </li>
                                            ))
                                        ) : (
                                            <li className="text-xs text-slate-400">Sin datos de contras</li>
                                        )}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

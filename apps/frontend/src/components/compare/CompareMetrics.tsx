import { Teacher } from './types';

interface CompareMetricsProps {
    teachers: Teacher[];
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

export function CompareMetrics({ teachers }: CompareMetricsProps) {
    if (!teachers || teachers.length === 0) return null;

    const gridColsClass = 
        teachers.length === 2 ? 'md:grid-cols-2' : 
        teachers.length === 3 ? 'md:grid-cols-3' : 
        'md:grid-cols-4';

    return (
        <div className="mt-12 border-t border-slate-100 pt-10 animate-fadeIn">
            <h2 className="text-xl font-black text-[#0284c7] mb-8 tracking-tight">Comparativa de Métricas</h2>

            <div className="space-y-10">
                {/* 1. Nivel de Aprendizaje (Rating) */}
                <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Nivel de Aprendizaje</h4>
                    <div className={`grid grid-cols-1 ${gridColsClass} gap-x-12 gap-y-6`}>
                        {teachers.map((teacher) => (
                            <div key={teacher.id}>
                                <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5 truncate">
                                    {teacher.name}
                                </div>
                                <div className="flex justify-between text-xs font-bold text-slate-700">
                                    <span>{teacher.rating.toFixed(1)}</span>
                                    <span className="text-slate-400 font-medium">{getGenericLabel(teacher.rating)}</span>
                                </div>
                                <ProgressBar value={teacher.rating} colorClass="bg-orange-500" />
                            </div>
                        ))}
                    </div>
                </div>

                {/* 2. Nivel de Dificultad */}
                <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Nivel de Dificultad</h4>
                    <div className={`grid grid-cols-1 ${gridColsClass} gap-x-12 gap-y-6`}>
                        {teachers.map((teacher) => (
                            <div key={teacher.id}>
                                <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5 truncate">
                                    {teacher.name}
                                </div>
                                <div className="flex justify-between text-xs font-bold text-slate-700">
                                    <span>{teacher.difficulty.toFixed(1)}</span>
                                    <span className="text-slate-400 font-medium">{getDifficultyLabel(teacher.difficulty)}</span>
                                </div>
                                <ProgressBar value={teacher.difficulty} colorClass="bg-[#0e4e6c]" />
                            </div>
                        ))}
                    </div>
                </div>

                {/* 3. Claridad al Explicar */}
                <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Claridad al Explicar</h4>
                    <div className={`grid grid-cols-1 ${gridColsClass} gap-x-12 gap-y-6`}>
                        {teachers.map((teacher) => (
                            <div key={teacher.id}>
                                <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5 truncate">
                                    {teacher.name}
                                </div>
                                <div className="flex justify-between text-xs font-bold text-slate-700">
                                    <span>{teacher.clarity.toFixed(1)}</span>
                                    <span className="text-slate-400 font-medium">{getGenericLabel(teacher.clarity)}</span>
                                </div>
                                <ProgressBar value={teacher.clarity} colorClass="bg-orange-500" />
                            </div>
                        ))}
                    </div>
                </div>

                {/* 4. Ayuda al Alumno / Utilidad */}
                <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Ayuda al Alumno</h4>
                    <div className={`grid grid-cols-1 ${gridColsClass} gap-x-12 gap-y-6`}>
                        {teachers.map((teacher) => (
                            <div key={teacher.id}>
                                <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5 truncate">
                                    {teacher.name}
                                </div>
                                <div className="flex justify-between text-xs font-bold text-slate-700">
                                    <span>{teacher.helpfulness.toFixed(1)}</span>
                                    <span className="text-slate-400 font-medium">{getGenericLabel(teacher.helpfulness)}</span>
                                </div>
                                <ProgressBar value={teacher.helpfulness} colorClass="bg-orange-500" />
                            </div>
                        ))}
                    </div>
                </div>

                {/* 5. Puntualidad */}
                <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Puntualidad</h4>
                    <div className={`grid grid-cols-1 ${gridColsClass} gap-x-12 gap-y-6`}>
                        {teachers.map((teacher) => (
                            <div key={teacher.id}>
                                <div className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1.5 truncate">
                                    {teacher.name}
                                </div>
                                <div className="flex justify-between text-xs font-bold text-slate-700">
                                    <span>{teacher.punctuality.toFixed(1)}</span>
                                    <span className="text-slate-400 font-medium">{getGenericLabel(teacher.punctuality)}</span>
                                </div>
                                <ProgressBar value={teacher.punctuality} colorClass="bg-orange-500" />
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

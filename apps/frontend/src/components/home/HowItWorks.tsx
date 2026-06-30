import { Search, BarChart3, CheckCircle2 } from "lucide-react";

const steps = [
    {
        icon: Search,
        title: "Busca",
        body: "Encuentra al docente por materia, facultad o nombre. Sin rumores de pasillo.",
    },
    {
        icon: BarChart3,
        title: "Compara con datos",
        body: "Revisa métricas de claridad, dificultad y la síntesis por IA de reseñas reales de estudiantes verificados.",
    },
    {
        icon: CheckCircle2,
        title: "Decide con confianza",
        body: "Eliges tu semestre sabiendo a qué atenerte, no de oído.",
    },
];

export function HowItWorks() {
    return (
        <section className="flex flex-col items-center mt-24 w-full">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#0f172a] tracking-tight text-balance text-center mb-3">
                Cómo funciona
            </h2>
            <p className="text-[#64748b] text-sm sm:text-base font-medium mb-14 text-center max-w-2xl">
                Tres pasos para pasar de la incertidumbre a una decisión académica respaldada por datos.
            </p>

            <ol className="grid grid-cols-1 md:grid-cols-3 gap-10 md:gap-6 w-full">
                {steps.map(({ icon: Icon, title, body }, i) => (
                    <li key={title} className="flex flex-col items-center text-center md:items-start md:text-left">
                        <div className="flex items-center gap-3 mb-5">
                            <span className="flex items-center justify-center w-9 h-9 rounded-full bg-[#0284c7] text-white text-sm font-extrabold shrink-0">
                                {i + 1}
                            </span>
                            <Icon className="w-5 h-5 text-[#0284c7]" strokeWidth={2.5} />
                        </div>
                        <h3 className="text-lg font-extrabold text-[#0f172a] mb-2">{title}</h3>
                        <p className="text-[#64748b] text-sm leading-relaxed font-medium max-w-xs">{body}</p>
                    </li>
                ))}
            </ol>
        </section>
    );
}

'use client'

import { Lightbulb, Check, Zap } from "lucide-react";
import { useEffect, useState } from "react";
import { useReducedMotion } from "motion/react";

/**
 * Panel de preview de la Síntesis IA. Muestra un EJEMPLO ilustrativo del producto
 * (no métricas globales reales): un docente de muestra, su consenso y sus métricas.
 * El "Consenso general" se escribe con efecto typing para reforzar la historia de IA.
 */

// Datos de ejemplo (mockup de producto, claramente ilustrativos).
const example = {
    teacher: "Dr. García",
    course: "Cálculo II",
    reviews: 312,
    consenso: "Destaca por su claridad al explicar conceptos complejos y disponibilidad post-clase.",
    puntos: "Sus parciales son de alta dificultad. Se recomienda preparación extra.",
    metrics: [
        { value: "4.7", label: "Claridad", color: "text-[#0f172a]" },
        { value: "3.2", label: "Facilidad", color: "text-[#c2410c]" },
        { value: "4.9", label: "Trato", color: "text-[#15803d]" },
    ],
};

function useTypewriter(text: string, enabled: boolean, speed = 22) {
    const [out, setOut] = useState(enabled ? "" : text);

    useEffect(() => {
        if (!enabled) {
            setOut(text);
            return;
        }
        setOut("");
        let i = 0;
        const id = setInterval(() => {
            i += 1;
            setOut(text.slice(0, i));
            if (i >= text.length) clearInterval(id);
        }, speed);
        return () => clearInterval(id);
    }, [text, enabled, speed]);

    return out;
}

export function HomeAISummary() {
    const reduceMotion = useReducedMotion();
    const typed = useTypewriter(example.consenso, !reduceMotion);
    const done = typed.length >= example.consenso.length;

    return (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-[0_8px_30px_rgb(2,132,199,0.10)] p-5">
            {/* Header del ejemplo */}
            <div className="flex items-start justify-between gap-3 mb-4">
                <div className="flex items-center gap-3 min-w-0">
                    <div className="w-9 h-9 bg-[#f1f5f9] rounded-lg flex items-center justify-center shrink-0">
                        <Lightbulb className="w-4 h-4 text-[#0284c7]" strokeWidth={2.5} />
                    </div>
                    <div className="min-w-0">
                        <p className="text-sm font-extrabold text-[#0f172a] truncate">Síntesis IA — {example.teacher}</p>
                        <p className="text-xs text-[#64748b] truncate">{example.course} · {example.reviews} reseñas</p>
                    </div>
                </div>
                <span className="shrink-0 text-[11px] font-bold text-[#0369a1] bg-[#e0f2fe] px-2.5 py-1 rounded-full">
                    IA activa
                </span>
            </div>

            {/* Caja de consenso */}
            <div className="bg-[#f0f9ff] rounded-xl p-4 border border-blue-50 space-y-3 text-[13px] leading-relaxed">
                <div>
                    <p className="flex items-center gap-1.5 font-extrabold text-[#0369a1]">
                        <Check className="w-3.5 h-3.5" strokeWidth={3} /> Consenso general
                    </p>
                    <p className="text-[#0c4a6e] mt-1 font-medium">
                        {typed}
                        {!done && (
                            <span className="pl-caret inline-block w-[2px] h-[1em] -mb-0.5 bg-[#0369a1] align-middle ml-0.5" aria-hidden="true" />
                        )}
                    </p>
                </div>
                <div className={`transition-opacity duration-500 ${done ? "opacity-100" : "opacity-0"}`}>
                    <p className="flex items-center gap-1.5 font-extrabold text-[#0284c7]">
                        <Zap className="w-3.5 h-3.5" strokeWidth={3} /> Puntos a considerar
                    </p>
                    <p className="text-[#0c4a6e] mt-1 font-medium">{example.puntos}</p>
                </div>
            </div>

            {/* Métricas del ejemplo */}
            <div className="grid grid-cols-3 gap-2 mt-3">
                {example.metrics.map((m) => (
                    <div key={m.label} className="bg-[#f8fafc] border border-gray-100 rounded-xl py-3 text-center">
                        <p className={`text-xl font-extrabold ${m.color}`}>{m.value}</p>
                        <p className="text-[11px] font-semibold text-[#64748b] mt-0.5">{m.label}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

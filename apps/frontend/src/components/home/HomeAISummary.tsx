'use client'

import { Lightbulb, MapPin } from "lucide-react";
import { AISummaryData } from "@/components/globalTypes";

interface HomeAISummaryProps {
    summaryData: AISummaryData;
}

export function HomeAISummary({ summaryData }: HomeAISummaryProps) {
    return (
        <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-[0_4px_20px_rgb(0,0,0,0.03)] hover:shadow-md transition-shadow">
            <div className="w-10 h-10 bg-[#e0f2fe] rounded-xl flex items-center justify-center mb-6">
                <Lightbulb className="w-5 h-5 text-[#0284c7]" strokeWidth={2.5} />
            </div>
            <h3 className="text-lg font-extrabold text-[#0f172a] mb-3">Síntesis IA</h3>
            <p className="text-[#64748b] mb-8 leading-relaxed text-sm font-medium">
                No pierdas tiempo leyendo cientos de comentarios. Nuestro motor procesa todas las evaluaciones para darte un resumen ejecutivo sobre la metodología, exigencia y trato de cada profesor.
            </p>

            <div className="bg-[#f0f9ff] rounded-xl p-5 border border-blue-50 relative overflow-hidden">
                <div className="flex gap-3 relative z-10">
                    <div className="mt-0.5">
                        <MapPin className="w-4 h-4 text-[#0284c7]" strokeWidth={2.5} />
                    </div>
                    <div className="text-[13px] text-[#0c4a6e] leading-relaxed font-medium space-y-2">
                        <p>
                            <span className="font-extrabold text-[#0369a1]">Consenso general:</span> 
                            {' '}{summaryData.pros.join(', ')}
                        </p>
                        {summaryData.contras.length > 0 && (
                            <p className="text-[#0ea5e9]">
                                <span className="font-extrabold">Puntos a considerar:</span>
                                {' '}{summaryData.contras.join(', ')}
                            </p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

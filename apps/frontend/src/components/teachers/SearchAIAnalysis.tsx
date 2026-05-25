import { Sparkles } from "lucide-react";
import { SearchResultsAnalysis } from "@/components/globalTypes";

interface SearchAIAnalysisProps {
    analysis: SearchResultsAnalysis;
}

export function SearchAIAnalysis({ analysis }: SearchAIAnalysisProps) {
    if (!analysis || !analysis.matchesText) return null;

    return (
        <div className="bg-[#e0f2fe]/40 border border-sky-100 rounded-2xl p-5 mb-6 shadow-sm flex items-start gap-4">
            <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center text-sky-600 shadow-sm border border-sky-100 shrink-0">
                <Sparkles className="w-5 h-5 text-[#0284c7]" />
            </div>
            <div className="flex-1 space-y-1 mt-0.5">
                <div className="flex items-center gap-2 mb-1.5">
                    <h3 className="text-[13px] font-black text-sky-950 tracking-wider uppercase">Análisis de resultados</h3>
                    <span className="bg-sky-500/10 text-sky-700 text-[9px] font-black px-1.5 py-0.5 rounded-md tracking-widest">IA</span>
                </div>
                <p className="text-xs text-slate-600 font-medium leading-relaxed">
                    {analysis.matchesText}
                </p>
            </div>
        </div>
    );
}

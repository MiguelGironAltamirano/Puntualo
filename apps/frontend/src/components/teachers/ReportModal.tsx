'use client'

import { useState } from 'react';
import { X, Flag } from 'lucide-react';

interface ReportModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export function ReportModal({ isOpen, onClose }: ReportModalProps) {
    const [reason, setReason] = useState<string | null>(null);
    const [details, setDetails] = useState('');

    if (!isOpen) return null;

    const reasons = [
        "Contenido ofensivo",
        "Información falsa",
        "Spam",
        "No es sobre el docente"
    ];

    return (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4 overflow-y-auto animate-fadeIn">
            <div className="bg-white rounded-3xl border border-slate-100 w-full max-w-sm p-4 sm:p-6 relative shadow-2xl my-auto text-left">
                <button onClick={onClose} className="absolute right-4 top-4 text-slate-400 hover:text-slate-600 hover:bg-slate-50 rounded-xl transition-all p-1.5 cursor-pointer focus:outline-none">
                    <X className="w-5 h-5" />
                </button>
                
                <div className="mb-6 border-b border-slate-100 pb-4">
                    <h2 className="text-lg font-black text-[#0f172a] tracking-tight mb-1">Reportar Comentario</h2>
                    <p className="text-xs text-slate-500 font-medium leading-relaxed">Ayúdanos a mantener la comunidad segura y respetuosa.</p>
                </div>

                <form onSubmit={(e) => { e.preventDefault(); onClose(); }} className="space-y-6">
                    <div>
                        <label className="text-[11px] font-black text-slate-700 uppercase tracking-wider block mb-3">¿Por qué reportas este comentario?</label>
                        <div className="space-y-2.5">
                            {reasons.map((r) => (
                                <label key={r} className={`flex items-center gap-3 p-3.5 rounded-xl border cursor-pointer transition-all ${reason === r ? 'border-[#0284c7] bg-sky-50' : 'border-slate-200 hover:border-slate-300'}`}>
                                    <input 
                                        type="radio" 
                                        name="reportReason" 
                                        value={r} 
                                        checked={reason === r} 
                                        onChange={() => setReason(r)} 
                                        className="w-4 h-4 text-[#0284c7] border-gray-300 focus:ring-[#0284c7] cursor-pointer"
                                    />
                                    <span className="text-xs font-semibold text-slate-700">{r}</span>
                                </label>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="text-[11px] font-black text-slate-700 uppercase tracking-wider block mb-2">Detalles adicionales (opcional)</label>
                        <textarea
                            rows={3}
                            value={details}
                            onChange={(e) => setDetails(e.target.value)}
                            placeholder="Proporciona más contexto para ayudarnos a revisar el reporte..."
                            className="w-full bg-white border border-slate-200 rounded-xl p-3 text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-[#ff8a00] focus:ring-2 focus:ring-orange-50 transition-all resize-none shadow-sm"
                        />
                    </div>

                    {/* Footer Actions */}
                    <div className="flex items-center justify-end gap-3 pt-2">
                        <button type="button" onClick={onClose} className="px-5 py-3 text-xs font-bold text-slate-600 bg-white border border-slate-200 hover:bg-slate-50 rounded-xl transition-colors cursor-pointer">
                            Cancelar
                        </button>
                        <button type="submit" disabled={!reason} className="px-5 py-3 bg-[#ff8a00] hover:bg-[#ea580c] disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-xs rounded-xl transition-all shadow-sm flex items-center gap-1.5 cursor-pointer">
                            <Flag className="w-3.5 h-3.5" /> Enviar Reporte
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

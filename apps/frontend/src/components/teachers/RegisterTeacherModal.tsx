import { useState, useRef } from "react";
import { Camera, Sparkles, UserPlus } from "lucide-react";

interface RegisterTeacherModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export function RegisterTeacherModal({ isOpen, onClose }: RegisterTeacherModalProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setImagePreview(URL.createObjectURL(file));
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl w-full max-w-lg p-8 shadow-xl relative animate-in fade-in zoom-in duration-200">
                {/* Header */}
                <div className="text-center mb-6">
                    <h2 className="text-xl font-bold text-slate-900 mb-1.5">Register New Professor</h2>
                    <p className="text-xs text-slate-500 font-medium">
                        Add academic details to expand the platform database.
                    </p>
                </div>

                {/* Profile Picture Upload */}
                <div className="flex flex-col items-center mb-8">
                    <input type="file" ref={fileInputRef} accept="image/jpeg, image/png" className="hidden" onChange={handleFileChange} />
                    <button type="button" onClick={() => fileInputRef.current?.click()} className="w-20 h-20 rounded-full border-2 border-dashed border-slate-300 bg-slate-50 flex items-center justify-center text-slate-400 hover:text-[#0284c7] hover:border-[#0284c7] hover:bg-sky-50 transition-colors cursor-pointer focus:outline-none overflow-hidden relative">
                        {imagePreview ? (
                            <img src={imagePreview} className="w-full h-full object-cover absolute inset-0" alt="Preview" />
                        ) : (
                            <Camera className="w-6 h-6" />
                        )}
                    </button>
                    <span className="text-[10px] font-medium text-slate-400 mt-2">
                        Upload Profile Picture (Optional)
                    </span>
                </div>

                {/* Form Fields */}
                <form className="space-y-5 mb-6" onSubmit={(e) => e.preventDefault()}>
                    {/* NOMBRES Y APELLIDOS */}
                    <div>
                        <label className="block text-[10px] font-black text-slate-700 uppercase tracking-wider mb-1.5">
                            Nombres y Apellidos Completos
                        </label>
                        <input
                            type="text"
                            placeholder="Ej. Dr. Juan Pérez"
                            className="w-full bg-white border border-slate-200 text-sm font-medium text-slate-800 rounded-lg px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-sky-100 focus:border-sky-300 transition-all placeholder:text-slate-400"
                        />
                    </div>

                    {/* TÍTULO */}
                    <div>
                        <label className="block text-[10px] font-black text-slate-700 uppercase tracking-wider mb-1.5">
                            Título
                        </label>
                        <select className="w-full bg-white border border-slate-200 text-sm font-medium text-slate-800 rounded-lg px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-sky-100 focus:border-sky-300 transition-all appearance-none cursor-pointer">
                            <option value="">Seleccione el título académico</option>
                            <option value="dr">Doctor (Dr.)</option>
                            <option value="dra">Doctora (Dra.)</option>
                            <option value="mtro">Maestro (Mtro.)</option>
                            <option value="mtra">Maestra (Mtra.)</option>
                            <option value="ing">Ingeniero/a (Ing.)</option>
                            <option value="lic">Licenciado/a (Lic.)</option>
                        </select>
                    </div>

                    {/* FACULTAD Y UNIVERSIDAD */}
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-[10px] font-black text-slate-700 uppercase tracking-wider mb-1.5">
                                Facultad
                            </label>
                            <input
                                type="text"
                                placeholder="Ej. Ciencias Exactas"
                                className="w-full bg-white border border-slate-200 text-sm font-medium text-slate-800 rounded-lg px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-sky-100 focus:border-sky-300 transition-all placeholder:text-slate-400"
                            />
                        </div>
                        <div>
                            <label className="block text-[10px] font-black text-slate-700 uppercase tracking-wider mb-1.5">
                                Universidad
                            </label>
                            <input
                                type="text"
                                placeholder="Ej. Universidad Central"
                                className="w-full bg-white border border-slate-200 text-sm font-medium text-slate-800 rounded-lg px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-sky-100 focus:border-sky-300 transition-all placeholder:text-slate-400"
                            />
                        </div>
                    </div>
                </form>

                {/* AI Insight Banner */}
                <div className="bg-[#e0f2fe]/50 border border-sky-100 rounded-xl p-4 mb-8 flex items-start gap-3">
                    <div className="mt-0.5 shrink-0">
                        <Sparkles className="w-4 h-4 text-[#0284c7]" />
                    </div>
                    <p className="text-[11px] text-sky-900 font-medium leading-relaxed">
                        <span className="font-bold text-sky-950">AI Insight:</span> Providing accurate faculty and university names helps our AI accurately link this professor to existing course reviews and departmental statistics.
                    </p>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center justify-end gap-5 pt-4 border-t border-slate-100 mt-auto">
                    <button
                        type="button"
                        onClick={onClose}
                        className="text-[11px] font-bold text-slate-500 hover:text-slate-800 transition-colors cursor-pointer uppercase tracking-wider"
                    >
                        Cancel
                    </button>
                    <button
                        type="button"
                        className="bg-[#ff8a00] hover:bg-[#ea580c] text-white px-6 py-2.5 rounded-lg text-[11px] font-black flex items-center gap-2 transition-colors cursor-pointer uppercase tracking-wider shadow-sm"
                    >
                        Register Professor <UserPlus className="w-3.5 h-3.5" strokeWidth={3} />
                    </button>
                </div>
            </div>
        </div>
    );
}

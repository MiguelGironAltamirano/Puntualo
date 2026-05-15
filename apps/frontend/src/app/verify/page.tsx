'use client'

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';

export default function VerifyPage() {
    const [step, setStep] = useState(1); // 1: Frontal, 2: Trasera
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null); // LA REFERENCIA
    const router = useRouter();

    // FUNCIÓN PARA ABRIR EL EXPLORADOR DE ARCHIVOS
    const handleBoxClick = () => {
        fileInputRef.current?.click();
    };

    // FUNCIÓN PARA CAPTURAR EL ARCHIVO ELEGIDO
    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setSelectedFile(file);
        }
    };

    const handleNext = () => {
        if (step === 1) {
            setStep(2);
            setSelectedFile(null); // Limpiamos para la cara trasera
        } else {
            router.push('/profesores');
        }
    };

    return (
        <main className="flex min-h-screen items-center justify-center bg-[#f0f9ff] p-4 font-sans">
            <div className="w-full max-w-xl bg-white rounded-3xl shadow-xl p-10 border border-gray-100 text-center relative">

                <div className="flex justify-center items-center gap-3 mb-10">
                    <div className={`h-2 w-12 rounded-full ${step >= 1 ? 'bg-[#ff8a00]' : 'bg-gray-200'}`}></div>
                    <div className={`h-2 w-12 rounded-full ${step === 2 ? 'bg-[#ff8a00]' : 'bg-gray-200'}`}></div>
                </div>

                <h2 className="text-3xl font-extrabold text-[#0f172a] mb-3">Verifica tu identidad</h2>
                <p className="text-sm text-[#64748b] mb-10 mx-auto leading-relaxed">
                    Sube una foto de la <br />
                    <span className="font-bold text-[#0284c7] uppercase">
                        {step === 1 ? 'parte delantera' : 'parte trasera'}
                    </span> de tu carnet.
                </p>

                {/* --- AQUÍ ESTÁ EL BLOQUE QUE PREGUNTABAS --- */}
                <div
                    onClick={handleBoxClick}
                    className="group border-2 border-dashed border-[#bae6fd] bg-[#f8fafc] rounded-2xl p-16 mb-10 flex flex-col items-center justify-center cursor-pointer hover:border-[#0284c7] hover:bg-white transition-all"
                >
                    <div className="w-16 h-16 bg-white rounded-2xl shadow-md flex items-center justify-center mb-6 text-2xl">
                        {selectedFile ? '✅' : (step === 1 ? '🪪' : '🔄')}
                    </div>

                    <p className="text-base font-bold text-[#0f172a]">
                        {selectedFile ? selectedFile.name : "Arrastra tu imagen aquí"}
                    </p>

                    {!selectedFile && (
                        <button className="mt-4 px-6 py-2 bg-white border-2 border-[#e0f2fe] rounded-xl text-xs font-bold text-[#0284c7]">
                            Explorar archivos
                        </button>
                    )}

                    {/* ESTE INPUT ES INVISIBLE PERO HACE EL TRABAJO */}
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileChange}
                        className="hidden"
                        accept="image/png, image/jpeg"
                    />
                </div>

                <div className="flex flex-col gap-4">
                    <button
                        onClick={handleNext}
                        className="w-full py-4 bg-[#ff8a00] hover:bg-[#ea580c] text-white font-bold rounded-2xl shadow-lg transition-all active:scale-[0.98]"
                    >
                        {step === 1 ? 'Siguiente paso →' : 'Finalizar Verificación'}
                    </button>

                    <button
                        onClick={() => router.push('/profesores')}
                        className="text-sm font-bold text-[#94a3b8] hover:text-[#0f172a] transition-colors"
                    >
                        Omitir paso por ahora
                    </button>
                </div>
            </div>
        </main>
    );
}
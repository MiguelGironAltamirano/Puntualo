'use client'

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';

export default function VerifyPage() {
    const [step, setStep] = useState(1); // 1: Frontal, 2: Trasera, 3: Éxito (Documentos Recibidos)
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const fileInputRef = useRef<HTMLInputElement>(null);
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
            setErrorMessage('');
            setSuccessMessage('');
        }
    };

    const uploadSide = async (side: 'front' | 'back') => {
        if (!selectedFile) {
            return false;
        }

        setUploading(true);
        setErrorMessage('');
        setSuccessMessage('');

        const token = localStorage.getItem('access_token');
        if (!token) {
            setUploading(false);
            setErrorMessage('Debes iniciar sesion para verificar tu identidad');
            return false;
        }

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const formData = new FormData();
            formData.append('file', selectedFile);

            const res = await fetch(`${apiUrl}/verification/carnet/${side}`, {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${token}`
                },
                body: formData
            });

            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
                setErrorMessage(data.detail?.message || data.detail || 'No se pudo subir la imagen');
                setUploading(false);
                return false;
            }

            setSuccessMessage(data.detail || 'Imagen subida correctamente');
            setUploading(false);
            return true;
        } catch {
            setErrorMessage('Error de conexion con el servidor');
            setUploading(false);
            return false;
        }
    };

    const handleNext = async () => {
        if (!selectedFile || uploading) {
            return;
        }

        const side = step === 1 ? 'front' : 'back';
        const ok = await uploadSide(side);

        if (!ok) {
            return;
        }

        if (step === 1) {
            setStep(2);
            setSelectedFile(null); // Limpiamos para la cara trasera
            setSuccessMessage('');
        } else if (step === 2) {
            setStep(3); // Pasamos a la pantalla de éxito que pide Figma
        }
    };

    // --- PANTALLA DE ÉXITO: DOCUMENTOS RECIBIDOS (PASO 3) ---
    if (step === 3) {
        return (
            <main className="flex min-h-screen items-center justify-center bg-[#f0f9ff] p-4 font-sans">
                <div className="w-full max-w-xl bg-white rounded-3xl shadow-xl p-10 border border-gray-100 text-center flex flex-col items-center">

                    {/* Logotipo o Nombre del Sistema */}
                    <span className="text-sm font-semibold text-[#0ea5e9] tracking-wide mb-4">Puntúalo</span>

                    {/* Icono de Check con Sombra Difuminada */}
                    <div className="w-20 h-20 bg-white border border-gray-50 rounded-full shadow-lg flex items-center justify-center mb-8 relative">
                        <div className="w-14 h-14 bg-gradient-to-br from-orange-400 to-orange-500 rounded-full flex items-center justify-center text-white text-2xl shadow-md">
                            ✓
                        </div>
                        <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-orange-400 border-2 border-white rounded-full"></div>
                    </div>

                    {/* Título y Mensaje de Figma */}
                    <h2 className="text-3xl font-extrabold text-[#0f172a] mb-4">¡Documentos recibidos!</h2>
                    <p className="text-sm text-[#64748b] leading-relaxed mb-8 max-w-sm">
                        Hemos recibido las fotos de tu carnet universitario correctamente. Nuestro equipo de verificación revisará la información y el proceso tardará aproximadamente <span className="font-bold text-[#0f172a]">1 día hábil</span>.
                    </p>

                    {/* Caja Informativa de Próximos Pasos */}
                    <div className="w-full bg-[#f8fafc] rounded-2xl p-5 border border-gray-100 flex gap-4 text-left mb-10">
                        <div className="w-10 h-10 bg-[#e0f2fe] rounded-xl flex items-center justify-center text-xl shrink-0">
                            ✉️
                        </div>
                        <div>
                            <h4 className="text-sm font-bold text-[#0f172a] mb-1">Próximos pasos</h4>
                            <p className="text-xs text-[#64748b] leading-relaxed">
                                Recibirás la confirmación de tu estado de verificación directamente en tu correo electrónico de Gmail registrado. Mantente atento a tu bandeja de entrada.
                            </p>
                        </div>
                    </div>

                    {/* Botones de Acción de Figma */}
                    <div className="w-full flex flex-col sm:flex-row gap-4">
                        <button
                            onClick={() => router.push('/teachers')}
                            className="flex-1 py-4 bg-[#ff8a00] hover:bg-[#ea580c] text-white font-bold rounded-2xl shadow-md transition-all active:scale-[0.98] text-sm"
                        >
                            Continuar al Buscador
                        </button>
                        <button
                            onClick={() => router.push('/')}
                            className="flex-1 py-4 bg-white border-2 border-[#bae6fd] hover:border-[#0284c7] text-[#0284c7] font-bold rounded-2xl transition-all text-sm"
                        >
                            Volver al Inicio
                        </button>
                    </div>

                </div>
            </main>
        );
    }

    // --- FLUJO TRADICIONAL (PASO 1 Y 2) ---
    return (
        <main className="flex min-h-screen items-center justify-center bg-[#f0f9ff] p-4 font-sans">
            <div className="w-full max-w-xl bg-white rounded-3xl shadow-xl p-10 border border-gray-100 text-center relative">

                {/* Indicador de barra de progreso */}
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

                {/* Zona de arrastre / Dropzone */}
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

                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileChange}
                        className="hidden"
                        accept="image/png, image/jpeg"
                    />
                </div>

                {errorMessage && (
                    <div className="mb-6 rounded-xl bg-red-100 px-4 py-3 text-sm text-red-700">
                        {errorMessage}
                    </div>
                )}

                {successMessage && (
                    <div className="mb-6 rounded-xl bg-green-100 px-4 py-3 text-sm text-green-700">
                        {successMessage}
                    </div>
                )}

                {/* Acciones principales */}
                <div className="flex flex-col gap-4">
                    <button
                        onClick={handleNext}
                        disabled={!selectedFile || uploading}
                        className="w-full py-4 bg-[#ff8a00] hover:bg-[#ea580c] disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-2xl shadow-lg transition-all active:scale-[0.98]"
                    >
                        {uploading
                            ? 'Subiendo imagen...'
                            : (step === 1 ? 'Siguiente paso →' : 'Finalizar Verificación')}
                    </button>

                    <button
                        onClick={() => router.push('/teachers')}
                        className="text-sm font-bold text-[#94a3b8] hover:text-[#0f172a] transition-colors"
                    >
                        Omitir paso por ahora
                    </button>
                </div>
            </div>
        </main>
    );
}
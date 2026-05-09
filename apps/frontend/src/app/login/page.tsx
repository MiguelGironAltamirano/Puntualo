'use client'

import { useState } from 'react';

export default function AuthPage() {
    // --- ESTADOS DEL FORMULARIO ---
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [username, setUsername] = useState('');
    const [career, setCareer] = useState('');
    const [file, setFile] = useState<File | null>(null); // Estado para RF-02

    // --- LÓGICA DE NAVEGACIÓN INTERNA ---
    const toggleMode = () => {
        setIsLogin(!isLogin);
        // Limpieza de campos para evitar persistencia entre Login y Registro
        setEmail('');
        setPassword('');
        setUsername('');
        setCareer('');
        setFile(null);
    };

    // --- MANEJO DE ENVÍO (Submit) ---
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        // Validación obligatoria de archivo para nuevos registros (RF-02)
        if (!isLogin && !file) {
            alert("Por favor, sube tu carnet o matrícula para validar tu cuenta.");
            return;
        }
        console.log("Datos listos para Backend:", { email, file });
        alert(isLogin ? 'Iniciando sesión...' : 'Registro enviado para validación institucional.');
    };

    return (
        <main className="flex min-h-screen items-center justify-center bg-[#f0f9ff] p-4">

            <div className="w-full max-w-md bg-white rounded-xl shadow-2xl p-8 border border-gray-100">

                {/* CABECERA: Branding de Puntualo */}
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-extrabold text-[#004a7c]">Puntualo</h1>
                    <p className="text-sm text-gray-400 mt-1 italic">La guía precisa para tu carrera</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">

                    {/* BLOQUE: Datos de Identidad (Solo en Registro) */}
                    {!isLogin && (
                        <div>
                            <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider ml-1">Nombre de Usuario</label>
                            <div className="relative mt-1">
                                <span className="absolute inset-y-0 left-3 flex items-center text-gray-600 text-base">🎓</span>
                                <input
                                    type="text"
                                    required
                                    placeholder="estudiante123"
                                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:ring-2 focus:ring-orange-400 outline-none text-sm text-gray-800 placeholder:text-gray-300"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                            </div>
                        </div>
                    )}

                    {/* BLOQUE: Credenciales Universitarias (Login/Registro) */}
                    <div>
                        <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider ml-1">Correo Universitario</label>
                        <div className="relative mt-1">
                            <span className="absolute inset-y-0 left-3 flex items-center text-gray-600 text-base">🎓</span>
                            <input
                                type="email"
                                required
                                placeholder="estudiante@unmsm.edu.pe"
                                pattern=".+@unmsm\.edu\.pe" // Validación de dominio institucional
                                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:ring-2 focus:ring-orange-400 outline-none text-sm text-gray-800 placeholder:text-gray-300"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider ml-1">Contraseña</label>
                        <div className="relative mt-1">
                            <span className="absolute inset-y-0 left-3 flex items-center text-gray-600 text-sm">🔒</span>
                            <input
                                type="password"
                                required
                                placeholder="........"
                                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:ring-2 focus:ring-orange-400 outline-none text-sm text-gray-800 placeholder:text-gray-300"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                    </div>

                    {/* BLOQUE: Requerimientos Funcionales (RF-02 - Solo en Registro) */}
                    {!isLogin && (
                        <>
                            <div>
                                <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider ml-1">Carrera (Opcional)</label>
                                <div className="relative mt-1">
                                    <span className="absolute inset-y-0 left-3 flex items-center text-gray-600 text-base">🎓</span>
                                    <input
                                        type="text"
                                        placeholder="Ingeniería X"
                                        className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:ring-2 focus:ring-orange-400 outline-none text-sm text-gray-800 placeholder:text-gray-300"
                                        value={career}
                                        onChange={(e) => setCareer(e.target.value)}
                                    />
                                </div>
                            </div>

                            {/* Botón personalizado para carga de archivos (RF-02) */}
                            <div className="pt-2">
                                <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider ml-1 mb-2">Foto del Carnet / Matrícula (JPG/PDF)</label>
                                <label className="inline-block px-4 py-2 bg-blue-50 text-blue-700 text-xs font-bold rounded-lg cursor-pointer hover:bg-blue-100 border border-blue-100 shadow-sm transition-transform active:scale-95">
                                    Elegir archivo
                                    <input
                                        type="file"
                                        required
                                        accept=".jpg,.jpeg,.pdf" // Restricción técnica de formatos
                                        className="hidden"
                                        onChange={(e) => setFile(e.target.files?.[0] || null)}
                                    />
                                </label>
                                {file && <span className="ml-3 text-[10px] text-green-600 font-semibold italic">{file.name}</span>}
                            </div>
                        </>
                    )}

                    {/* ACCIONES DE FORMULARIO */}
                    {isLogin && (
                        <div className="text-right">
                            <button type="button" className="text-[11px] text-[#004a7c] opacity-80 hover:opacity-100 font-semibold transition-opacity">Olvidé mi contraseña</button>
                        </div>
                    )}

                    <button
                        type="submit"
                        className="w-full py-3 bg-[#ff8a00] hover:bg-[#e67e00] text-white font-bold rounded-lg shadow-md transition-all flex items-center justify-center gap-2 mt-4 active:scale-[0.98]"
                    >
                        {isLogin ? 'Acceder' : 'Crear cuenta'} <span>→</span>
                    </button>
                </form>

                {/* PIE DE PÁGINA: Switch entre vistas */}
                <div className="text-center mt-8">
                    <button
                        onClick={toggleMode}
                        className="text-[12px] text-gray-500 font-medium"
                    >
                        {isLogin ? (
                            <>¿Aún no estás en Puntualo? <span className="text-[#004a7c] font-bold hover:underline">Crear cuenta</span></>
                        ) : (
                            <span className="text-[#004a7c] font-bold hover:underline">Volver al Login</span>
                        )}
                    </button>
                </div>
            </div>
        </main>
    );
}
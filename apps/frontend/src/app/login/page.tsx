'use client'

import { useState } from 'react';
import Link from 'next/link';

export default function AuthPage() {
    // --- ESTADOS DEL FORMULARIO ---
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    // --- MANEJO DE ENVÍO (Submit) ---
    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        console.log("Datos listos para Backend login:", { email });
        alert('Iniciando sesión...');
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

                    {/* BLOQUE: Credenciales Universitarias (Login) */}
                    <div>
                        <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider ml-1">Correo Universitario</label>
                        <div className="relative mt-1">
                            <span className="absolute inset-y-0 left-3 flex items-center text-gray-600 text-base">✉️</span>
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

                    {/* ACCIONES DE FORMULARIO */}
                    <div className="text-right">
                        <button type="button" className="text-[11px] text-[#004a7c] opacity-80 hover:opacity-100 font-semibold transition-opacity">Olvidé mi contraseña</button>
                    </div>

                    <button
                        type="submit"
                        className="w-full py-3 bg-[#ff8a00] hover:bg-[#e67e00] text-white font-bold rounded-lg shadow-md transition-all flex items-center justify-center gap-2 mt-4 active:scale-[0.98]"
                    >
                        Acceder <span>→</span>
                    </button>
                </form>

                {/* PIE DE PÁGINA: Switch a Registro */}
                <div className="text-center mt-8">
                    <p className="text-[12px] text-gray-500 font-medium">
                        ¿Aún no estás en Puntualo?{' '}
                        <Link href="/register" className="text-[#004a7c] font-bold hover:underline">
                            Crear cuenta
                        </Link>
                    </p>
                </div>
            </div>
        </main>
    );
}
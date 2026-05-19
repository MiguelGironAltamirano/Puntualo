'use client'

import { useState } from 'react';
import Link from 'next/link';

export default function AuthPage() {
    // --- ESTADOS DEL FORMULARIO ---
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    // --- MANEJO DE ENVÍO (Submit) ---
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            if (!res.ok) {
                const data = await res.json();
                setError(data.detail || 'Credenciales inválidas');
                setLoading(false);
                return;
            }

            const data = await res.json();
            localStorage.setItem('access_token', data.access_token);
            if (data.refresh_token) {
                localStorage.setItem('refresh_token', data.refresh_token);
            }

            window.location.href = '/profesores';
        } catch {
            setError('Error de conexión con el servidor');
            setLoading(false);
        }
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
                    {error && (
                        <div className="p-3 bg-red-100 text-red-700 rounded-lg text-sm mb-4">
                            {error}
                        </div>
                    )}

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
                        disabled={loading}
                        className={`w-full py-3 text-white font-bold rounded-lg shadow-md transition-all flex items-center justify-center gap-2 mt-4 active:scale-[0.98] ${
                            loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-[#ff8a00] hover:bg-[#e67e00]'
                        }`}
                    >
                        {loading ? 'Accediendo...' : (
                            <>Acceder <span>→</span></>
                        )}
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
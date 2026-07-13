'use client'

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Mail, Lock } from 'lucide-react';

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

            // Redirigir según el rol del usuario (reconocimiento automático)
            if (data.role === 'admin') {
                window.location.href = '/admin';
            } else {
                window.location.href = '/teachers';
            }
        } catch {
            setError('Error de conexión con el servidor');
            setLoading(false);
        }
    };

    return (
        <main className="flex min-h-screen items-center justify-center bg-[#f0f9ff] p-4">

            <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl p-8 sm:p-10 border border-gray-100">

                {/* CABECERA: Branding de Puntualo */}
                <div className="text-center mb-8">
                    <Link href="/" className="inline-flex">
                        <Image
                            src="/puntualo_logo.png"
                            alt="Puntualo"
                            width={490}
                            height={200}
                            priority
                            fetchPriority="high"
                            className="h-14 w-auto mx-auto"
                        />
                    </Link>
                    <p className="text-base text-gray-400 mt-2 italic">La guía precisa para tu carrera</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {error && (
                        <div className="p-3 bg-red-100 text-red-700 rounded-xl text-sm mb-4">
                            {error}
                        </div>
                    )}

                    {/* BLOQUE: Credenciales Universitarias (Login) */}
                    <div>
                        <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Correo Universitario</label>
                        <div className="relative mt-1">
                            <span className="absolute inset-y-0 left-4 flex items-center text-gray-600">
                                <Mail className="w-4 h-4" />
                            </span>
                            <input
                                type="email"
                                required
                                autoComplete="username"
                                placeholder="estudiante@unmsm.edu.pe"
                                pattern=".+@unmsm\.edu\.pe" // Validación de dominio institucional
                                className="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:border-sky-300 text-base text-gray-800 placeholder:text-gray-400"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Contraseña</label>
                        <div className="relative mt-1">
                            <span className="absolute inset-y-0 left-4 flex items-center text-gray-600">
                                <Lock className="w-4 h-4" />
                            </span>
                            <input
                                type="password"
                                required
                                autoComplete="current-password"
                                placeholder="········"
                                className="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:border-sky-300 text-base text-gray-800 placeholder:text-gray-400"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                    </div>

                    {/* ACCIONES DE FORMULARIO */}
                    <div className="text-right">
                        <Link
                            href="/reset-password"
                            className="text-sm text-[#0284c7] opacity-80 hover:opacity-100 font-semibold transition-opacity"
                        >
                            Olvidé mi contraseña
                        </Link>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full py-3.5 text-white font-bold text-base rounded-full shadow-md transition-all flex items-center justify-center gap-2 mt-4 active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-orange-300 focus-visible:ring-offset-2 ${
                            loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-[#c2410c] hover:bg-[#9a3412]'
                        }`}
                    >
                        {loading ? 'Accediendo...' : (
                            <>Acceder <span>→</span></>
                        )}
                    </button>
                </form>

                {/* PIE DE PÁGINA: Switch a Registro */}
                <div className="text-center mt-8">
                    <p className="text-sm text-gray-500 font-medium">
                        ¿Aún no estás en Puntualo?{' '}
                        <Link href="/register" className="text-[#0284c7] font-bold hover:underline">
                            Crear cuenta
                        </Link>
                    </p>
                </div>
            </div>
        </main>
    );
}
'use client'

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { BookOpen, GraduationCap, IdCard, Lock, Mail, User } from 'lucide-react';

export default function RegisterPage() {
    // --- ESTADOS DEL FORMULARIO ---
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [username, setUsername] = useState('');
    const [fullName, setFullName] = useState('');
    const [dni, setDni] = useState('');
    const [career, setCareer] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [showCodeModal, setShowCodeModal] = useState(false);
    const [code, setCode] = useState('');
    const [codeError, setCodeError] = useState('');
    const [verifyLoading, setVerifyLoading] = useState(false);
    const [pendingEmail, setPendingEmail] = useState('');

    // --- MANEJO DE ENVÍO (Submit) ---
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // Nota: la verificación de documento se maneja en un flujo separado.

        setLoading(true);

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email,
                    password,
                    username,
                    full_name: fullName,
                    dni: dni || null,
                    career: career || null
                })
            });

            if (!res.ok) {
                const data = await res.json();
                setError(data.detail || 'Ocurrió un error en el registro');
                setLoading(false);
                return;
            }

            setLoading(false);
            setPendingEmail(email);
            setCode('');
            setCodeError('');
            setShowCodeModal(true);
        } catch {
            setError('Error de conexión con el servidor');
            setLoading(false);
        }
    };

    const handleVerify = async (e: React.FormEvent) => {
        e.preventDefault();
        setCodeError('');
        setVerifyLoading(true);

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/auth/register/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: pendingEmail, code })
            });

            if (!res.ok) {
                const data = await res.json();
                setCodeError(data.detail || 'Codigo invalido');
                setVerifyLoading(false);
                return;
            }

            const loginRes = await fetch(`${apiUrl}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: pendingEmail, password })
            });

            if (loginRes.ok) {
                const loginData = await loginRes.json();
                localStorage.setItem('access_token', loginData.access_token);
                if (loginData.refresh_token) {
                    localStorage.setItem('refresh_token', loginData.refresh_token);
                }
            }

            setVerifyLoading(false);
            window.location.href = '/verify';
        } catch {
            setCodeError('Error de conexión con el servidor');
            setVerifyLoading(false);
        }
    };

    return (
        <main className="flex min-h-screen items-center justify-center bg-[#f0f9ff] p-4">
            {showCodeModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
                    <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl p-6 sm:p-8 border border-gray-100">
                        <h2 className="text-2xl font-extrabold text-[#0f172a]">Verifica tu correo</h2>
                        <p className="text-base text-gray-500 mt-2">
                            Enviamos un codigo de 6 digitos a <span className="font-semibold text-gray-700">{pendingEmail}</span>.
                        </p>

                        {codeError && (
                            <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-xl text-sm">
                                {codeError}
                            </div>
                        )}

                        <form onSubmit={handleVerify} className="mt-6 space-y-4">
                            <div>
                                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Codigo de verificacion</label>
                                <input
                                    type="text"
                                    inputMode="numeric"
                                    pattern="\d{6}"
                                    maxLength={6}
                                    required
                                    placeholder="123456"
                                    className="w-full mt-1 px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:border-sky-300 text-base text-gray-800 placeholder:text-gray-400"
                                    value={code}
                                    onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={verifyLoading || code.length !== 6}
                                className={`w-full py-3.5 text-white font-bold text-base rounded-full shadow-md transition-all flex items-center justify-center gap-2 active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-orange-300 focus-visible:ring-offset-2 ${
                                    verifyLoading || code.length !== 6 ? 'bg-gray-400 cursor-not-allowed' : 'bg-[#c2410c] hover:bg-[#9a3412]'
                                }`}
                            >
                                {verifyLoading ? 'Verificando...' : 'Validar codigo'}
                            </button>
                        </form>
                    </div>
                </div>
            )}

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

                    {/* BLOQUE: Datos de Identidad */}
                    <div>
                        <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Nombre Completo</label>
                        <div className="relative mt-1">
                            <span className="absolute inset-y-0 left-4 flex items-center text-gray-600">
                                <User className="w-4 h-4" />
                            </span>
                            <input
                                type="text"
                                required
                                placeholder="Juan Pérez"
                                className="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:border-sky-300 text-base text-gray-800 placeholder:text-gray-400"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Nombre de Usuario</label>
                        <div className="relative mt-1">
                            <span className="absolute inset-y-0 left-4 flex items-center text-gray-600">
                                <GraduationCap className="w-4 h-4" />
                            </span>
                            <input
                                type="text"
                                required
                                placeholder="estudiante123"
                                className="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:border-sky-300 text-base text-gray-800 placeholder:text-gray-400"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">DNI (Opcional)</label>
                        <div className="relative mt-1">
                            <span className="absolute inset-y-0 left-4 flex items-center text-gray-600">
                                <IdCard className="w-4 h-4" />
                            </span>
                            <input
                                type="text"
                                placeholder="12345678"
                                className="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:border-sky-300 text-base text-gray-800 placeholder:text-gray-400"
                                value={dni}
                                onChange={(e) => setDni(e.target.value)}
                            />
                        </div>
                    </div>

                    {/* BLOQUE: Credenciales Universitarias */}
                    <div>
                        <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Correo Universitario</label>
                        <div className="relative mt-1">
                            <span className="absolute inset-y-0 left-4 flex items-center text-gray-600">
                                <Mail className="w-4 h-4" />
                            </span>
                            <input
                                type="email"
                                required
                                placeholder="estudiante@unmsm.edu.pe"
                                pattern=".+@unmsm\.edu\.pe"
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
                                placeholder="........"
                                className="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:border-sky-300 text-base text-gray-800 placeholder:text-gray-400"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                    </div>

                    {/* BLOQUE: Requerimientos Funcionales (RF-02) */}
                    <div>
                        <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Carrera (Opcional)</label>
                        <div className="relative mt-1">
                            <span className="absolute inset-y-0 left-4 flex items-center text-gray-600">
                                <BookOpen className="w-4 h-4" />
                            </span>
                            <input
                                type="text"
                                placeholder="Ingeniería X"
                                className="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:border-sky-300 text-base text-gray-800 placeholder:text-gray-400"
                                value={career}
                                onChange={(e) => setCareer(e.target.value)}
                            />
                        </div>
                    </div>

                    {/* La carga de documento se gestiona en un flujo de verificación separado */}

                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full py-3.5 text-white font-bold text-base rounded-full shadow-md transition-all flex items-center justify-center gap-2 mt-4 active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-orange-300 focus-visible:ring-offset-2 ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-[#c2410c] hover:bg-[#9a3412]'
                            }`}
                    >
                        {loading ? 'Procesando...' : (
                            <>Crear cuenta <span>→</span></>
                        )}
                    </button>
                </form>

                {/* PIE DE PÁGINA: Switch a Login */}
                <div className="text-center mt-8">
                    <p className="text-sm text-gray-500 font-medium">
                        ¿Ya tienes una cuenta en Puntualo?{' '}
                        <Link href="/login" className="text-[#0284c7] font-bold hover:underline">
                            Inicia sesión
                        </Link>
                    </p>
                </div>
            </div>
        </main>
    );
}
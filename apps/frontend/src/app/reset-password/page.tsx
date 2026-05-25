'use client'

import { useState } from 'react';
import Link from 'next/link';
import { Lock, Mail, ShieldCheck } from 'lucide-react';

export default function ResetPasswordPage() {
    const [email, setEmail] = useState('');
    const [code, setCode] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [info, setInfo] = useState('');
    const [loading, setLoading] = useState(false);
    const [codeSent, setCodeSent] = useState(false);
    const [codeVerified, setCodeVerified] = useState(false);

    const handleSendCode = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setInfo('');
        setLoading(true);

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/auth/password-reset/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email })
            });

            if (!res.ok) {
                const data = await res.json();
                setError(data.detail || 'No se pudo enviar el codigo');
                setLoading(false);
                return;
            }

            setCodeSent(true);
            setInfo('Te enviamos un codigo de 6 digitos a tu correo.');
            setLoading(false);
        } catch {
            setError('Error de conexión con el servidor');
            setLoading(false);
        }
    };

    const handleVerifyCode = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setInfo('');
        setLoading(true);

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/auth/password-reset/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, code })
            });

            if (!res.ok) {
                const data = await res.json();
                setError(data.detail || 'Codigo invalido');
                setLoading(false);
                return;
            }

            setCodeVerified(true);
            setInfo('Codigo verificado. Ahora crea una nueva contraseña.');
            setLoading(false);
        } catch {
            setError('Error de conexión con el servidor');
            setLoading(false);
        }
    };

    const handleConfirmPassword = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setInfo('');
        setLoading(true);

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/auth/password-reset/confirm`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email,
                    code,
                    new_password: newPassword,
                    confirm_password: confirmPassword
                })
            });

            if (!res.ok) {
                const data = await res.json();
                setError(data.detail || 'No se pudo actualizar la contraseña');
                setLoading(false);
                return;
            }

            setInfo('Contraseña actualizada. Redirigiendo al login...');
            setLoading(false);
            setTimeout(() => {
                window.location.href = '/login';
            }, 1200);
        } catch {
            setError('Error de conexión con el servidor');
            setLoading(false);
        }
    };

    return (
        <main className="flex min-h-screen items-center justify-center bg-[#f0f9ff] p-4">
            <div className="w-full max-w-md bg-white rounded-xl shadow-2xl p-8 border border-gray-100">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-extrabold text-[#004a7c]">Puntualo</h1>
                    <p className="text-sm text-gray-400 mt-1 italic">Recupera tu acceso</p>
                </div>

                {error && (
                    <div className="p-3 bg-red-100 text-red-700 rounded-lg text-sm mb-4">
                        {error}
                    </div>
                )}

                {info && (
                    <div className="p-3 bg-blue-100 text-blue-700 rounded-lg text-sm mb-4">
                        {info}
                    </div>
                )}

                {!codeVerified ? (
                    <form onSubmit={codeSent ? handleVerifyCode : handleSendCode} className="space-y-4">
                        <div>
                            <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider ml-1">Correo Universitario</label>
                            <div className="relative mt-1">
                                <span className="absolute inset-y-0 left-3 flex items-center text-gray-600">
                                    <Mail className="w-4 h-4" />
                                </span>
                                <input
                                    type="email"
                                    required
                                    placeholder="estudiante@unmsm.edu.pe"
                                    pattern=".+@unmsm\.edu\.pe"
                                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:ring-2 focus:ring-orange-400 outline-none text-sm text-gray-800 placeholder:text-gray-300"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                        </div>

                        {codeSent && (
                            <div>
                                <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider ml-1">Codigo de 6 digitos</label>
                                <div className="relative mt-1">
                                    <span className="absolute inset-y-0 left-3 flex items-center text-gray-600">
                                        <ShieldCheck className="w-4 h-4" />
                                    </span>
                                    <input
                                        type="text"
                                        inputMode="numeric"
                                        pattern="\d{6}"
                                        maxLength={6}
                                        required
                                        placeholder="123456"
                                        className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:ring-2 focus:ring-orange-400 outline-none text-sm text-gray-800 placeholder:text-gray-300"
                                        value={code}
                                        onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                                    />
                                </div>
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={loading || (codeSent && code.length !== 6)}
                            className={`w-full py-3 text-white font-bold rounded-lg shadow-md transition-all flex items-center justify-center gap-2 mt-4 active:scale-[0.98] ${
                                loading || (codeSent && code.length !== 6) ? 'bg-gray-400 cursor-not-allowed' : 'bg-[#ff8a00] hover:bg-[#e67e00]'
                            }`}
                        >
                            {loading ? 'Procesando...' : (codeSent ? 'Validar codigo' : 'Enviar codigo')}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleConfirmPassword} className="space-y-4">
                        <div>
                            <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider ml-1">Nueva Contraseña</label>
                            <div className="relative mt-1">
                                <span className="absolute inset-y-0 left-3 flex items-center text-gray-600">
                                    <Lock className="w-4 h-4" />
                                </span>
                                <input
                                    type="password"
                                    required
                                    placeholder="........"
                                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:ring-2 focus:ring-orange-400 outline-none text-sm text-gray-800 placeholder:text-gray-300"
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-[10px] font-bold text-gray-500 uppercase tracking-wider ml-1">Confirmar Nueva Contraseña</label>
                            <div className="relative mt-1">
                                <span className="absolute inset-y-0 left-3 flex items-center text-gray-600">
                                    <Lock className="w-4 h-4" />
                                </span>
                                <input
                                    type="password"
                                    required
                                    placeholder="........"
                                    className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg bg-gray-50 focus:ring-2 focus:ring-orange-400 outline-none text-sm text-gray-800 placeholder:text-gray-300"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className={`w-full py-3 text-white font-bold rounded-lg shadow-md transition-all flex items-center justify-center gap-2 mt-4 active:scale-[0.98] ${
                                loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-[#ff8a00] hover:bg-[#e67e00]'
                            }`}
                        >
                            {loading ? 'Actualizando...' : 'Cambiar contraseña'}
                        </button>
                    </form>
                )}

                <div className="text-center mt-8">
                    <p className="text-[12px] text-gray-500 font-medium">
                        ¿Ya recuerdas tu contraseña?{' '}
                        <Link href="/login" className="text-[#004a7c] font-bold hover:underline">
                            Volver al login
                        </Link>
                    </p>
                </div>
            </div>
        </main>
    );
}

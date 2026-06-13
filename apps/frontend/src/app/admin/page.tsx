'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
    BadgeCheck,
    GraduationCap,
    Gavel,
    BarChart3,
    Loader2,
} from 'lucide-react';

interface AdminStats {
    users_pending: number;
    professors_pending: number;
}

export default function AdminDashboard() {
    const router = useRouter();
    const [stats, setStats] = useState<AdminStats | null>(null);
    const [loadingStats, setLoadingStats] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            router.replace('/login');
            return;
        }

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        fetch(`${apiUrl}/admin/stats`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then((res) => {
                if (res.status === 401 || res.status === 403) {
                    router.replace('/login');
                    return null;
                }
                return res.json();
            })
            .then((data) => {
                if (data) setStats(data);
            })
            .catch(() => {
                // No bloquear la UI si falla la carga de stats
                setStats({ users_pending: 0, professors_pending: 0 });
            })
            .finally(() => setLoadingStats(false));
    }, [router]);

    return (
        <div className="min-h-screen flex flex-col bg-[#f0f9ff]">
            {/* Contenido principal */}
            <main className="flex-1 max-w-4xl mx-auto w-full px-6 py-10">

                {/* Encabezado */}
                <div className="mb-8">
                    <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">
                        Panel de Administración
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Bienvenido al centro de control. Gestiona verificaciones y monitorea la actividad de la plataforma.
                    </p>
                </div>

                {/* Lista de tarjetas de acción */}
                <div className="flex flex-col gap-4">

                    {/* Tarjeta 1: Aprobar Verificación de Usuarios */}
                    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
                        <div className="flex items-start justify-between mb-4">
                            <div className="p-3 bg-blue-50 rounded-xl">
                                <BadgeCheck className="w-6 h-6 text-blue-500" />
                            </div>
                            {loadingStats ? (
                                <span className="flex items-center gap-1 text-[11px] font-bold bg-red-50 text-red-500 px-3 py-1 rounded-full">
                                    <Loader2 className="w-3 h-3 animate-spin" /> Cargando...
                                </span>
                            ) : (
                                <span className="text-[11px] font-bold tracking-widest bg-red-50 text-red-500 px-3 py-1 rounded-full uppercase">
                                    {stats?.users_pending ?? 0} Pendientes
                                </span>
                            )}
                        </div>
                        <h2 className="text-lg font-bold text-gray-900 mb-1">
                            Aprobar Verificación de Usuarios
                        </h2>
                        <p className="text-sm text-gray-500 mb-5">
                            Revisa la documentación e identidad de los nuevos estudiantes
                            registrados para habilitar su acceso completo a la plataforma.
                        </p>
                        <button
                            id="btn-comenzar-revision"
                            onClick={() => router.push('/admin/users/verify')}
                            className="inline-flex items-center gap-2 bg-[#ff8a00] hover:bg-[#e67e00] active:scale-[0.98] text-white font-bold text-sm px-5 py-2.5 rounded-lg transition-all shadow-sm"
                        >
                            Comenzar Revisión →
                        </button>
                    </div>

                    {/* Tarjeta 2: Aprobar Validación de Profesores */}
                    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
                        <div className="flex items-start justify-between mb-4">
                            <div className="p-3 bg-blue-50 rounded-xl">
                                <GraduationCap className="w-6 h-6 text-blue-500" />
                            </div>
                            {loadingStats ? (
                                <span className="flex items-center gap-1 text-[11px] font-bold bg-orange-50 text-orange-500 px-3 py-1 rounded-full">
                                    <Loader2 className="w-3 h-3 animate-spin" /> Cargando...
                                </span>
                            ) : (
                                <span className="text-[11px] font-bold tracking-widest bg-orange-50 text-orange-500 px-3 py-1 rounded-full uppercase">
                                    {stats?.professors_pending ?? 0} Pendientes
                                </span>
                            )}
                        </div>
                        <h2 className="text-lg font-bold text-gray-900 mb-1">
                            Aprobar Validación de Profesores
                        </h2>
                        <p className="text-sm text-gray-500 mb-5">
                            Verifica las credenciales académicas y la vinculación institucional de
                            los docentes para asegurar la calidad educativa.
                        </p>
                        <button
                            id="btn-validar-docentes"
                            onClick={() => router.push('/admin/teachers/validate')}
                            className="inline-flex items-center gap-2 bg-[#ff8a00] hover:bg-[#e67e00] active:scale-[0.98] text-white font-bold text-sm px-5 py-2.5 rounded-lg transition-all shadow-sm"
                        >
                            Validar Docentes →
                        </button>
                    </div>

                    {/* Tarjeta 3: Gestión de Baneos por Comentarios */}
                    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
                        <div className="flex items-start justify-between mb-4">
                            <div className="p-3 bg-blue-50 rounded-xl">
                                <Gavel className="w-6 h-6 text-blue-500" />
                            </div>
                        </div>
                        <h2 className="text-lg font-bold text-gray-900 mb-1">
                            Gestión de Baneos por Comentarios
                        </h2>
                        <p className="text-sm text-gray-500 mb-5">
                            Revisa los reportes de comentarios inapropiados y gestiona las
                            suspensiones de usuarios según las normas de la comunidad.
                        </p>
                        <button
                            id="btn-gestionar-baneos"
                            onClick={() => router.push('/admin/bans')}
                            className="inline-flex items-center gap-2 bg-[#ff8a00] hover:bg-[#e67e00] active:scale-[0.98] text-white font-bold text-sm px-5 py-2.5 rounded-lg transition-all shadow-sm"
                        >
                            Gestionar Baneos →
                        </button>
                    </div>

                    {/* Resumen de Actividad */}
                    <div className="bg-gray-50 border border-gray-100 rounded-2xl p-6 mt-2">
                        <div className="flex items-center gap-2 mb-4">
                            <BarChart3 className="w-5 h-5 text-[#004a7c]" />
                            <h2 className="text-base font-bold text-gray-800">
                                Resumen de Actividad
                            </h2>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-white rounded-xl border border-gray-100 p-4">
                                <div className="flex items-center gap-2 mb-1">
                                    <span className="w-2 h-2 rounded-full bg-red-500 inline-block" />
                                    <span className="text-xs text-gray-500">Usuarios por Verificar</span>
                                </div>
                                <p className="text-3xl font-extrabold text-gray-900">
                                    {loadingStats ? (
                                        <Loader2 className="w-6 h-6 animate-spin text-gray-300" />
                                    ) : (
                                        stats?.users_pending ?? 0
                                    )}
                                </p>
                            </div>
                            <div className="bg-white rounded-xl border border-gray-100 p-4">
                                <div className="flex items-center gap-2 mb-1">
                                    <span className="w-2 h-2 rounded-full bg-orange-400 inline-block" />
                                    <span className="text-xs text-gray-500">Profesores Pendientes</span>
                                </div>
                                <p className="text-3xl font-extrabold text-gray-900">
                                    {loadingStats ? (
                                        <Loader2 className="w-6 h-6 animate-spin text-gray-300" />
                                    ) : (
                                        stats?.professors_pending ?? 0
                                    )}
                                </p>
                            </div>
                        </div>
                    </div>

                </div>
            </main>

            {/* Footer */}
            <footer className="bg-gray-100 border-t border-gray-200 py-4 px-6">
                <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
                    <p className="text-[11px] font-bold text-gray-400 tracking-widest uppercase">
                        © 2026 Puntualo. Edtech Administration Systems.
                    </p>
                    <nav className="flex gap-4">
                        <a href="#" className="text-[11px] text-gray-400 hover:text-gray-600 transition-colors">Support</a>
                        <a href="#" className="text-[11px] text-gray-400 hover:text-gray-600 transition-colors">Privacy Policy</a>
                        <a href="#" className="text-[11px] text-gray-400 hover:text-gray-600 transition-colors">Terms of Service</a>
                    </nav>
                </div>
            </footer>
        </div>
    );
}

'use client'

import { useEffect, useState } from 'react';
import { Navbar } from "@/components/layout/Navbar";
import Link from "next/link";
import { useRouter } from 'next/navigation';
import { HeroSection } from "@/components/home/HeroSection";
import { FeatureCards } from "@/components/home/FeatureCards";

type UserProfile = {
    full_name: string;
    is_verified: boolean;
};

export default function Home() {
    const [searchQuery, setSearchQuery] = useState('');
    const [user, setUser] = useState<UserProfile | null>(null);
    const [isCheckingSession, setIsCheckingSession] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            setIsCheckingSession(false);
            return;
        }

        const fetchProfile = async () => {
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
                const res = await fetch(`${apiUrl}/auth/me`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });

                if (!res.ok) {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    setUser(null);
                    return;
                }

                const data = await res.json();
                setUser({
                    full_name: data.full_name,
                    is_verified: data.is_verified
                });
            } catch {
                setUser(null);
            } finally {
                setIsCheckingSession(false);
            }
        };

        fetchProfile();
    }, []);

    const canAccessBuscador = () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            router.push('/login');
            return false;
        }
        return true;
    };

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (!canAccessBuscador()) {
            return;
        }
        if (searchQuery.trim() !== '') {
            router.push(`/teachers?query=${encodeURIComponent(searchQuery)}`);
        }
    };

    if (isCheckingSession) {
        return (
            <div className="min-h-screen bg-white font-sans flex flex-col relative overflow-x-hidden selection:bg-sky-100 selection:text-sky-900">
                <Navbar showSearch={false} />
                <main className="flex-1 w-full max-w-[1000px] mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-center relative z-10 pt-20 pb-24">
                    <div className="text-sm font-semibold text-slate-400">Cargando tu inicio...</div>
                </main>
            </div>
        );
    }

    if (user) {
        return (
            <div className="min-h-screen bg-white font-sans flex flex-col relative overflow-x-hidden selection:bg-sky-100 selection:text-sky-900">
                <Navbar showSearch={false} />

                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-5xl h-[520px] flex justify-between pointer-events-none opacity-50 z-0">
                    <div className="w-[420px] h-[420px] bg-[#e0f2fe] rounded-full blur-[110px] -translate-x-1/4 -translate-y-1/4"></div>
                    <div className="w-[420px] h-[420px] bg-[#e0f2fe] rounded-full blur-[110px] translate-x-1/4 -translate-y-1/4"></div>
                </div>

                <main className="flex-1 w-full max-w-[1000px] mx-auto px-4 sm:px-6 lg:px-8 flex flex-col relative z-10 pt-16 pb-24">
                    <section className="flex flex-col gap-6">
                        <div className="flex flex-col gap-2">
                            <span className="text-xs font-bold uppercase tracking-[0.2em] text-slate-400">Inicio de estudiante</span>
                            <h1 className="text-4xl sm:text-5xl font-extrabold text-[#0f172a] tracking-tight">
                                Bienvenido, {user.full_name.split(' ')[0]}.
                            </h1>
                            <p className="text-sm sm:text-base text-[#64748b] max-w-2xl font-medium">
                                Tienes acceso completo al buscador inteligente y las comparativas para elegir al docente ideal.
                            </p>
                        </div>

                        {!user.is_verified && (
                            <div className="rounded-2xl border border-[#fed7aa] bg-[#fff7ed] p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                                <div>
                                    <h2 className="text-sm font-extrabold text-[#9a3412]">Tu cuenta aún no está verificada</h2>
                                    <p className="text-xs text-[#9a3412]/80 mt-1">
                                        Continúa el flujo subiendo tu carnet universitario para activar todas las funciones.
                                    </p>
                                </div>
                                <button
                                    type="button"
                                    onClick={() => router.push('/verify')}
                                    className="px-4 py-2 rounded-full bg-[#ff8a00] hover:bg-[#e67e00] text-white text-xs font-bold transition-colors"
                                >
                                    Prosigue con tu proceso de Verificación
                                </button>
                            </div>
                        )}

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-[0_8px_24px_rgb(0,0,0,0.05)] flex flex-col">
                                <h3 className="text-lg font-extrabold text-[#0f172a] mb-2">Explorar Buscador</h3>
                                <p className="text-sm text-[#64748b] mb-6 flex-1">
                                    Encuentra profesores por materia, facultad o reputación con filtros avanzados.
                                </p>
                                <button
                                    type="button"
                                    onClick={() => router.push('/teachers')}
                                    className="self-start px-5 py-2 rounded-full border-2 border-[#bae6fd] text-[#0284c7] font-bold text-sm hover:bg-[#f0f9ff] transition-colors"
                                >
                                    Ir al Buscador
                                </button>
                            </div>
                            <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-[0_8px_24px_rgb(0,0,0,0.05)] flex flex-col">
                                <h3 className="text-lg font-extrabold text-[#0f172a] mb-2">Comparar docentes</h3>
                                <p className="text-sm text-[#64748b] mb-6 flex-1">
                                    Compara hasta tres perfiles con sus métricas clave en un panel paralelo.
                                </p>
                                <button
                                    type="button"
                                    onClick={() => router.push('/compare')}
                                    className="self-start px-5 py-2 rounded-full border-2 border-[#bae6fd] text-[#0284c7] font-bold text-sm hover:bg-[#f0f9ff] transition-colors"
                                >
                                    Abrir Comparativo
                                </button>
                            </div>
                        </div>
                    </section>
                </main>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-white font-sans flex flex-col relative overflow-x-hidden selection:bg-sky-100 selection:text-sky-900">
            {/* Navbar en modo Landing */}
            <Navbar showSearch={false} />

            {/* Background gradients */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-5xl h-[600px] flex justify-between pointer-events-none opacity-50 z-0">
                <div className="w-[500px] h-[500px] bg-[#e0f2fe] rounded-full blur-[100px] -translate-x-1/4 -translate-y-1/4"></div>
                <div className="w-[500px] h-[500px] bg-[#e0f2fe] rounded-full blur-[100px] translate-x-1/4 -translate-y-1/4"></div>
            </div>

            {/* Contenedor Principal */}
            <main className="flex-1 w-full max-w-[1000px] mx-auto px-4 sm:px-6 lg:px-8 flex flex-col relative z-10 pt-20 pb-24 scale-100">
                <HeroSection 
                    searchQuery={searchQuery} 
                    setSearchQuery={setSearchQuery} 
                    canAccessBuscador={canAccessBuscador} 
                    handleSearch={handleSearch} 
                />

                <FeatureCards canAccessBuscador={canAccessBuscador} />
            </main>

            {/* Footer */}
            <footer className="w-full bg-[#f8fafc] py-8 mt-12 border-t border-gray-100 relative z-10">
                <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
                    <div className="text-lg font-extrabold text-[#0284c7] tracking-tight">
                        Puntualo
                    </div>
                    <div className="flex items-center gap-6 text-[13px] text-[#64748b] font-bold">
                        <Link href="#" className="hover:text-gray-900 transition-colors">Privacidad</Link>
                        <Link href="#" className="hover:text-gray-900 transition-colors">Términos de Uso</Link>
                        <Link href="#" className="hover:text-gray-900 transition-colors">Contacto</Link>
                    </div>
                    <div className="text-[13px] text-[#94a3b8] font-medium">
                        © 2026 Puntualo EdTech. Todos los derechos reservados.
                    </div>
                </div>
            </footer>
        </div>
    );
}

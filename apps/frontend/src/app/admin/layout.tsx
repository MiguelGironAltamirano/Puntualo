'use client'

import { ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { ArrowLeft } from 'lucide-react';

interface AdminLayoutProps {
    children: ReactNode;
}

export default function AdminLayout({ children }: AdminLayoutProps) {
    const router = useRouter();
    const [isAdmin, setIsAdmin] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if user is admin by checking token and role
        // For now, we'll allow access if user has token (proper check should be on backend)
        const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
        if (!token) {
            router.push('/login');
        } else {
            // In production, verify role from token or call /me endpoint
            setIsAdmin(true);
        }
        setLoading(false);
    }, [router]);

    if (loading) {
        return (
            <div className="min-h-screen bg-slate-50 flex items-center justify-center">
                <p className="text-slate-600">Verificando acceso...</p>
            </div>
        );
    }

    if (!isAdmin) {
        return (
            <div className="min-h-screen bg-slate-50 flex items-center justify-center">
                <p className="text-slate-600">No tienes acceso a esta sección</p>
            </div>
        );
    }

    return (
        <div>
            {/* Admin Header */}
            <div className="bg-white border-b border-slate-200">
                <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => router.back()}
                            className="text-slate-400 hover:text-slate-600 transition-colors"
                        >
                            <ArrowLeft className="w-5 h-5" />
                        </button>
                        <h1 className="text-xl font-black text-slate-900">Panel Administrativo</h1>
                    </div>
                    <p className="text-xs text-slate-500 font-medium">Rol: Administrador</p>
                </div>
            </div>

            {/* Content */}
            {children}
        </div>
    );
}

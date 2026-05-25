'use client'

import { useState } from 'react';
import { Navbar } from "@/components/layout/Navbar";
import Link from "next/link";
import { useRouter } from 'next/navigation';
import { HeroSection } from "@/components/home/HeroSection";
import { FeatureCards } from "@/components/home/FeatureCards";

export default function Home() {
    const [searchQuery, setSearchQuery] = useState('');
    const router = useRouter();

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

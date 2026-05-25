'use client'

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { Bell, CircleHelp, Search, User } from "lucide-react";

interface NavbarProps {
  showSearch?: boolean;
  searchQuery?: string;
  setSearchQuery?: (value: string) => void;
}

export function Navbar({ showSearch = true, searchQuery = '', setSearchQuery }: NavbarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [isAuthMenuOpen, setIsAuthMenuOpen] = useState(false);
  const [hasSession] = useState(() => {
    if (typeof window === 'undefined') {
      return false;
    }
    return Boolean(localStorage.getItem('access_token'));
  });

  // Detectamos dinámicamente qué pestaña debe estar activa según la URL
  const isHomeActive = pathname === "/";
  const isBuscadorActive = pathname.startsWith("/teachers");
  const iscompareActive = pathname.startsWith("/compare");

  return (
    <nav className="w-full flex items-center justify-between px-8 py-4 bg-white border-b border-slate-100 z-50 sticky top-0 h-[69px]">
      {/* Left: Logo y Buscador */}
      <div className="flex items-center gap-6 flex-1 max-w-xl">
        <Link href="/" className="text-xl font-extrabold text-[#0284c7] tracking-tight shrink-0 no-underline">
          Puntualo
        </Link>

        {showSearch && (
          <div className="relative flex items-center bg-slate-50 border border-slate-200 rounded-full px-4 py-1.5 w-full max-w-md focus-within:border-sky-400 focus-within:bg-white transition-all">
            <Search className="w-4 h-4 text-slate-400 mr-2 shrink-0" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery?.(e.target.value)}
              placeholder="Buscar por profesor o materia..."
              className="w-full bg-transparent text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none"
            />
          </div>
        )}
      </div>

      {/* Center: Links con detección automática de ruta */}
      <div className="hidden md:flex items-center gap-8 text-sm font-bold absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
        {/* Pestaña Home */}
        <div className="relative group">
          <Link
            href="/"
            className={`transition-colors no-underline ${isHomeActive ? 'text-[#0284c7]' : 'text-gray-400 hover:text-gray-900'}`}
          >
            Home
          </Link>
          {isHomeActive && (
            <div className="absolute -bottom-[23px] left-0 right-0 h-0.5 bg-[#0284c7] rounded-full"></div>
          )}
        </div>

        {/* Pestaña Buscador */}
        <div className="relative group">
          <Link
            href="/teachers"
            onClick={(event) => {
              if (!hasSession) {
                event.preventDefault();
                router.push('/login');
              }
            }}
            className={`transition-colors no-underline ${isBuscadorActive ? 'text-[#0284c7]' : 'text-gray-400 hover:text-gray-900'}`}
          >
            Buscador
          </Link>
          {isBuscadorActive && (
            <div className="absolute -bottom-[23px] left-0 right-0 h-0.5 bg-[#0284c7] rounded-full"></div>
          )}
        </div>

        {/* Pestaña Comparativo */}
        <div className="relative group">
          <Link
            href="/compare"
            className={`transition-colors no-underline ${iscompareActive ? 'text-[#0284c7]' : 'text-gray-400 hover:text-gray-900'}`}
          >
            Comparativo
          </Link>
          {iscompareActive && (
            <div className="absolute -bottom-[23px] left-0 right-0 h-0.5 bg-[#0284c7] rounded-full"></div>
          )}
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-5 z-10">
        <button className="text-gray-400 hover:text-gray-600 transition-colors p-1 relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-[#0284c7] rounded-full"></span>
        </button>
        <button className="text-gray-400 hover:text-gray-600 transition-colors hidden sm:block p-1">
          <CircleHelp className="w-5 h-5" />
        </button>
        <div className="h-5 w-[1px] bg-gray-200 hidden sm:block mx-1"></div>
        <div className="relative">
          <button
            type="button"
            onClick={() => {
              setIsAuthMenuOpen((open) => !open);
            }}
            aria-haspopup="true"
            aria-expanded={isAuthMenuOpen}
            className="w-9 h-9 rounded-full bg-slate-100 border border-slate-300 flex items-center justify-center text-slate-400 hover:text-slate-500 transition-colors"
          >
            <User className="w-4 h-4" />
          </button>
          {!hasSession && isAuthMenuOpen && (
            <div className="absolute right-0 mt-2 w-40 bg-white border border-slate-100 shadow-lg rounded-xl p-2 flex flex-col gap-1">
              <Link
                href="/login"
                className="px-3 py-2 rounded-lg text-xs font-bold text-[#0284c7] hover:bg-[#f0f9ff] transition-colors"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="px-3 py-2 rounded-lg text-xs font-bold text-white bg-[#ff8a00] hover:bg-[#e67e00] transition-colors"
              >
                Register
              </Link>
            </div>
          )}
          {hasSession && isAuthMenuOpen && (
            <div className="absolute right-0 mt-2 w-40 bg-white border border-slate-100 shadow-lg rounded-xl p-2 flex flex-col gap-1">
              <button
                type="button"
                onClick={() => {
                  localStorage.removeItem('access_token');
                  localStorage.removeItem('refresh_token');
                  setIsAuthMenuOpen(false);
                  router.push('/');
                }}
                className="px-3 py-2 rounded-lg text-xs font-bold text-slate-600 hover:bg-slate-50 transition-colors text-left"
              >
                Cerrar sesion
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
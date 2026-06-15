'use client'

import Link from "next/link";
import Image from "next/image";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { Bell, CircleHelp, Search, User, Menu, X } from "lucide-react";

interface NavbarProps {
  showSearch?: boolean;
  searchQuery?: string;
  setSearchQuery?: (value: string) => void;
}

export function Navbar({ showSearch = true, searchQuery = '', setSearchQuery }: NavbarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [isAuthMenuOpen, setIsAuthMenuOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
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
    <nav className="-mx-4 md:-mx-8 lg:-mx-16 w-[calc(100%+2rem)] md:w-[calc(100%+4rem)] lg:w-[calc(100%+8rem)] flex items-center justify-between px-4 md:px-8 lg:px-16 py-4 bg-white border-b border-slate-100 z-50 sticky top-0 h-[69px] relative">
      {/* Left/Center: Logo, Buscador y Links */}
      <div className="flex items-center gap-3 md:gap-6 lg:gap-8 flex-1 min-w-0">
        <Link href="/" className="flex items-center shrink-0 no-underline">
          <Image
            src="/puntualo_logo.png"
            alt="Puntualo"
            width={120}
            height={32}
            priority
            className="h-auto w-24 md:w-36"
            style={{ width: "auto" }}
          />
        </Link>

        {showSearch && (
          <div className="hidden md:flex relative items-center bg-slate-50 border border-slate-200 rounded-full px-4 py-1.5 w-full max-w-[280px] focus-within:border-sky-400 focus-within:bg-white transition-all min-w-0 shrink-0">
            <Search className="w-3.5 h-3.5 text-slate-400 mr-2 shrink-0" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery?.(e.target.value)}
              placeholder="Buscar..."
              className="w-full bg-transparent text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none min-w-0"
            />
          </div>
        )}

        {/* Links con detección automática de ruta */}
        <div className="hidden md:flex items-center gap-6 lg:gap-8 text-sm font-bold shrink-0">
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
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-3 md:gap-5 z-10 shrink-0">
        {/* Desktop-only Actions */}
        <div className="hidden md:flex items-center gap-3 md:gap-5">
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
              <div className="absolute right-0 mt-2 w-40 bg-white border border-slate-100 shadow-lg rounded-xl p-2 flex flex-col gap-1 z-50">
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
              <div className="absolute right-0 mt-2 w-40 bg-white border border-slate-100 shadow-lg rounded-xl p-2 flex flex-col gap-1 z-50">
                <button
                  type="button"
                  onClick={() => {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    setIsAuthMenuOpen(false);
                    router.push('/');
                  }}
                  className="px-3 py-2 rounded-lg text-xs font-bold text-slate-600 hover:bg-slate-50 transition-colors text-left w-full"
                >
                  Cerrar sesion
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Mobile Hamburger Menu Button */}
        <button
          type="button"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="text-slate-400 hover:text-slate-600 transition-colors p-1 md:hidden"
          aria-label="Toggle menu"
        >
          {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu Dropdown */}
      {isMobileMenuOpen && (
        <div className="absolute top-[68px] left-0 w-full bg-white/95 backdrop-blur-md border-b border-slate-100 shadow-lg flex flex-col p-6 gap-4 md:hidden z-40 animate-in slide-in-from-top duration-200">
          
          {/* Mobile-only Search */}
          {showSearch && (
            <div className="relative flex items-center bg-slate-50 border border-slate-200 rounded-full px-4 py-2 w-full focus-within:border-sky-400 focus-within:bg-white transition-all mb-2">
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

          {/* Links */}
          <div className="flex flex-col gap-1">
            <Link
              href="/"
              onClick={() => setIsMobileMenuOpen(false)}
              className={`text-sm font-bold py-2 no-underline transition-colors ${isHomeActive ? 'text-[#0284c7]' : 'text-slate-600 hover:text-slate-900'}`}
            >
              Home
            </Link>
            <Link
              href="/teachers"
              onClick={(event) => {
                setIsMobileMenuOpen(false);
                if (!hasSession) {
                  event.preventDefault();
                  router.push('/login');
                }
              }}
              className={`text-sm font-bold py-2 no-underline transition-colors ${isBuscadorActive ? 'text-[#0284c7]' : 'text-slate-600 hover:text-slate-900'}`}
            >
              Buscador
            </Link>
            <Link
              href="/compare"
              onClick={() => setIsMobileMenuOpen(false)}
              className={`text-sm font-bold py-2 no-underline transition-colors ${iscompareActive ? 'text-[#0284c7]' : 'text-slate-600 hover:text-slate-900'}`}
            >
              Comparativo
            </Link>
          </div>

          {/* Mobile-only Actions: Notifications & User profile links */}
          <div className="flex flex-col gap-2 border-t border-slate-100 pt-4 mt-2">
            <div className="flex items-center justify-between py-2 text-sm font-bold text-slate-600">
              <span className="flex items-center gap-2">
                <Bell className="w-4 h-4 text-slate-400" />
                Notificaciones
              </span>
              <span className="w-2 h-2 bg-[#0284c7] rounded-full"></span>
            </div>

            {!hasSession ? (
              <div className="flex flex-col gap-2 mt-2">
                <Link
                  href="/login"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="px-4 py-2.5 rounded-xl text-xs font-bold text-center text-[#0284c7] bg-[#f0f9ff] hover:bg-[#e0f2fe] transition-colors no-underline"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="px-4 py-2.5 rounded-xl text-xs font-bold text-center text-white bg-[#ff8a00] hover:bg-[#e67e00] transition-colors no-underline"
                >
                  Register
                </Link>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => {
                  localStorage.removeItem('access_token');
                  localStorage.removeItem('refresh_token');
                  setIsMobileMenuOpen(false);
                  router.push('/');
                }}
                className="px-4 py-2.5 rounded-xl text-xs font-bold text-center text-slate-600 bg-slate-50 hover:bg-slate-100 transition-colors mt-2 w-full"
              >
                Cerrar sesión
              </button>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
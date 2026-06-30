'use client'

import Link from "next/link";
import Image from "next/image";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { Bell, Search, User, Menu, X } from "lucide-react";

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
    if (typeof window === 'undefined') return false;
    return Boolean(localStorage.getItem('access_token'));
  });

  const isHomeActive = pathname === "/";
  const isBuscadorActive = pathname.startsWith("/teachers");
  const isCompareActive = pathname.startsWith("/compare");

  const navLinks = [
    { href: '/', label: 'Home', active: isHomeActive, requiresAuth: false },
    { href: '/teachers', label: 'Buscador', active: isBuscadorActive, requiresAuth: true },
    { href: '/compare', label: 'Comparativo', active: isCompareActive, requiresAuth: true },
  ];

  return (
    <nav className="sticky top-0 z-50 w-full bg-white/95 backdrop-blur-sm border-b border-slate-100 h-[72px]">
      <div className="max-w-[1400px] mx-auto px-6 h-full grid grid-cols-[1fr_auto_1fr] items-center gap-4">

        {/* LEFT: Logo + Nav links */}
        <div className="flex items-stretch self-stretch gap-8">
          <div className="flex items-center">
            <Link href="/" className="shrink-0 no-underline">
              <Image
                src="/puntualo_logo.png"
                alt="Puntualo"
                width={110}
                height={30}
                priority
                className="h-9 w-auto"
              />
            </Link>
          </div>

          <div className="hidden md:flex items-stretch gap-0">
            {navLinks.map(({ href, label, active, requiresAuth }) => (
              <div
                key={href}
                className={`flex items-center px-4 border-b-2 transition-colors ${
                  active ? 'border-[#0284c7]' : 'border-transparent'
                }`}
              >
                <Link
                  href={href}
                  onClick={(e) => {
                    if (requiresAuth && !hasSession) {
                      e.preventDefault();
                      router.push('/login');
                    }
                  }}
                  className={`text-sm font-semibold no-underline transition-colors whitespace-nowrap rounded focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:ring-offset-2 ${
                    active ? 'text-[#0284c7]' : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  {label}
                </Link>
              </div>
            ))}
          </div>
        </div>

        {/* CENTER: Search — always occupies space to avoid layout shift */}
        <div className="flex items-center">
          {showSearch ? (
            <div className="relative flex items-center bg-slate-50 border border-slate-200 rounded-full px-4 py-1.5 w-56 lg:w-72 focus-within:border-sky-400 focus-within:bg-white transition-all">
              <Search className="w-3.5 h-3.5 text-slate-400 mr-2 shrink-0" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery?.(e.target.value)}
                placeholder="Buscar por profesor..."
                className="w-full bg-transparent text-xs font-medium text-slate-800 placeholder-slate-500 focus:outline-none"
              />
            </div>
          ) : (
            <div className="w-56 lg:w-72" />
          )}
        </div>

        {/* RIGHT: Actions */}
        <div className="flex items-center justify-end gap-1">
          <div className="hidden md:flex items-center gap-1">
            <button type="button" aria-label="Notificaciones" className="relative p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-50 rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:ring-offset-2">
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-[#0284c7] rounded-full" />
            </button>
            <div className="w-px h-4 bg-slate-200 mx-1" />
            <div className="relative">
              <button
                type="button"
                onClick={() => setIsAuthMenuOpen(o => !o)}
                aria-label="Menú de cuenta"
                aria-expanded={isAuthMenuOpen}
                aria-haspopup="menu"
                className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-500 hover:border-slate-300 hover:bg-slate-200 transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:ring-offset-2"
              >
                <User className="w-3.5 h-3.5" />
              </button>
              {!hasSession && isAuthMenuOpen && (
                <div className="absolute right-0 mt-2 w-36 bg-white border border-slate-100 shadow-lg rounded-xl p-1.5 flex flex-col gap-1 z-50">
                  <Link href="/login" className="px-3 py-2 rounded-lg text-xs font-bold text-[#0284c7] hover:bg-[#f0f9ff] transition-colors no-underline">
                    Login
                  </Link>
                  <Link href="/register" className="px-3 py-2 rounded-lg text-xs font-bold text-white bg-[#c2410c] hover:bg-[#9a3412] transition-colors no-underline block text-center focus:outline-none focus-visible:ring-2 focus-visible:ring-orange-300 focus-visible:ring-offset-2">
                    Register
                  </Link>
                </div>
              )}
              {hasSession && isAuthMenuOpen && (
                <div className="absolute right-0 mt-2 w-36 bg-white border border-slate-100 shadow-lg rounded-xl p-1.5 z-50">
                  <button
                    type="button"
                    onClick={() => {
                      localStorage.removeItem('access_token');
                      localStorage.removeItem('refresh_token');
                      window.location.replace('/');
                    }}
                    className="w-full px-3 py-2 rounded-lg text-xs font-bold text-slate-600 hover:bg-slate-50 transition-colors text-left"
                  >
                    Cerrar sesión
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Mobile hamburger */}
          <button
            type="button"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label={isMobileMenuOpen ? "Cerrar menú" : "Abrir menú"}
            aria-expanded={isMobileMenuOpen}
            className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-50 rounded-lg transition-colors md:hidden focus:outline-none focus-visible:ring-2 focus-visible:ring-sky-400 focus-visible:ring-offset-2"
          >
            {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile dropdown */}
      {isMobileMenuOpen && (
        <div className="absolute top-[72px] left-0 w-full bg-white border-b border-slate-100 shadow-lg flex flex-col p-5 gap-4 md:hidden z-40">
          {showSearch && (
            <div className="relative flex items-center bg-slate-50 border border-slate-200 rounded-full px-4 py-2 focus-within:border-sky-400 focus-within:bg-white transition-all">
              <Search className="w-3.5 h-3.5 text-slate-400 mr-2 shrink-0" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery?.(e.target.value)}
                placeholder="Buscar por profesor..."
                className="w-full bg-transparent text-xs font-medium text-slate-800 placeholder-slate-500 focus:outline-none"
              />
            </div>
          )}

          <div className="flex flex-col">
            {navLinks.map(({ href, label, active, requiresAuth }) => (
              <Link
                key={href}
                href={href}
                onClick={(e) => {
                  setIsMobileMenuOpen(false);
                  if (requiresAuth && !hasSession) {
                    e.preventDefault();
                    router.push('/login');
                  }
                }}
                className={`text-sm font-semibold py-2.5 border-b border-slate-50 last:border-0 no-underline transition-colors ${
                  active ? 'text-[#0284c7]' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {label}
              </Link>
            ))}
          </div>

          <div className="border-t border-slate-100 pt-3 flex flex-col gap-2">
            {!hasSession ? (
              <>
                <Link href="/login" onClick={() => setIsMobileMenuOpen(false)} className="px-4 py-2.5 rounded-xl text-xs font-bold text-center text-[#0284c7] bg-[#f0f9ff] no-underline">
                  Login
                </Link>
                <Link href="/register" onClick={() => setIsMobileMenuOpen(false)} className="px-4 py-2.5 rounded-xl text-xs font-bold text-center text-white bg-[#c2410c] hover:bg-[#9a3412] no-underline focus:outline-none focus-visible:ring-2 focus-visible:ring-orange-300 focus-visible:ring-offset-2">
                  Register
                </Link>
              </>
            ) : (
              <button
                type="button"
                onClick={() => {
                  localStorage.removeItem('access_token');
                  localStorage.removeItem('refresh_token');
                  window.location.replace('/');
                }}
                className="px-4 py-2.5 rounded-xl text-xs font-bold text-slate-600 bg-slate-50 w-full"
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

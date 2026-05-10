import Link from "next/link";
import { Bell, CircleHelp, User } from "lucide-react";

export function Navbar() {
  return (
    <nav className="w-full flex items-center justify-between px-6 py-4 bg-white z-50">
      {/* Left: Logo */}
      <div className="flex items-center">
        <Link href="/" className="text-xl font-extrabold text-[#0369a1] tracking-tight">
          Puntualo
        </Link>
      </div>

      {/* Center: Links */}
      <div className="hidden md:flex items-center gap-8 text-sm font-bold">
        <div className="relative group">
          <Link href="/" className="text-[#0369a1]">
            Home
          </Link>
          <div className="absolute -bottom-1.5 left-0 right-0 h-0.5 bg-[#0369a1] rounded-full"></div>
        </div>
        <Link href="/buscador" className="text-gray-500 hover:text-gray-900 transition-colors">
          Buscador
        </Link>
        <Link href="/comparar" className="text-gray-500 hover:text-gray-900 transition-colors">
          Comparativo
        </Link>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-4">
        <button className="text-gray-400 hover:text-gray-600 transition-colors">
          <Bell className="w-5 h-5" />
        </button>
        <button className="text-gray-400 hover:text-gray-600 transition-colors hidden sm:block">
          <CircleHelp className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-4 ml-2 pl-4">
          <Link 
            href="/login" 
            className="text-sm font-semibold text-gray-600 hover:text-gray-900 transition-colors"
          >
            Iniciar sesión
          </Link>
          <Link 
            href="/register" 
            className="text-sm font-semibold bg-[#f97316] text-white px-5 py-2.5 rounded-full hover:bg-[#ea580c] transition-colors"
          >
            Regístrate
          </Link>
        </div>
      </div>
    </nav>
  );
}

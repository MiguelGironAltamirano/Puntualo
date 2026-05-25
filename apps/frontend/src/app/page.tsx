'use client'

import { useState } from 'react';
import { Navbar } from "@/components/layout/Navbar";
import { Search, Lightbulb, Filter, MapPin, AlignRight } from "lucide-react";
import Link from "next/link";
import { useRouter } from 'next/navigation';

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
      // Redirige al buscador pasando el parámetro en la URL
      router.push(`/teachers?query=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <div className="min-h-screen bg-white font-sans flex flex-col relative overflow-x-hidden selection:bg-sky-100 selection:text-sky-900">
      {/* Navbar en modo Landing (sin la barra pequeña arriba) */}
      <Navbar showSearch={false} />

      {/* Background gradients */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-5xl h-[600px] flex justify-between pointer-events-none opacity-50 z-0">
        <div className="w-[500px] h-[500px] bg-[#e0f2fe] rounded-full blur-[100px] -translate-x-1/4 -translate-y-1/4"></div>
        <div className="w-[500px] h-[500px] bg-[#e0f2fe] rounded-full blur-[100px] translate-x-1/4 -translate-y-1/4"></div>
      </div>

      {/* Contenedor Principal */}
      <main className="flex-1 w-full max-w-[1000px] mx-auto px-4 sm:px-6 lg:px-8 flex flex-col relative z-10 pt-20 pb-24 scale-100">

        {/* Hero Section */}
        <section className="flex flex-col items-center text-center mt-4 mb-24">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#f1f5f9] text-[#475569] text-xs font-semibold mb-8">
            <span className="text-[#0284c7]">✨</span> Búsqueda potenciada por Inteligencia Artificial
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-[3.5rem] font-extrabold text-[#0f172a] tracking-tight max-w-3xl leading-tight mb-6">
            Elige al docente <span className="text-[#0284c7]">ideal</span> para tu semestre.
          </h1>

          <p className="text-lg text-[#64748b] max-w-2xl mb-10 leading-relaxed font-medium">
            Decisiones académicas respaldadas por datos. Encuentra perfiles detallados, comparativas estructuradas y el consenso real de los estudiantes.
          </p>

          {/* Formulario de Búsqueda Grande con Input Súper Nítido */}
          <form onSubmit={handleSearch} className="w-full max-w-3xl relative">
            <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" strokeWidth={2.5} />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              spellCheck={false}
              className="w-full h-16 pl-14 pr-32 rounded-full border border-gray-200 bg-white shadow-[0_8px_30px_rgb(0,0,0,0.06)] text-base font-bold text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-100 focus:border-sky-300 transition-all placeholder:text-gray-400 block"
              placeholder="Busca por docente, materia o facultad..."
            />
            <button type="submit" className="absolute right-2 top-2 bottom-2 px-8 bg-[#ff8a00] hover:bg-[#ea580c] text-white font-bold text-sm rounded-full transition-colors">
              Buscar
            </button>
          </form>

          {/* Tags sugeridos interactivos */}
          <div className="flex flex-wrap justify-center gap-3 mt-6">
            {["Cálculo Avanzado", "Ingeniería", "Alta Claridad"].map((tag) => (
              <button
                key={tag}
                type="button"
                onClick={() => {
                  if (canAccessBuscador()) {
                    router.push(`/teachers?query=${encodeURIComponent(tag)}`);
                  }
                }}
                className="px-4 py-1.5 bg-[#f8fafc] border border-gray-200 rounded-full text-xs font-bold text-[#64748b] shadow-sm hover:border-gray-300 cursor-pointer transition-colors"
              >
                {tag}
              </button>
            ))}
          </div>
        </section>

        {/* Features Section */}
        <section className="flex flex-col items-center mt-12 w-full">
          <h2 className="text-xl font-extrabold text-[#0f172a] mb-2">¿Por qué usar Puntualo?</h2>
          <p className="text-[#64748b] text-sm font-medium mb-12 text-center max-w-2xl">
            Nuestra plataforma transforma la incertidumbre en confianza académica.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full mb-6">
            {/* Card 1 */}
            <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-[0_4px_20px_rgb(0,0,0,0.03)] hover:shadow-md transition-shadow">
              <div className="w-10 h-10 bg-[#e0f2fe] rounded-xl flex items-center justify-center mb-6">
                <Lightbulb className="w-5 h-5 text-[#0284c7]" strokeWidth={2.5} />
              </div>
              <h3 className="text-lg font-extrabold text-[#0f172a] mb-3">Síntesis IA</h3>
              <p className="text-[#64748b] mb-8 leading-relaxed text-sm font-medium">
                No pierdas tiempo leyendo cientos de comentarios. Nuestro motor procesa todas las evaluaciones para darte un resumen ejecutivo sobre la metodología, exigencia y trato de cada profesor.
              </p>

              <div className="bg-[#f0f9ff] rounded-xl p-5 border border-blue-50 relative overflow-hidden">
                <div className="flex gap-3 relative z-10">
                  <div className="mt-0.5">
                    <MapPin className="w-4 h-4 text-[#0284c7]" strokeWidth={2.5} />
                  </div>
                  <p className="text-[13px] text-[#0c4a6e] leading-relaxed font-medium">
                    <span className="font-extrabold">Consenso general:</span> Destaca por su claridad al explicar conceptos complejos, aunque sus parciales son conocidos por su alta dificultad.
                  </p>
                </div>
              </div>
            </div>

            {/* Card 2 */}
            <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-[0_4px_20px_rgb(0,0,0,0.03)] hover:shadow-md transition-shadow flex flex-col">
              <div className="w-10 h-10 bg-[#f1f5f9] rounded-xl flex items-center justify-center mb-6">
                <AlignRight className="w-5 h-5 text-[#475569] transform -rotate-90" strokeWidth={2.5} />
              </div>
              <h3 className="text-lg font-extrabold text-[#0f172a] mb-3">Comparativa</h3>
              <p className="text-[#64748b] mb-10 leading-relaxed text-sm font-medium flex-1">
                Alinea hasta tres perfiles docentes lado a lado. Compara sus métricas de claridad, dificultad y accesibilidad en un layout paralelo perfecto.
              </p>

              <div className="flex gap-2 mt-auto pb-4">
                <div className="h-2 bg-[#ff8a00] w-[40%] rounded-full"></div>
                <div className="h-2 bg-[#0ea5e9] w-[35%] rounded-full"></div>
                <div className="h-2 bg-[#cbd5e1] w-[25%] rounded-full"></div>
              </div>
            </div>
          </div>

          {/* Full Width Card */}
          <div className="bg-white w-full rounded-2xl p-8 border border-gray-100 shadow-[0_4px_20px_rgb(0,0,0,0.03)] hover:shadow-md transition-shadow flex flex-col md:flex-row md:items-center justify-between gap-8">
            <div className="flex items-start md:items-center gap-6">
              <div className="w-10 h-10 bg-[#f1f5f9] rounded-xl flex items-center justify-center flex-shrink-0">
                <Filter className="w-5 h-5 text-[#64748b]" strokeWidth={2.5} />
              </div>
              <div>
                <h3 className="text-lg font-extrabold text-[#0f172a] mb-1.5">Filtros Quirúrgicos</h3>
                <p className="text-[#64748b] text-sm leading-relaxed max-w-2xl font-medium">
                  Refina tu búsqueda a un nivel granular. Filtra no solo por departamento o facultad, sino por metodologías de evaluación, tolerancia a inasistencias o carga de lectura.
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => {
                if (canAccessBuscador()) {
                  router.push('/teachers');
                }
              }}
              className="px-6 py-2.5 rounded-full border-2 border-[#bae6fd] text-[#0284c7] font-bold hover:bg-[#f0f9ff] transition-colors whitespace-nowrap text-sm text-center"
            >
              Explorar Buscador
            </button>
          </div>
        </section>
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


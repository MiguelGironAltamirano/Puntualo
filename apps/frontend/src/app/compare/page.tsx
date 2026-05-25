'use client'

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Navbar } from '@/components/layout/Navbar';
import { Search, Plus, X, RotateCcw } from 'lucide-react';
import { Teacher } from '@/components/compare/types';
import { IASummary } from '@/components/compare/IASummary';
import { CompareMetrics } from '@/components/compare/CompareMetrics';
import { StudentReviews } from '@/components/compare/StudentReviews';

// Reducido a exactamente 2 opciones de prueba para validar la UI
const MOCK_TEACHERS: Teacher[] = [
    {
        id: '1',
        name: 'GUSTAVO DE LA CRUZ CASA',
        course: 'INTERACCIÓN HOMBRE-COMPUTADORA',
        school: 'Ingeniería de Software',
        rating: 4.5,
        difficulty: 3.5,
        clarity: 4.6,
        takeAgain: '92%',
        avatar: '/avatar1.jpg',
        tags: ['Buena gente', 'Clases claras', 'Exigente'],
        reviews: [
            { text: "Su metodología es muy práctica, pero espera que leas antes de clase. Las diapositivas ayudan bastante.", course: "Interacción Hombre-Computadora", date: "Hace 1 mes" },
            { text: "Los exámenes son un poco largos, pero califica justo y el proyecto final aporta mucho al portafolio.", course: "Interacción Hombre-Computadora", date: "Hace 3 meses" }
        ],
        aiSummary: {
            pros: ['Metodología práctica', 'Material de apoyo útil', 'Calificación justa'],
            contras: ['Exámenes largos', 'Requiere lectura previa']
        }
    },
    {
        id: '2',
        name: 'MANUEL CARPIO',
        course: 'INTERACCIÓN HOMBRE-COMPUTADORA',
        school: 'Ingeniería de Software',
        rating: 4.9,
        difficulty: 4.0,
        clarity: 5.0,
        takeAgain: '75%',
        avatar: '/avatar2.jpg',
        tags: ['Exigente', 'Mucho trabajo', 'Teórico'],
        reviews: [
            { text: "Explica a detalle cada tema, pero deja bastantes tareas por semana. Hay que ser organizado.", course: "Interacción Hombre-Computadora", date: "Hace 2 meses" },
            { text: "La teoría es densa y muy técnica. Hay que tomar apuntes rápido si quieres aprobar los parciales.", course: "Interacción Hombre-Computadora", date: "Hace 5 meses" }
        ],
        aiSummary: {
            pros: ['Explicaciones detalladas', 'Buen dominio del tema'],
            contras: ['Mucha carga de tareas', 'Teoría densa', 'Requiere organización']
        }
    },
];

export default function ComparePage() {
    const router = useRouter();
    const [slotA, setSlotA] = useState<Teacher | null>(null);
    const [slotB, setSlotB] = useState<Teacher | null>(null);
    const [searchA, setSearchA] = useState('');
    const [searchB, setSearchB] = useState('');

    const filteredTeachersA = MOCK_TEACHERS.filter(t => t.name.toLowerCase().includes(searchA.toLowerCase()) && t.id !== slotB?.id);
    const filteredTeachersB = MOCK_TEACHERS.filter(t => t.name.toLowerCase().includes(searchB.toLowerCase()) && t.id !== slotA?.id);

    return (
        <div className="min-h-screen bg-white font-sans text-slate-900">
            <Navbar />

            <div className="mx-auto max-w-[1400px] px-8 py-8">

                {/* Cabecera estilo Versus */}
                <div className="mb-10 relative">
                    <h1 className="text-4xl font-black text-[#0284c7] tracking-tight">Versus</h1>
                    <p className="text-sm text-slate-500 mt-1 font-medium">
                        Comparando docentes en paralelo. Contrasta sus métricas y opiniones.
                    </p>
                    {(slotA || slotB) && (
                        <button
                            onClick={() => { setSlotA(null); setSlotB(null); }}
                            className="absolute right-0 top-1/2 -translate-y-1/2 flex items-center gap-2 px-4 py-2 border border-slate-200 bg-white hover:bg-slate-50 rounded-xl text-sm font-bold text-slate-700 transition-colors shadow-sm"
                        >
                            <RotateCcw className="w-4 h-4 text-slate-400" />
                            Limpiar Comparación
                        </button>
                    )}
                </div>

                {/* ESTRUCTURA DE 2 COLUMNAS PRINCIPALES */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-12">

                    {/* ================= COLUMNA DOCENTE A ================= */}
                    <div className="relative">
                        {!slotA ? (
                            <div className="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm">
                                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Seleccionar Primer Docente</h3>
                                <div className="relative">
                                    <Search className="absolute left-4 top-3.5 text-slate-400" size={18} />
                                    <input
                                        type="text"
                                        placeholder="Escribe el nombre del profesor..."
                                        value={searchA}
                                        onChange={(e) => setSearchA(e.target.value)}
                                        className="w-full pl-11 pr-4 py-3 bg-white border border-slate-200 rounded-2xl text-sm text-slate-900 font-medium placeholder-slate-400 focus:outline-none focus:border-sky-500 transition-all shadow-sm"
                                    />
                                    {searchA && (
                                        <div className="absolute left-0 right-0 top-full mt-2 z-50 bg-white border border-slate-200 rounded-2xl shadow-xl max-h-60 overflow-y-auto p-2">
                                            {filteredTeachersA.length > 0 ? (
                                                filteredTeachersA.map(t => (
                                                    <div
                                                        key={t.id}
                                                        onClick={() => { setSlotA(t); setSearchA(''); }}
                                                        className="p-3 hover:bg-sky-50 rounded-xl cursor-pointer text-sm font-bold text-slate-800 transition-all"
                                                    >
                                                        {t.name}
                                                        <span className="block text-xs font-semibold text-slate-400 mt-0.5">{t.course}</span>
                                                    </div>
                                                ))
                                            ) : (
                                                <div className="p-3 text-xs font-bold text-slate-400 text-center">No se encontraron docentes</div>
                                            )}
                                        </div>
                                    )}
                                </div>
                                <div className="h-48 border-2 border-dashed border-slate-200 rounded-2xl flex flex-col items-center justify-center text-slate-400 text-sm mt-4 bg-slate-50/50">
                                    <Plus size={24} className="mb-2 text-slate-300" /> Usa el buscador
                                </div>
                            </div>
                        ) : (
                            /* Perfil de Docente A en la parte superior */
                            <div className="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm relative">
                                <button onClick={() => setSlotA(null)} className="absolute right-4 top-4 p-1.5 bg-slate-50 hover:bg-red-50 hover:text-red-500 rounded-xl transition-all">
                                    <X size={16} />
                                </button>
                                <div className="flex flex-col items-center text-center py-4">
                                    {slotA.avatar ? (
                                        <Image src={slotA.avatar} alt={slotA.name} width={64} height={64} className="w-16 h-16 rounded-full object-cover border border-slate-200 shadow-sm mb-3" />
                                    ) : (
                                        <div className="w-16 h-16 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-xl mb-3">👨‍🏫</div>
                                    )}
                                    <h2 className="text-lg font-black text-slate-900 leading-tight">{slotA.name}</h2>
                                    <p className="text-xs font-bold text-slate-400 mt-1">{slotA.school}</p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* ================= COLUMNA DOCENTE B ================= */}
                    <div className="relative">
                        {!slotB ? (
                            <div className="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm">
                                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Seleccionar Segundo Docente</h3>
                                <div className="relative">
                                    <Search className="absolute left-4 top-3.5 text-slate-400" size={18} />
                                    <input
                                        type="text"
                                        placeholder="Escribe el nombre del profesor..."
                                        value={searchB}
                                        onChange={(e) => setSearchB(e.target.value)}
                                        className="w-full pl-11 pr-4 py-3 bg-white border border-slate-200 rounded-2xl text-sm text-slate-900 font-medium placeholder-slate-400 focus:outline-none focus:border-sky-500 transition-all shadow-sm"
                                    />
                                    {searchB && (
                                        <div className="absolute left-0 right-0 top-full mt-2 z-50 bg-white border border-slate-200 rounded-2xl shadow-xl max-h-60 overflow-y-auto p-2">
                                            {filteredTeachersB.length > 0 ? (
                                                filteredTeachersB.map(t => (
                                                    <div
                                                        key={t.id}
                                                        onClick={() => { setSlotB(t); setSearchB(''); }}
                                                        className="p-3 hover:bg-sky-50 rounded-xl cursor-pointer text-sm font-bold text-slate-800 transition-all"
                                                    >
                                                        {t.name}
                                                        <span className="block text-xs font-semibold text-slate-400 mt-0.5">{t.course}</span>
                                                    </div>
                                                ))
                                            ) : (
                                                <div className="p-3 text-xs font-bold text-slate-400 text-center">No se encontraron docentes</div>
                                            )}
                                        </div>
                                    )}
                                </div>
                                <div className="h-48 border-2 border-dashed border-slate-200 rounded-2xl flex flex-col items-center justify-center text-slate-400 text-sm mt-4 bg-slate-50/50">
                                    <Plus size={24} className="mb-2 text-slate-300" /> Usa el buscador
                                </div>
                            </div>
                        ) : (
                            /* Perfil de Docente B en la parte superior */
                            <div className="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm relative">
                                <button onClick={() => setSlotB(null)} className="absolute right-4 top-4 p-1.5 bg-slate-50 hover:bg-red-50 hover:text-red-500 rounded-xl transition-all">
                                    <X size={16} />
                                </button>
                                <div className="flex flex-col items-center text-center py-4">
                                    {slotB.avatar ? (
                                        <Image src={slotB.avatar} alt={slotB.name} width={64} height={64} className="w-16 h-16 rounded-full object-cover border border-slate-200 shadow-sm mb-3" />
                                    ) : (
                                        <div className="w-16 h-16 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-xl mb-3">👩‍🏫</div>
                                    )}
                                    <h2 className="text-lg font-black text-slate-900 leading-tight">{slotB.name}</h2>
                                    <p className="text-xs font-bold text-slate-400 mt-1">{slotB.school}</p>
                                </div>
                            </div>
                        )}
                    </div>

                </div>

                {/* ================= SECCIÓN: RESUMEN IA Y COMPARATIVA DE MÉTRICAS ================= */}
                {(slotA || slotB) && (
                    <>
                        <IASummary slotA={slotA} slotB={slotB} />
                        <CompareMetrics slotA={slotA} slotB={slotB} />
                        <StudentReviews slotA={slotA} slotB={slotB} />
                    </>
                )}

            </div>
        </div>
    );
}
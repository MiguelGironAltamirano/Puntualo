'use client'

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Navbar } from "@/components/layout/Navbar";
import { CommentList } from "@/components/teachers/CommentList";
import { EvaluarModal } from "@/components/teachers/EvaluarModal";
import { ArrowLeft, Bookmark, ClipboardList, GraduationCap, MessageSquare, X } from "lucide-react";
import { TeacherData } from "@/components/teachers/types";

const TEACHERS_DATA: Record<string, TeacherData> = {
    "1": {
        name: 'Dra. Elena Navarro',
        rating: '4.8 / 5.0',
        faculty: 'Facultad de Ciencias Exactas y Naturales',
        department: 'Departamento de Matemáticas',
        avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80',
        aiSummary: {
            pros: ['Excepcional claridad explicativa', 'Provee excelente material de estudio', 'Accesible en consulta'],
            contras: ['Exámenes considerados rigurosos']
        },
        education: 'Doctorado en Matemáticas',
        university: 'Universidad Nacional Autónoma',
        research: ['Cálculo Avanzado', 'Topología', 'Álgebra Computacional'],
        experience: '15+ Años de trayectoria docente en nivel superior.',
        metrics: { claridad: 4.9, facilidad: 3.2, ayuda: 4.7, total: 142 },
        style: ['Mucha tarea práctica', 'Uso intensivo de pizarra', 'Asistencia obligatoria'],
        comments: [
            {
                id: 1,
                course: 'Cálculo Diferencial',
                semester: 'Semestre 2023-1',
                mode: 'Modalidad Presencial',
                score: '5.0',
                verified: true,
                text: 'Es de las mejores profesoras que he tenido en la facultad. Explica desde cero y tiene muchísima paciencia si vas a sus horas de consulta. Los exámenes son largos pero si haces las guías de ejercicios, no hay sorpresas. Totalmente recomendada si quieres aprender de verdad.',
                tags: ['#ExplicaBien', '#DaRetroalimentación'],
                reactions: { heart: 12, fire: 8, lightbulb: 3, droplet: 15, chart: 5, likes: 24, dislikes: 2 }
            },
            {
                id: 2,
                course: 'Álgebra Lineal',
                semester: 'Semestre 2022-2',
                mode: 'Modalidad Virtual',
                score: '4.0',
                verified: true,
                text: 'En modalidad virtual se adaptó bastante bien, usaba una tableta gráfica que hacía las clases muy fluidas. La carga de trabajo es pesada y a veces califica duro, pero siempre es justa. No es una materia de "relleno" con ella.',
                tags: ['#MuchaTarea', '#Justa'],
                reactions: { heart: 6, fire: 4, lightbulb: 10, droplet: 2, chart: 1, likes: 18, dislikes: 4 }
            },
            {
                id: 3,
                course: 'Cálculo Integral',
                semester: 'Semestre 2023-2',
                mode: 'Modalidad Presencial',
                score: '4.5',
                verified: false,
                text: 'Excelente dominio del tema. Me ayudó mucho que subiera apuntes adicionales al campus virtual. El único detalle es que a veces va un poco rápido si nadie hace preguntas, así que no duden en detenerla si no entienden algo.',
                tags: ['#MaterialDeApoyo'],
                reactions: { heart: 20, fire: 14, lightbulb: 0, droplet: 25, chart: 12, likes: 32, dislikes: 1 }
            }
        ]
    }
};

export default function TeacherProfilePage() {
    const params = useParams();
    const router = useRouter();
    const id = params?.id as string;
    const teacher = TEACHERS_DATA[id] || TEACHERS_DATA["1"];

    // Estados para controlar el Modal de Formulario
    const [isModalOpen, setIsModalOpen] = useState(false);

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans text-left selection:bg-sky-100 selection:text-sky-900 relative">
            <Navbar showSearch={false} />

            <main className="flex-1 w-full max-w-[1000px] mx-auto px-4 py-8 space-y-6 bg-white">

                {/* BOTÓN VOLVER */}
                <button
                    onClick={() => router.push('/teachers')}
                    className="flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-slate-800 transition-colors mb-2 focus:outline-none cursor-pointer"
                >
                    <ArrowLeft className="w-4 h-4" /> Volver a Resultados
                </button>

                {/* HEADER PRINCIPAL */}
                <div className="bg-white border border-slate-100 rounded-2xl p-6 flex flex-col sm:flex-row items-center justify-between gap-6 shadow-sm">
                    <div className="flex flex-col sm:flex-row items-center gap-5 text-center sm:text-left">
                        <div className="w-16 h-16 rounded-full overflow-hidden bg-slate-100 border border-slate-200 shrink-0">
                            <img src={teacher.avatar} alt={teacher.name} className="w-full h-full object-cover object-top" />
                        </div>
                        <div className="space-y-1">
                            <div className="flex flex-col sm:flex-row sm:items-center gap-3 justify-center sm:justify-start">
                                <h1 className="text-xl font-black text-slate-900 tracking-tight">{teacher.name}</h1>
                                <span className="bg-[#ff8a00] text-white text-[10px] font-black px-2 py-0.5 rounded-md shadow-sm">
                                    {teacher.rating}
                                </span>
                            </div>
                            <p className="text-xs font-semibold text-slate-500 flex flex-wrap items-center justify-center sm:justify-start gap-1">
                                <ClipboardList className="w-3.5 h-3.5 text-slate-400" /> {teacher.faculty} • {teacher.department}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0 w-full sm:w-auto justify-center">
                        <button className="px-4 py-2 border border-slate-200 hover:bg-slate-50 text-slate-600 text-xs font-bold rounded-xl transition-colors cursor-pointer">
                            <Bookmark className="w-3.5 h-3.5 text-slate-400" /> Guardar
                        </button>
                        <button
                            onClick={() => setIsModalOpen(true)}
                            className="px-4 py-2 bg-[#ff8a00] hover:bg-[#ea580c] text-white text-xs font-black rounded-xl flex items-center gap-1.5 transition-colors shadow-sm cursor-pointer"
                        >
                            <MessageSquare className="w-3.5 h-3.5" /> Evaluar
                        </button>
                    </div>
                </div>

                {/* SÍNTESIS DE IA */}
                <div className="bg-[#e0f2fe]/40 border border-sky-100 rounded-2xl p-6 shadow-sm">
                    <div className="flex gap-4 items-start">
                        <div className="w-9 h-9 bg-white rounded-xl flex items-center justify-center text-sky-600 shadow-sm border border-sky-100 shrink-0 text-base">🧠</div>
                        <div className="space-y-1">
                            <div className="flex items-center gap-2">
                                <h3 className="text-xs font-black text-sky-950 tracking-wider uppercase">Síntesis de IA</h3>
                                <span className="bg-sky-500/10 text-sky-700 text-[8px] font-black px-1.5 py-0.5 rounded-md tracking-widest">Beta</span>
                            </div>
                            <div className="text-xs text-slate-600 font-medium leading-relaxed space-y-2">
                                <p><span className="font-bold text-sky-800">Pros:</span> {teacher.aiSummary.pros.join(', ')}</p>
                                <p><span className="font-bold text-sky-800">Contras:</span> {teacher.aiSummary.contras.join(', ')}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* HOJA DE VIDA */}
                <div className="bg-white border border-slate-100 rounded-2xl p-6 text-xs font-medium shadow-sm">
                    <div className="flex items-center gap-2 mb-5">
                        <GraduationCap className="w-4 h-4 text-[#0284c7]" />
                        <h3 className="text-xs font-black text-slate-900 tracking-wider uppercase">Hoja de Vida</h3>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-slate-600">
                        <div>
                            <span className="text-[9px] font-bold text-slate-400 uppercase block tracking-wider">Educación</span>
                            <p className="font-bold text-slate-800">{teacher.education}</p>
                            <p className="text-[11px] text-slate-400">{teacher.university}</p>
                        </div>
                        <div>
                            <span className="text-[9px] font-bold text-slate-400 uppercase block tracking-wider">Áreas de Investigación</span>
                            <div className="flex flex-wrap gap-1.5 mt-1">
                                {teacher.research.map((item: string) => (
                                    <span key={item} className="px-2 py-0.5 bg-slate-50 border border-slate-200 text-slate-500 font-bold text-[9px] rounded-md">{item}</span>
                                ))}
                            </div>
                        </div>
                        <div>
                            <span className="text-[9px] font-bold text-slate-400 uppercase block tracking-wider">Experiencia</span>
                            <p className="font-bold text-slate-800">{teacher.experience}</p>
                        </div>
                    </div>
                </div>

                {/* SECCIÓN INFERIOR COMPUESTA */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">

                    {/* Bloque Izquierdo: Métricas */}
                    <div className="space-y-4">
                        <div className="bg-white border border-slate-100 rounded-2xl p-5 space-y-4 shadow-sm">
                            <h4 className="text-xs font-black text-slate-900 uppercase tracking-wider">Métricas Promedio</h4>
                            <div className="space-y-3">
                                <div>
                                    <div className="flex justify-between text-[10px] font-bold text-slate-400 mb-1"><span>Claridad</span> <span className="text-slate-700 font-black">{teacher.metrics.claridad}</span></div>
                                    <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                                        <div className="bg-[#ff8a00] h-full" style={{ width: `${(teacher.metrics.claridad / 5) * 100}%` }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-[10px] font-bold text-slate-400 mb-1"><span>Facilidad</span> <span className="text-slate-700 font-black">{teacher.metrics.facilidad}</span></div>
                                    <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                                        <div className="bg-[#ff8a00] h-full" style={{ width: `${(teacher.metrics.facilidad / 5) * 100}%` }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-[10px] font-bold text-slate-400 mb-1"><span>Ayuda</span> <span className="text-slate-700 font-black">{teacher.metrics.ayuda}</span></div>
                                    <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                                        <div className="bg-[#ff8a00] h-full" style={{ width: `${(teacher.metrics.ayuda / 5) * 100}%` }}></div>
                                    </div>
                                </div>
                            </div>
                            <p className="text-[10px] font-medium text-slate-400 pt-1 text-center">ℹ Basado en {teacher.metrics.total} evaluaciones</p>
                        </div>

                        <div className="bg-sky-50/40 border border-sky-100/60 rounded-2xl p-5">
                            <h4 className="text-[10px] font-black text-[#0284c7] uppercase tracking-wider mb-3">Estilo de Enseñanza</h4>
                            <ul className="space-y-1.5 text-xs font-semibold text-slate-600">
                                {teacher.style.map((item: string) => <li key={item} className="flex items-center gap-2"><span className="text-sky-500">✓</span> {item}</li>)}
                            </ul>
                        </div>
                    </div>

                    {/* Bloque Derecho Inyectado de forma limpia usando tu nuevo componente */}
                    <CommentList comments={teacher.comments} />

                </div>
            </main>

            {/* POP-UP MODAL EXTRACTED */}
            <EvaluarModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} teacher={teacher} />

        </div>
    );
}
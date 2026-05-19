'use client'

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Navbar } from "@/components/layout/Navbar";
import { ListaComentarios } from "./ListaComentarios";
import { ArrowLeft, Bookmark, ClipboardList, GraduationCap, MessageSquare, X } from "lucide-react";

const PROFESORES_DATA: Record<string, any> = {
    "1": {
        name: 'Dra. Elena Navarro',
        rating: '4.8 / 5.0',
        faculty: 'Facultad de Ciencias Exactas y Naturales',
        department: 'Departamento de Matemáticas',
        avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80',
        aiSummary: 'Los estudiantes destacan a la Dra. Navarro por su excepcional claridad explicativa en temas complejos de cálculo. Aunque sus exámenes son considerados rigurosos, la mayoría coincide en que provee el material y la disposición necesaria para aprobar si se asiste regularmente. Se valora especialmente su accesibilidad durante las horas de consulta presenciales.',
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
                likes: 24,
                dislikes: 2,
                reactions: [
                    { icon: '❤️', count: 12 },
                    { icon: '🔥', count: 8 },
                    { icon: '💡', count: 3 },
                    { icon: '💧', count: 15 },
                    { icon: '📈', count: 5 }
                ]
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
                likes: 18,
                dislikes: 4,
                reactions: [
                    { icon: '❤️', count: 6 },
                    { icon: '🔥', count: 4 },
                    { icon: '💡', count: 10 },
                    { icon: '💧', count: 2 },
                    { icon: '📈', count: 1 }
                ]
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
                likes: 32,
                dislikes: 1,
                reactions: [
                    { icon: '❤️', count: 20 },
                    { icon: '🔥', count: 14 },
                    { icon: '💡', count: 0 },
                    { icon: '💧', count: 25 },
                    { icon: '📈', count: 12 }
                ]
            }
        ]
    }
};

export default function PerfilProfesorPage() {
    const params = useParams();
    const router = useRouter();
    const id = params?.id as string;
    const profesor = PROFESORES_DATA[id] || PROFESORES_DATA["1"];

    // Estados para controlar el Modal de Formulario
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [ratingInput, setRatingInput] = useState(5);
    const [claridadInput, setClaridadInput] = useState(50);
    const [dificultadInput, setDificultadInput] = useState(50);
    const [comentario, setComentario] = useState('');
    const [tagsForm, setTagsForm] = useState<string[]>([]);

    const toggleTagForm = (tag: string) => {
        setTagsForm(tagsForm.includes(tag) ? tagsForm.filter(t => t !== tag) : [...tagsForm, tag]);
    };

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans text-left selection:bg-sky-100 selection:text-sky-900 relative">
            <Navbar showSearch={false} />

            <main className="flex-1 w-full max-w-[1000px] mx-auto px-4 py-8 space-y-6 bg-white">

                {/* BOTÓN VOLVER */}
                <button
                    onClick={() => router.push('/profesores')}
                    className="flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-slate-800 transition-colors mb-2 focus:outline-none cursor-pointer"
                >
                    <ArrowLeft className="w-4 h-4" /> Volver a Resultados
                </button>

                {/* HEADER PRINCIPAL */}
                <div className="bg-white border border-slate-100 rounded-2xl p-6 flex flex-col sm:flex-row items-center justify-between gap-6 shadow-sm">
                    <div className="flex flex-col sm:flex-row items-center gap-5 text-center sm:text-left">
                        <div className="w-16 h-16 rounded-full overflow-hidden bg-slate-100 border border-slate-200 shrink-0">
                            <img src={profesor.avatar} alt={profesor.name} className="w-full h-full object-cover object-top" />
                        </div>
                        <div className="space-y-1">
                            <div className="flex flex-col sm:flex-row sm:items-center gap-3 justify-center sm:justify-start">
                                <h1 className="text-xl font-black text-slate-900 tracking-tight">{profesor.name}</h1>
                                <span className="bg-[#ff8a00] text-white text-[10px] font-black px-2 py-0.5 rounded-md shadow-sm">
                                    {profesor.rating}
                                </span>
                            </div>
                            <p className="text-xs font-semibold text-slate-500 flex flex-wrap items-center justify-center sm:justify-start gap-1">
                                <ClipboardList className="w-3.5 h-3.5 text-slate-400" /> {profesor.faculty} • {profesor.department}
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
                            <p className="text-xs text-slate-600 font-medium leading-relaxed">{profesor.aiSummary}</p>
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
                            <p className="font-bold text-slate-800">{profesor.education}</p>
                            <p className="text-[11px] text-slate-400">{profesor.university}</p>
                        </div>
                        <div>
                            <span className="text-[9px] font-bold text-slate-400 uppercase block tracking-wider">Áreas de Investigación</span>
                            <div className="flex flex-wrap gap-1.5 mt-1">
                                {profesor.research.map((item: string) => (
                                    <span key={item} className="px-2 py-0.5 bg-slate-50 border border-slate-200 text-slate-500 font-bold text-[9px] rounded-md">{item}</span>
                                ))}
                            </div>
                        </div>
                        <div>
                            <span className="text-[9px] font-bold text-slate-400 uppercase block tracking-wider">Experiencia</span>
                            <p className="font-bold text-slate-800">{profesor.experience}</p>
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
                                    <div className="flex justify-between text-[10px] font-bold text-slate-400 mb-1"><span>Claridad</span> <span className="text-slate-700 font-black">{profesor.metrics.claridad}</span></div>
                                    <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                                        <div className="bg-[#ff8a00] h-full" style={{ width: `${(profesor.metrics.claridad / 5) * 100}%` }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-[10px] font-bold text-slate-400 mb-1"><span>Facilidad</span> <span className="text-slate-700 font-black">{profesor.metrics.facilidad}</span></div>
                                    <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                                        <div className="bg-[#ff8a00] h-full" style={{ width: `${(profesor.metrics.facilidad / 5) * 100}%` }}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-[10px] font-bold text-slate-400 mb-1"><span>Ayuda</span> <span className="text-slate-700 font-black">{profesor.metrics.ayuda}</span></div>
                                    <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                                        <div className="bg-[#ff8a00] h-full" style={{ width: `${(profesor.metrics.ayuda / 5) * 100}%` }}></div>
                                    </div>
                                </div>
                            </div>
                            <p className="text-[10px] font-medium text-slate-400 pt-1 text-center">ℹ Basado en {profesor.metrics.total} evaluaciones</p>
                        </div>

                        <div className="bg-sky-50/40 border border-sky-100/60 rounded-2xl p-5">
                            <h4 className="text-[10px] font-black text-[#0284c7] uppercase tracking-wider mb-3">Estilo de Enseñanza</h4>
                            <ul className="space-y-1.5 text-xs font-semibold text-slate-600">
                                {profesor.style.map((item: string) => <li key={item} className="flex items-center gap-2"><span className="text-sky-500">✓</span> {item}</li>)}
                            </ul>
                        </div>
                    </div>

                    {/* Bloque Derecho Inyectado de forma limpia usando tu nuevo componente */}
                    <ListaComentarios comments={profesor.comments} />

                </div>
            </main>

            {/* POP-UP MODAL */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
                    <div className="bg-white rounded-2xl border border-slate-100 w-full max-w-md p-6 relative shadow-2xl my-auto text-left">
                        <button onClick={() => setIsModalOpen(false)} className="absolute right-4 top-4 text-slate-400 hover:text-slate-600 transition-colors p-1 cursor-pointer focus:outline-none"><X className="w-4 h-4" /></button>
                        <h2 className="text-base font-black text-slate-900 tracking-tight mb-1">Califica a este docente</h2>
                        <p className="text-[11px] text-slate-400 font-medium mb-5">Tu evaluación es anónima y apoya a la comunidad de San Marcos.</p>
                        <form onSubmit={(e) => { e.preventDefault(); setIsModalOpen(false); }} className="space-y-4">
                            <div>
                                <div className="flex justify-between items-center mb-1"><label className="text-[10px] font-black text-slate-700 uppercase">Puntaje General</label><span className="text-xs font-black text-[#ff8a00]">{ratingInput} / 10</span></div>
                                <input type="range" min="1" max="10" step="0.5" value={ratingInput} onChange={(e) => setRatingInput(Number(e.target.value))} className="w-full h-1.5 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-[#ff8a00]" />
                            </div>
                            <div>
                                <div className="flex justify-between items-center mb-1"><label className="text-[10px] font-black text-slate-700 uppercase">Claridad Explicativa</label><span className="text-xs font-bold text-slate-700">{claridadInput}%</span></div>
                                <input type="range" min="0" max="100" value={claridadInput} onChange={(e) => setClaridadInput(Number(e.target.value))} className="w-full h-1.5 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-[#ff8a00]" />
                            </div>
                            <div>
                                <div className="flex justify-between items-center mb-1"><label className="text-[10px] font-black text-slate-700 uppercase">Nivel de Exigencia</label><span className="text-xs font-bold text-slate-700">{dificultadInput}%</span></div>
                                <input type="range" min="0" max="100" value={dificultadInput} onChange={(e) => setDificultadInput(Number(e.target.value))} className="w-full h-1.5 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-slate-500" />
                            </div>
                            <div>
                                <label className="text-[10px] font-black text-slate-700 uppercase block mb-1.5">Etiquetas</label>
                                <div className="flex flex-wrap gap-1.5">
                                    {['Barco', 'Exigente', 'Justo', 'Proyectos', 'Teórico'].map((tag) => {
                                        const active = tagsForm.includes(tag);
                                        return <button key={tag} type="button" onClick={() => toggleTagForm(tag)} className={`px-2.5 py-1 rounded-md text-[9px] font-bold border cursor-pointer ${active ? 'bg-sky-50 text-sky-700 border-sky-300' : 'bg-white text-slate-400 border-slate-200'}`}>{tag}</button>
                                    })}
                                </div>
                            </div>
                            <div>
                                <label className="text-[10px] font-black text-slate-700 uppercase block mb-1">Reseña Detallada</label>
                                <textarea rows={3} value={comentario} onChange={(e) => setComentario(e.target.value)} required placeholder="Metodología de enseñanza, parciales, etc..." className="w-full bg-white border border-slate-200 rounded-xl p-3 text-xs font-medium text-slate-800 placeholder-slate-400 focus:outline-none focus:border-sky-400 shadow-sm resize-none" />
                            </div>
                            <button type="submit" className="w-full py-2.5 bg-[#ff8a00] hover:bg-[#ea580c] text-white font-bold text-xs rounded-xl transition-all shadow-sm cursor-pointer mt-2">Enviar Calificación</button>
                        </form>
                    </div>
                </div>
            )}

        </div>
    );
}
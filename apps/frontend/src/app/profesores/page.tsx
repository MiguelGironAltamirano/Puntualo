'use client'

import Link from 'next/link';

const PROFESSORS = [
    {
        id: 1,
        name: 'Julio César',
        department: 'Ingeniería de Sistemas',
        rating: 4.8,
        reviews: 120
    },
    {
        id: 2,
        name: 'María López',
        department: 'Ingeniería Industrial',
        rating: 4.5,
        reviews: 85
    },
    {
        id: 3,
        name: 'Carlos Ruiz',
        department: 'Ciencias de la Computación',
        rating: 3.9,
        reviews: 45
    },
    {
        id: 4,
        name: 'Ana García',
        department: 'Ingeniería de Software',
        rating: 4.9,
        reviews: 210
    }
];

export default function ProfesoresPage() {
    return (
        <main className="min-h-screen bg-[#f0f9ff] p-8">
            <div className="max-w-4xl mx-auto">
                <header className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-3xl font-extrabold text-[#004a7c]">Puntualo</h1>
                        <p className="text-gray-500">Directorio de Profesores</p>
                    </div>
                    <Link href="/login" className="px-4 py-2 bg-white text-gray-700 font-semibold rounded-lg shadow border hover:bg-gray-50 transition-colors">
                        Cerrar sesión
                    </Link>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {PROFESSORS.map(prof => (
                        <div key={prof.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                            <div className="flex items-start justify-between">
                                <div>
                                    <h2 className="text-xl font-bold text-gray-800">{prof.name}</h2>
                                    <p className="text-sm text-gray-500 mt-1">{prof.department}</p>
                                </div>
                                <div className="bg-orange-100 text-orange-700 px-3 py-1 rounded-full text-sm font-bold flex items-center gap-1">
                                    ⭐ {prof.rating}
                                </div>
                            </div>
                            <div className="mt-4 pt-4 border-t border-gray-50 flex justify-between items-center">
                                <span className="text-xs text-gray-400">{prof.reviews} reseñas</span>
                                <button className="text-sm text-[#004a7c] font-semibold hover:underline">
                                    Ver detalles →
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </main>
    );
}

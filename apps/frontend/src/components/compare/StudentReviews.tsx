import { Teacher } from './types';
import { Quote } from 'lucide-react';

interface StudentReviewsProps {
    teachers: Teacher[];
}

export function StudentReviews({ teachers }: StudentReviewsProps) {
    if (!teachers || teachers.length === 0) return null;

    const gridColsClass = 
        teachers.length === 2 ? 'md:grid-cols-2' : 
        teachers.length === 3 ? 'md:grid-cols-3' : 
        'md:grid-cols-4';

    return (
        <div className="mt-12 border-t border-slate-100 pt-10 animate-fadeIn">
            <h2 className="text-xl font-black text-slate-900 mb-8 tracking-tight">Lo que dicen los alumnos</h2>
            <div className={`grid grid-cols-1 ${gridColsClass} gap-8`}>
                {teachers.map((teacher) => (
                    <div key={teacher.id}>
                        <h3 className="text-xs font-black text-slate-900 uppercase tracking-wider mb-4 pb-2 border-b border-slate-100 truncate">
                            Reseñas de {teacher.name}
                        </h3>
                        {teacher.reviews && teacher.reviews.length > 0 ? (
                            <div className="space-y-4">
                                {teacher.reviews.map((review, i) => (
                                    <div key={i} className="bg-white border border-slate-200/60 p-6 rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.02)] relative group hover:border-sky-200 transition-colors">
                                        <Quote className="w-6 h-6 text-sky-100 mb-3 fill-sky-50" />
                                        <p className="text-sm text-slate-600 italic leading-relaxed mb-5 font-medium">"{review.text}"</p>
                                        <div className="flex items-center gap-2 pt-4 border-t border-slate-50">
                                            <span className="px-2 py-0.5 bg-sky-50 text-[#0284c7] font-bold text-[10px] rounded-md uppercase tracking-wider truncate max-w-[120px]" title={review.course}>
                                                {review.course}
                                            </span>
                                            <span className="text-[10px] font-semibold text-slate-400">
                                                - {review.date}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="bg-slate-50 border border-slate-100 border-dashed p-6 rounded-2xl h-full min-h-[120px] flex items-center justify-center text-xs font-medium text-slate-400">
                                Sin comentarios disponibles
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

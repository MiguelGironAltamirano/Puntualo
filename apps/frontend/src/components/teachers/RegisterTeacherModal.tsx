'use client'

import { useEffect, useState } from "react";
import { Sparkles, User, UserPlus } from "lucide-react";

interface RegisterTeacherModalProps {
    isOpen: boolean;
    onClose: () => void;
    onCreated?: () => void;
}

interface University {
    id: number;
    name: string;
    city: string;
    country: string;
}

interface Faculty {
    id: number;
    university_id: number;
    name: string;
}

const TITLES = [
    { value: "", label: "Sin título" },
    { value: "Dr.", label: "Doctor (Dr.)" },
    { value: "Dra.", label: "Doctora (Dra.)" },
    { value: "Mtro.", label: "Maestro (Mtro.)" },
    { value: "Mtra.", label: "Maestra (Mtra.)" },
    { value: "Ing.", label: "Ingeniero/a (Ing.)" },
    { value: "Lic.", label: "Licenciado/a (Lic.)" },
];

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function extractErrorMessage(detail: unknown): string {
    if (typeof detail === 'string') return detail;
    if (detail && typeof detail === 'object' && 'message' in detail) {
        const msg = (detail as { message?: unknown }).message;
        if (typeof msg === 'string') return msg;
    }
    return 'Ocurrió un error al registrar el profesor';
}

export function RegisterTeacherModal({ isOpen, onClose, onCreated }: RegisterTeacherModalProps) {
    const [title, setTitle] = useState('');
    const [fullName, setFullName] = useState('');
    const [universityId, setUniversityId] = useState<string>('');
    const [facultyId, setFacultyId] = useState<string>('');

    const [universities, setUniversities] = useState<University[]>([]);
    const [faculties, setFaculties] = useState<Faculty[]>([]);
    const [loadingCatalogs, setLoadingCatalogs] = useState(false);
    const [loadingFaculties, setLoadingFaculties] = useState(false);

    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        if (!isOpen) return;

        let cancelled = false;
        setLoadingCatalogs(true);
        fetch(`${API_URL}/catalogs/universities`)
            .then((res) => res.ok ? res.json() : Promise.reject(res))
            .then((data: University[]) => {
                if (!cancelled) {
                    setUniversities(data);
                    if (data.length === 1) {
                        setUniversityId(String(data[0].id));
                    }
                }
            })
            .catch(() => {
                if (!cancelled) setError('No se pudieron cargar las universidades');
            })
            .finally(() => {
                if (!cancelled) setLoadingCatalogs(false);
            });

        return () => { cancelled = true; };
    }, [isOpen]);

    useEffect(() => {
        if (!universityId) {
            setFaculties([]);
            setFacultyId('');
            return;
        }

        let cancelled = false;
        setLoadingFaculties(true);
        setFacultyId('');
        fetch(`${API_URL}/catalogs/universities/${universityId}/faculties`)
            .then((res) => res.ok ? res.json() : Promise.reject(res))
            .then((data: Faculty[]) => {
                if (!cancelled) setFaculties(data);
            })
            .catch(() => {
                if (!cancelled) setError('No se pudieron cargar las facultades');
            })
            .finally(() => {
                if (!cancelled) setLoadingFaculties(false);
            });

        return () => { cancelled = true; };
    }, [universityId]);

    const resetForm = () => {
        setTitle('');
        setFullName('');
        setUniversityId(universities.length === 1 ? String(universities[0].id) : '');
        setFacultyId('');
        setError('');
        setSuccess(false);
    };

    const handleClose = () => {
        resetForm();
        onClose();
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        const token = localStorage.getItem('access_token');
        if (!token) {
            setError('Tu sesión expiró. Iniciá sesión de nuevo.');
            return;
        }

        const trimmedName = fullName.trim();
        if (trimmedName.length < 3) {
            setError('El nombre del profesor debe tener al menos 3 caracteres');
            return;
        }
        if (!universityId || !facultyId) {
            setError('Seleccioná universidad y facultad');
            return;
        }

        const composedName = title
            ? `${title} ${trimmedName}`.replace(/\s+/g, ' ')
            : trimmedName;

        setSubmitting(true);

        try {
            const res = await fetch(`${API_URL}/professors/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    full_name: composedName,
                    university_id: Number(universityId),
                    faculty_id: Number(facultyId),
                }),
            });

            if (!res.ok) {
                const data = await res.json().catch(() => null);
                const detail = data?.detail;

                if (res.status === 403) {
                    setError('Necesitás verificar tu correo institucional para registrar profesores.');
                } else if (res.status === 401) {
                    setError('Tu sesión expiró. Iniciá sesión de nuevo.');
                } else if (res.status === 409) {
                    setError('Este profesor ya está registrado en la universidad seleccionada.');
                } else if (res.status === 404) {
                    setError(extractErrorMessage(detail));
                } else {
                    setError(extractErrorMessage(detail));
                }
                setSubmitting(false);
                return;
            }

            setSuccess(true);
            setSubmitting(false);
            onCreated?.();
            setTimeout(() => {
                handleClose();
            }, 1200);
        } catch {
            setError('Error de conexión con el servidor');
            setSubmitting(false);
        }
    };

    if (!isOpen) return null;

    const canSubmit =
        !submitting &&
        !success &&
        fullName.trim().length >= 3 &&
        Boolean(universityId) &&
        Boolean(facultyId);

    return (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl w-full max-w-lg p-8 shadow-xl relative animate-in fade-in zoom-in duration-200">
                {/* Header */}
                <div className="text-center mb-6">
                    <h2 className="text-xl font-bold text-slate-900 mb-1.5">Registrar nuevo profesor</h2>
                    <p className="text-xs text-slate-500 font-medium">
                        Agregá los datos académicos para sumarlo al catálogo.
                    </p>
                </div>

                {/* Avatar placeholder estático */}
                <div className="flex flex-col items-center mb-8">
                    <div className="w-20 h-20 rounded-full border-2 border-dashed border-slate-300 bg-slate-50 flex items-center justify-center text-slate-400">
                        <User className="w-7 h-7" />
                    </div>
                    <span className="text-[10px] font-medium text-slate-400 mt-2">
                        Foto de perfil (próximamente)
                    </span>
                </div>

                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-xs font-medium">
                        {error}
                    </div>
                )}
                {success && (
                    <div className="mb-4 p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-lg text-xs font-medium">
                        Profesor registrado correctamente. Está pendiente de validación.
                    </div>
                )}

                {/* Form */}
                <form className="space-y-5 mb-6" onSubmit={handleSubmit}>
                    {/* NOMBRE */}
                    <div>
                        <label className="block text-[10px] font-black text-slate-700 uppercase tracking-wider mb-1.5">
                            Nombres y apellidos
                        </label>
                        <input
                            type="text"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            placeholder="Ej. Juan Pérez"
                            minLength={3}
                            maxLength={200}
                            required
                            className="w-full bg-white border border-slate-200 text-sm font-medium text-slate-800 rounded-lg px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-sky-100 focus:border-sky-300 transition-all placeholder:text-slate-400"
                        />
                    </div>

                    {/* TITULO */}
                    <div>
                        <label className="block text-[10px] font-black text-slate-700 uppercase tracking-wider mb-1.5">
                            Título académico
                        </label>
                        <select
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            className="w-full bg-white border border-slate-200 text-sm font-medium text-slate-800 rounded-lg px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-sky-100 focus:border-sky-300 transition-all appearance-none cursor-pointer"
                        >
                            {TITLES.map((t) => (
                                <option key={t.value} value={t.value}>{t.label}</option>
                            ))}
                        </select>
                    </div>

                    {/* UNIVERSIDAD Y FACULTAD */}
                    <div className="grid grid-cols-1 gap-4">
                        <div>
                            <label className="block text-[10px] font-black text-slate-700 uppercase tracking-wider mb-1.5">
                                Universidad
                            </label>
                            <select
                                value={universityId}
                                onChange={(e) => setUniversityId(e.target.value)}
                                disabled={loadingCatalogs}
                                required
                                className="w-full bg-white border border-slate-200 text-sm font-medium text-slate-800 rounded-lg px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-sky-100 focus:border-sky-300 transition-all appearance-none cursor-pointer disabled:bg-slate-50 disabled:cursor-not-allowed"
                            >
                                <option value="">
                                    {loadingCatalogs ? 'Cargando...' : 'Seleccioná una universidad'}
                                </option>
                                {universities.map((u) => (
                                    <option key={u.id} value={u.id}>{u.name}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-[10px] font-black text-slate-700 uppercase tracking-wider mb-1.5">
                                Facultad
                            </label>
                            <select
                                value={facultyId}
                                onChange={(e) => setFacultyId(e.target.value)}
                                disabled={!universityId || loadingFaculties}
                                required
                                className="w-full bg-white border border-slate-200 text-sm font-medium text-slate-800 rounded-lg px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-sky-100 focus:border-sky-300 transition-all appearance-none cursor-pointer disabled:bg-slate-50 disabled:cursor-not-allowed"
                            >
                                <option value="">
                                    {!universityId
                                        ? 'Elegí una universidad primero'
                                        : loadingFaculties
                                            ? 'Cargando facultades...'
                                            : 'Seleccioná una facultad'}
                                </option>
                                {faculties.map((f) => (
                                    <option key={f.id} value={f.id}>{f.name}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* AI Insight */}
                    <div className="bg-[#e0f2fe]/50 border border-sky-100 rounded-xl p-4 flex items-start gap-3">
                        <div className="mt-0.5 shrink-0">
                            <Sparkles className="w-4 h-4 text-[#0284c7]" />
                        </div>
                        <p className="text-[11px] text-sky-900 font-medium leading-relaxed">
                            <span className="font-bold text-sky-950">Importante:</span> El profesor quedará en estado pendiente de validación hasta que nuestro pipeline confirme su existencia con fuentes oficiales.
                        </p>
                    </div>

                    {/* Acciones */}
                    <div className="flex items-center justify-end gap-5 pt-4 border-t border-slate-100">
                        <button
                            type="button"
                            onClick={handleClose}
                            disabled={submitting}
                            className="text-[11px] font-bold text-slate-500 hover:text-slate-800 transition-colors cursor-pointer uppercase tracking-wider disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            disabled={!canSubmit}
                            className={`px-6 py-2.5 rounded-lg text-[11px] font-black flex items-center gap-2 transition-colors uppercase tracking-wider shadow-sm ${
                                canSubmit
                                    ? 'bg-[#ff8a00] hover:bg-[#ea580c] text-white cursor-pointer'
                                    : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                            }`}
                        >
                            {submitting ? 'Registrando...' : 'Registrar profesor'}
                            {!submitting && <UserPlus className="w-3.5 h-3.5" strokeWidth={3} />}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

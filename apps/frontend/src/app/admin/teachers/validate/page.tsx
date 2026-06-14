'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
    ArrowLeft,
    Check,
    X,
    GraduationCap,
    University,
    BookOpen,
    CalendarDays,
    ShieldCheck,
    ShieldX,
    Search,
    FileSearch,
    UserCircle2,
} from 'lucide-react';

// ── Types ──────────────────────────────────────────────────────────────────────

interface EvidenceInfo {
    source: string;
    role: string;
    found: boolean;
    affiliation_confirmed: boolean;
    confidence: number | null;
}

interface ProfessorItem {
    professor_id: string;
    full_name: string;
    university_name: string;
    faculty_name: string;
    validation_status: string;
    global_score: number | null;
    total_evaluations: number;
    registered_at: string;
    evidence: EvidenceInfo[];
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function getInitials(name: string): string {
    return name
        .split(' ')
        .filter((w) => w.length > 2)
        .slice(0, 2)
        .map((n) => n[0])
        .join('')
        .toUpperCase();
}

function timeAgo(dateStr: string): string {
    const diff = Date.now() - new Date(dateStr).getTime();
    const hours = Math.floor(diff / 3_600_000);
    if (hours < 1) return 'Hace menos de 1 hora';
    if (hours < 24) return `Hace ${hours}h`;
    const days = Math.floor(hours / 24);
    if (days < 30) return `Hace ${days} día${days > 1 ? 's' : ''}`;
    const months = Math.floor(days / 30);
    return `Hace ${months} mes${months > 1 ? 'es' : ''}`;
}

const SOURCE_LABELS: Record<string, string> = {
    unmsm_directory: 'Directorio UNMSM',
    openalex: 'OpenAlex',
    orcid: 'ORCID',
    tavily: 'Búsqueda Web',
};

// ── Professor Detail Modal ─────────────────────────────────────────────────────

function ProfessorDetailModal({
    professor,
    onClose,
    onApprove,
    onReject,
    processing,
}: {
    professor: ProfessorItem;
    onClose: () => void;
    onApprove: () => void;
    onReject: () => void;
    processing: boolean;
}) {
    const overlayRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        function handleKey(e: KeyboardEvent) {
            if (e.key === 'Escape') onClose();
        }
        window.addEventListener('keydown', handleKey);
        return () => window.removeEventListener('keydown', handleKey);
    }, [onClose]);

    return (
        <div
            ref={overlayRef}
            className="pv-modal-overlay"
            onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}
        >
            <div className="pv-modal">
                {/* Modal Header */}
                <div className="pv-modal-header">
                    <div className="pv-modal-avatar">
                        {getInitials(professor.full_name)}
                    </div>
                    <div className="pv-modal-title-block">
                        <h2 className="pv-modal-name">{professor.full_name}</h2>
                        <p className="pv-modal-sub">Docente · {professor.faculty_name}</p>
                    </div>
                    <button className="pv-modal-close" onClick={onClose} aria-label="Cerrar">
                        <X size={18} />
                    </button>
                </div>

                {/* Info Grid */}
                <div className="pv-modal-body">
                    <div className="pv-info-grid">
                        <div className="pv-info-item">
                            <University size={15} className="pv-info-icon" />
                            <div>
                                <p className="pv-info-label">Universidad</p>
                                <p className="pv-info-value">{professor.university_name}</p>
                            </div>
                        </div>
                        <div className="pv-info-item">
                            <GraduationCap size={15} className="pv-info-icon" />
                            <div>
                                <p className="pv-info-label">Facultad</p>
                                <p className="pv-info-value">{professor.faculty_name}</p>
                            </div>
                        </div>
                        <div className="pv-info-item">
                            <CalendarDays size={15} className="pv-info-icon" />
                            <div>
                                <p className="pv-info-label">Registrado</p>
                                <p className="pv-info-value">{timeAgo(professor.registered_at)}</p>
                            </div>
                        </div>
                        <div className="pv-info-item">
                            <BookOpen size={15} className="pv-info-icon" />
                            <div>
                                <p className="pv-info-label">Estado Actual</p>
                                <span className="pv-status-badge pv-status-not-found">
                                    No encontrado (IA)
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Evidence Section */}
                    {professor.evidence.length > 0 && (
                        <div className="pv-evidence-section">
                            <h3 className="pv-evidence-title">
                                <FileSearch size={15} />
                                Resultados de Búsqueda Automática (IA)
                            </h3>
                            <div className="pv-evidence-list">
                                {professor.evidence.map((ev, idx) => (
                                    <div key={idx} className="pv-evidence-row">
                                        <div className="pv-evidence-source">
                                            <span className="pv-source-dot" style={{
                                                background: ev.found ? '#22c55e' : '#f87171'
                                            }} />
                                            {SOURCE_LABELS[ev.source] || ev.source}
                                            <span className="pv-source-role">({ev.role})</span>
                                        </div>
                                        <div className="pv-evidence-badges">
                                            <span className={`pv-ev-badge ${ev.found ? 'pv-ev-badge--found' : 'pv-ev-badge--not-found'}`}>
                                                {ev.found ? '✓ Encontrado' : '✗ No encontrado'}
                                            </span>
                                            {ev.affiliation_confirmed && (
                                                <span className="pv-ev-badge pv-ev-badge--confirmed">
                                                    Afiliación confirmada
                                                </span>
                                            )}
                                            {ev.confidence !== null && (
                                                <span className="pv-ev-badge pv-ev-badge--confidence">
                                                    Confianza: {(ev.confidence * 100).toFixed(0)}%
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {professor.evidence.length === 0 && (
                        <div className="pv-no-evidence">
                            <Search size={20} />
                            <span>No se registraron evidencias de búsqueda automática para este profesor.</span>
                        </div>
                    )}
                </div>

                {/* Modal Footer Actions */}
                <div className="pv-modal-footer">
                    <button
                        className="pv-btn-reject"
                        onClick={onReject}
                        disabled={processing}
                    >
                        <ShieldX size={16} />
                        Rechazar
                    </button>
                    <button
                        className="pv-btn-approve"
                        onClick={onApprove}
                        disabled={processing}
                    >
                        <ShieldCheck size={16} />
                        Aprobar
                    </button>
                </div>
            </div>
        </div>
    );
}

// ── Professor Card ─────────────────────────────────────────────────────────────

function ProfessorCard({
    professor,
    onApprove,
    onReject,
}: {
    professor: ProfessorItem;
    onApprove: (id: string) => Promise<void>;
    onReject: (id: string) => Promise<void>;
}) {
    const [processing, setProcessing] = useState(false);
    const [showModal, setShowModal] = useState(false);

    async function handleApprove() {
        setProcessing(true);
        setShowModal(false);
        await onApprove(professor.professor_id);
    }

    async function handleReject() {
        setProcessing(true);
        setShowModal(false);
        await onReject(professor.professor_id);
    }

    return (
        <>
            {showModal && (
                <ProfessorDetailModal
                    professor={professor}
                    onClose={() => setShowModal(false)}
                    onApprove={handleApprove}
                    onReject={handleReject}
                    processing={processing}
                />
            )}
            <div className={`pv-card ${processing ? 'pv-card--processing' : ''}`}>
                {/* Avatar */}
                <div className="pv-card-avatar">
                    {getInitials(professor.full_name)}
                </div>

                {/* Info */}
                <div className="pv-card-info">
                    <h3 className="pv-card-name">{professor.full_name}</h3>
                    <p className="pv-card-meta">
                        <GraduationCap size={13} className="pv-meta-icon" />
                        <span>Docente</span>
                        <span className="pv-meta-dot">·</span>
                        <BookOpen size={13} className="pv-meta-icon" />
                        <span>{professor.faculty_name}</span>
                        <span className="pv-meta-dot">·</span>
                        <University size={13} className="pv-meta-icon" />
                        <span>{professor.university_name}</span>
                    </p>
                </div>

                {/* Actions */}
                <div className="pv-card-actions">
                    <button
                        className="pv-btn-detail"
                        onClick={() => setShowModal(true)}
                        disabled={processing}
                    >
                        Ver Detalle
                    </button>
                    <button
                        className="pv-btn-reject-sm"
                        onClick={handleReject}
                        disabled={processing}
                    >
                        <X size={15} />
                        Rechazar
                    </button>
                    <button
                        className="pv-btn-approve-sm"
                        onClick={handleApprove}
                        disabled={processing}
                    >
                        <Check size={15} />
                        Aprobar
                    </button>
                </div>
            </div>
        </>
    );
}

// ── Main Page ──────────────────────────────────────────────────────────────────

export default function AdminValidateTeachersPage() {
    const router = useRouter();
    const [items, setItems] = useState<ProfessorItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    function getToken() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            router.replace('/login');
            return null;
        }
        return token;
    }

    useEffect(() => {
        const token = getToken();
        if (!token) return;

        fetch(`${API}/admin/teachers/validations/pending`, {
            headers: { Authorization: `Bearer ${token}` },
        })
            .then((res) => {
                if (res.status === 401 || res.status === 403) {
                    router.replace('/login');
                    throw new Error('No autorizado');
                }
                return res.json();
            })
            .then((data) => setItems(data.items ?? []))
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    async function handleApprove(professorId: string) {
        const token = getToken();
        if (!token) return;
        try {
            const res = await fetch(`${API}/admin/teachers/validations/${professorId}/approve`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) throw new Error('Error al aprobar');
            setItems((prev) => prev.filter((p) => p.professor_id !== professorId));
        } catch {
            alert('No se pudo aprobar el profesor. Intenta de nuevo.');
        }
    }

    async function handleReject(professorId: string) {
        const token = getToken();
        if (!token) return;
        try {
            const res = await fetch(`${API}/admin/teachers/validations/${professorId}/reject`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) throw new Error('Error al rechazar');
            setItems((prev) => prev.filter((p) => p.professor_id !== professorId));
        } catch {
            alert('No se pudo rechazar el profesor. Intenta de nuevo.');
        }
    }

    return (
        <>
            <style>{`
                /* ── Base ── */
                .pv-page {
                    min-height: 100vh;
                    background: #f0f4f8;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                }
                .pv-main {
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 40px 24px 64px;
                }

                /* ── Header ── */
                .pv-back-btn {
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    font-size: 13px;
                    font-weight: 600;
                    color: #64748b;
                    background: none;
                    border: none;
                    padding: 0;
                    cursor: pointer;
                    margin-bottom: 18px;
                    transition: color 0.2s;
                }
                .pv-back-btn:hover { color: #334155; }
                .pv-title {
                    font-size: 28px;
                    font-weight: 800;
                    color: #0f172a;
                    margin: 0 0 6px;
                    letter-spacing: -0.4px;
                }
                .pv-subtitle {
                    font-size: 14px;
                    color: #64748b;
                    margin: 0 0 28px;
                }

                /* ── Card ── */
                .pv-card {
                    background: #fff;
                    border-radius: 14px;
                    border: 1.5px solid #e2e8f0;
                    padding: 20px 24px;
                    display: flex;
                    align-items: center;
                    gap: 16px;
                    margin-bottom: 12px;
                    transition: box-shadow 0.2s, opacity 0.2s;
                }
                .pv-card:hover {
                    box-shadow: 0 4px 16px rgba(0,0,0,0.07);
                }
                .pv-card--processing {
                    opacity: 0.45;
                    pointer-events: none;
                }

                /* ── Avatar ── */
                .pv-card-avatar {
                    width: 48px;
                    height: 48px;
                    border-radius: 50%;
                    background: #e0f2fe;
                    color: #0369a1;
                    font-size: 16px;
                    font-weight: 800;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                    letter-spacing: 0.5px;
                }

                /* ── Card Info ── */
                .pv-card-info {
                    flex: 1;
                    min-width: 0;
                }
                .pv-card-name {
                    font-size: 15px;
                    font-weight: 700;
                    color: #0f172a;
                    margin: 0 0 4px;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                }
                .pv-card-meta {
                    display: flex;
                    align-items: center;
                    gap: 5px;
                    font-size: 13px;
                    color: #64748b;
                    margin: 0;
                    flex-wrap: wrap;
                }
                .pv-meta-icon { color: #94a3b8; flex-shrink: 0; }
                .pv-meta-dot { color: #cbd5e1; }

                /* ── Card Actions ── */
                .pv-card-actions {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    flex-shrink: 0;
                }
                .pv-btn-detail {
                    font-size: 13px;
                    font-weight: 600;
                    color: #0891b2;
                    background: none;
                    border: none;
                    cursor: pointer;
                    padding: 6px 10px;
                    border-radius: 6px;
                    transition: background 0.15s, color 0.15s;
                    white-space: nowrap;
                }
                .pv-btn-detail:hover {
                    background: #e0f2fe;
                    color: #0e7490;
                }
                .pv-btn-reject-sm {
                    display: inline-flex;
                    align-items: center;
                    gap: 5px;
                    font-size: 13px;
                    font-weight: 600;
                    color: #475569;
                    background: #fff;
                    border: 1.5px solid #cbd5e1;
                    border-radius: 8px;
                    padding: 7px 14px;
                    cursor: pointer;
                    transition: all 0.18s;
                    white-space: nowrap;
                }
                .pv-btn-reject-sm:hover {
                    border-color: #ef4444;
                    color: #ef4444;
                    background: #fff5f5;
                }
                .pv-btn-reject-sm:disabled, .pv-btn-approve-sm:disabled, .pv-btn-detail:disabled {
                    opacity: 0.4;
                    cursor: not-allowed;
                }
                .pv-btn-approve-sm {
                    display: inline-flex;
                    align-items: center;
                    gap: 5px;
                    font-size: 13px;
                    font-weight: 700;
                    color: #fff;
                    background: #f97316;
                    border: none;
                    border-radius: 8px;
                    padding: 7px 16px;
                    cursor: pointer;
                    transition: background 0.18s, transform 0.15s;
                    white-space: nowrap;
                }
                .pv-btn-approve-sm:hover { background: #ea580c; transform: scale(1.03); }

                /* ── Modal Overlay ── */
                .pv-modal-overlay {
                    position: fixed;
                    inset: 0;
                    background: rgba(2,8,23,0.7);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 9999;
                    animation: pvFadeIn 0.18s ease;
                    padding: 20px;
                }
                @keyframes pvFadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }

                /* ── Modal ── */
                .pv-modal {
                    background: #fff;
                    border-radius: 18px;
                    width: 100%;
                    max-width: 600px;
                    max-height: 90vh;
                    overflow-y: auto;
                    box-shadow: 0 24px 80px rgba(0,0,0,0.35);
                    animation: pvScaleIn 0.2s cubic-bezier(.34,1.56,.64,1);
                }
                @keyframes pvScaleIn {
                    from { transform: scale(0.9); opacity: 0; }
                    to { transform: scale(1); opacity: 1; }
                }
                .pv-modal-header {
                    display: flex;
                    align-items: center;
                    gap: 14px;
                    padding: 24px 24px 20px;
                    border-bottom: 1px solid #f1f5f9;
                    position: sticky;
                    top: 0;
                    background: #fff;
                    z-index: 2;
                    border-radius: 18px 18px 0 0;
                }
                .pv-modal-avatar {
                    width: 52px;
                    height: 52px;
                    border-radius: 50%;
                    background: #e0f2fe;
                    color: #0369a1;
                    font-size: 18px;
                    font-weight: 800;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                }
                .pv-modal-title-block { flex: 1; }
                .pv-modal-name {
                    font-size: 18px;
                    font-weight: 800;
                    color: #0f172a;
                    margin: 0 0 3px;
                }
                .pv-modal-sub {
                    font-size: 13px;
                    color: #64748b;
                    margin: 0;
                }
                .pv-modal-close {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    background: #f1f5f9;
                    border: none;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    color: #64748b;
                    transition: background 0.15s;
                    flex-shrink: 0;
                }
                .pv-modal-close:hover { background: #e2e8f0; }

                /* ── Modal Body ── */
                .pv-modal-body { padding: 20px 24px; }
                .pv-info-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 16px;
                    margin-bottom: 24px;
                }
                .pv-info-item {
                    display: flex;
                    align-items: flex-start;
                    gap: 10px;
                }
                .pv-info-icon { color: #94a3b8; flex-shrink: 0; margin-top: 2px; }
                .pv-info-label {
                    font-size: 11px;
                    font-weight: 600;
                    color: #94a3b8;
                    text-transform: uppercase;
                    letter-spacing: 0.06em;
                    margin: 0 0 3px;
                }
                .pv-info-value {
                    font-size: 14px;
                    font-weight: 600;
                    color: #1e293b;
                    margin: 0;
                }
                .pv-status-badge {
                    display: inline-block;
                    font-size: 11px;
                    font-weight: 700;
                    padding: 3px 10px;
                    border-radius: 99px;
                }
                .pv-status-not-found { background: #fff7ed; color: #c2410c; }

                /* ── Evidence Section ── */
                .pv-evidence-section {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 10px;
                    padding: 16px;
                }
                .pv-evidence-title {
                    display: flex;
                    align-items: center;
                    gap: 7px;
                    font-size: 12px;
                    font-weight: 700;
                    color: #475569;
                    text-transform: uppercase;
                    letter-spacing: 0.06em;
                    margin: 0 0 12px;
                }
                .pv-evidence-list { display: flex; flex-direction: column; gap: 10px; }
                .pv-evidence-row {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 10px;
                    flex-wrap: wrap;
                }
                .pv-evidence-source {
                    display: flex;
                    align-items: center;
                    gap: 7px;
                    font-size: 13px;
                    font-weight: 600;
                    color: #334155;
                }
                .pv-source-dot {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    flex-shrink: 0;
                }
                .pv-source-role {
                    font-size: 11px;
                    color: #94a3b8;
                    font-weight: 400;
                }
                .pv-evidence-badges { display: flex; gap: 5px; flex-wrap: wrap; }
                .pv-ev-badge {
                    font-size: 11px;
                    font-weight: 600;
                    padding: 2px 8px;
                    border-radius: 99px;
                }
                .pv-ev-badge--found { background: #f0fdf4; color: #16a34a; }
                .pv-ev-badge--not-found { background: #fff5f5; color: #ef4444; }
                .pv-ev-badge--confirmed { background: #eff6ff; color: #2563eb; }
                .pv-ev-badge--confidence { background: #faf5ff; color: #7c3aed; }
                .pv-no-evidence {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 13px;
                    color: #94a3b8;
                    background: #f8fafc;
                    border-radius: 10px;
                    padding: 14px 16px;
                    border: 1px solid #e2e8f0;
                }

                /* ── Modal Footer ── */
                .pv-modal-footer {
                    display: flex;
                    align-items: center;
                    justify-content: flex-end;
                    gap: 10px;
                    padding: 16px 24px 24px;
                    border-top: 1px solid #f1f5f9;
                }
                .pv-btn-reject {
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    font-size: 14px;
                    font-weight: 600;
                    color: #475569;
                    background: #fff;
                    border: 1.5px solid #cbd5e1;
                    border-radius: 9px;
                    padding: 9px 18px;
                    cursor: pointer;
                    transition: all 0.18s;
                }
                .pv-btn-reject:hover { border-color: #ef4444; color: #ef4444; background: #fff5f5; }
                .pv-btn-reject:disabled, .pv-btn-approve:disabled { opacity: 0.4; cursor: not-allowed; }
                .pv-btn-approve {
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    font-size: 14px;
                    font-weight: 700;
                    color: #fff;
                    background: #f97316;
                    border: none;
                    border-radius: 9px;
                    padding: 9px 20px;
                    cursor: pointer;
                    transition: background 0.18s, transform 0.15s;
                }
                .pv-btn-approve:hover { background: #ea580c; transform: scale(1.03); }

                /* ── Empty / Loading / Error ── */
                .pv-state {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 64px 24px;
                    gap: 12px;
                    color: #94a3b8;
                    text-align: center;
                }
                .pv-state-icon {
                    width: 56px;
                    height: 56px;
                    border-radius: 50%;
                    background: #f1f5f9;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .pv-state-title { font-size: 16px; font-weight: 700; color: #334155; margin: 0; }
                .pv-state-body { font-size: 14px; color: #94a3b8; margin: 0; }

                /* ── Skeleton ── */
                @keyframes pvShimmer {
                    0% { background-position: -600px 0; }
                    100% { background-position: 600px 0; }
                }
                .pv-skeleton {
                    border-radius: 14px;
                    background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
                    background-size: 600px 100%;
                    animation: pvShimmer 1.4s infinite linear;
                    height: 88px;
                    margin-bottom: 12px;
                }
            `}</style>

            <div className="pv-page">
                <main className="pv-main">
                    {/* Header */}
                    <button className="pv-back-btn" onClick={() => router.push('/admin')}>
                        <ArrowLeft size={16} /> Volver al Panel
                    </button>
                    <h1 className="pv-title">Validación de Profesores</h1>
                    <p className="pv-subtitle">
                        Revisa y aprueba los registros del cuerpo docente que no pudieron ser validados
                        automáticamente por el sistema de IA.
                    </p>

                    {/* Content */}
                    {loading ? (
                        <>
                            {[1, 2, 3].map((i) => <div key={i} className="pv-skeleton" />)}
                        </>
                    ) : error ? (
                        <div className="pv-state">
                            <div className="pv-state-icon">
                                <X size={24} style={{ color: '#ef4444' }} />
                            </div>
                            <p className="pv-state-title">Error al cargar</p>
                            <p className="pv-state-body">{error}</p>
                        </div>
                    ) : items.length === 0 ? (
                        <div className="pv-state">
                            <div className="pv-state-icon">
                                <UserCircle2 size={26} style={{ color: '#94a3b8' }} />
                            </div>
                            <p className="pv-state-title">Todo validado</p>
                            <p className="pv-state-body">
                                No hay profesores pendientes de validación manual en este momento.
                            </p>
                        </div>
                    ) : (
                        <>
                            {items.map((professor) => (
                                <ProfessorCard
                                    key={professor.professor_id}
                                    professor={professor}
                                    onApprove={handleApprove}
                                    onReject={handleReject}
                                />
                            ))}
                            <p style={{ fontSize: 13, color: '#94a3b8', marginTop: 8 }}>
                                Mostrando {items.length} profesor{items.length !== 1 ? 'es' : ''} pendiente{items.length !== 1 ? 's' : ''}
                            </p>
                        </>
                    )}
                </main>
            </div>
        </>
    );
}

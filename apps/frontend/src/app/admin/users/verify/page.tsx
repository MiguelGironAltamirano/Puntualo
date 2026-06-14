'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
    CheckCircle,
    XCircle,
    ArrowLeft,
    Clock,
    UserCircle2,
    GraduationCap,
    CreditCard,
    ImageOff,
    X,
    ZoomIn,
} from 'lucide-react';

// ── Types ──────────────────────────────────────────────────────────────────────

interface DocumentInfo {
    id: string;
    side: 'front' | 'back' | null;
    file_path: string;
    mime_type: string;
}

interface PendingItem {
    request_id: string;
    user_id: string;
    full_name: string;
    email: string;
    username: string;
    dni: string | null;
    career_name: string | null;
    documents: DocumentInfo[];
    submitted_at: string;
}

// ── Constants ──────────────────────────────────────────────────────────────────

const REJECTION_REASONS = [
    { value: 'Documento ilegible', label: 'Documento ilegible', description: 'La foto es borrosa, oscura o con reflejos que impiden leer los datos.' },
    { value: 'Falta una cara del documento', label: 'Falta una cara del documento', description: 'No se subió el frente o el reverso del carnet.' },
    { value: 'Datos no coinciden', label: 'Datos no coinciden', description: 'La información del perfil no coincide con la del carnet.' },
    { value: 'Documento inválido', label: 'Documento inválido', description: 'No parece ser un carnet universitario o matrícula oficial válida.' },
];

// ── Helpers ────────────────────────────────────────────────────────────────────

function timeAgo(dateStr: string): string {
    const diff = Date.now() - new Date(dateStr).getTime();
    const hours = Math.floor(diff / 3_600_000);
    if (hours < 1) return 'Hace menos de 1 hora';
    if (hours < 24) return `Hace ${hours} hora${hours > 1 ? 's' : ''}`;
    const days = Math.floor(hours / 24);
    return `Hace ${days} día${days > 1 ? 's' : ''}`;
}

function getInitials(name: string): string {
    return name
        .split(' ')
        .slice(0, 2)
        .map((n) => n[0])
        .join('')
        .toUpperCase();
}

const AVATAR_COLORS = [
    '#0074D9', '#FF6B35', '#2ECC71', '#9B59B6', '#E74C3C',
    '#1ABC9C', '#F39C12', '#3498DB',
];

function avatarColor(name: string): string {
    let hash = 0;
    for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
    return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
}

// ── Image Lightbox ─────────────────────────────────────────────────────────────

function Lightbox({ url, onClose }: { url: string; onClose: () => void }) {
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
            className="lightbox-overlay"
            onClick={(e) => { if (e.target === overlayRef.current) onClose(); }}
        >
            <div className="lightbox-container">
                <button className="lightbox-close" onClick={onClose} aria-label="Cerrar">
                    <X size={22} />
                </button>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                    src={url}
                    alt="Documento de verificación"
                    className="lightbox-img"
                    draggable={false}
                />
            </div>
        </div>
    );
}

// ── Document Thumbnail ─────────────────────────────────────────────────────────

function DocThumb({
    doc,
    onOpen,
}: {
    doc: DocumentInfo;
    onOpen: (url: string) => void;
}) {
    const label = doc.side === 'front' ? 'Frente' : doc.side === 'back' ? 'Dorso' : '—';

    return (
        <button
            className="doc-thumb"
            onClick={() => onOpen(doc.file_path)}
            title={`Ver imagen: ${label}`}
        >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={doc.file_path} alt={label} className="doc-thumb-img" />
            <span className="doc-thumb-badge">{label}</span>
            <div className="doc-thumb-zoom">
                <ZoomIn size={14} />
            </div>
        </button>
    );
}

// ── Verification Row ───────────────────────────────────────────────────────────

function VerificationRow({
    item,
    onApprove,
    onReject,
    onOpenLightbox,
}: {
    item: PendingItem;
    onApprove: (requestId: string) => void;
    onReject: (requestId: string, reason: string) => void;
    onOpenLightbox: (url: string) => void;
}) {
    const [selectedReason, setSelectedReason] = useState('');
    const [processing, setProcessing] = useState(false);

    const frontDoc = item.documents.find((d) => d.side === 'front');
    const backDoc = item.documents.find((d) => d.side === 'back');
    const hasBothSides = !!frontDoc && !!backDoc;

    async function handleApprove() {
        setProcessing(true);
        await onApprove(item.request_id);
    }

    async function handleReject() {
        if (!selectedReason) return;
        setProcessing(true);
        await onReject(item.request_id, selectedReason);
    }

    return (
        <tr className={`verify-row ${processing ? 'verify-row--processing' : ''}`}>
            {/* Usuario */}
            <td className="verify-cell">
                    <div className="user-info">
                        <div
                            className="user-avatar"
                            style={{ background: avatarColor(item.full_name) }}
                        >
                            {getInitials(item.full_name)}
                        </div>
                        <div>
                            <p className="user-name">{item.full_name}</p>
                            <p className="user-email">{item.email}</p>
                        </div>
                    </div>
                </td>

                {/* Detalles */}
                <td className="verify-cell">
                    <div className="detail-lines">
                        {item.career_name && (
                            <span className="detail-line">
                                <GraduationCap size={13} className="detail-icon" />
                                {item.career_name}
                            </span>
                        )}
                        {item.dni && (
                            <span className="detail-line">
                                <CreditCard size={13} className="detail-icon" />
                                DNI: {item.dni}
                            </span>
                        )}
                        <span className="detail-line">
                            <Clock size={13} className="detail-icon" />
                            {timeAgo(item.submitted_at)}
                        </span>
                    </div>
                </td>

            {/* Documentación */}
            <td className="verify-cell">
                <div className="docs-row">
                    {frontDoc ? (
                        <DocThumb doc={frontDoc} onOpen={onOpenLightbox} />
                    ) : (
                        <div className="doc-missing">
                            <ImageOff size={20} className="doc-missing-icon" />
                            <span className="badge-missing">Falta Frente</span>
                        </div>
                    )}
                    {backDoc ? (
                        <DocThumb doc={backDoc} onOpen={onOpenLightbox} />
                    ) : (
                        <div className="doc-missing">
                            <ImageOff size={20} className="doc-missing-icon" />
                            <span className="badge-missing">Falta Dorso</span>
                        </div>
                    )}
                </div>
                    {!hasBothSides && (
                        <span className="badge-incomplete">Incompleto</span>
                    )}
                </td>

                {/* Motivo de rechazo */}
                <td className="verify-cell">
                    <select
                        className="reason-select"
                        value={selectedReason}
                        onChange={(e) => setSelectedReason(e.target.value)}
                        disabled={processing}
                    >
                        <option value="">Seleccionar...</option>
                        {REJECTION_REASONS.map((r) => (
                            <option key={r.value} value={r.value}>
                                {r.label}
                            </option>
                        ))}
                    </select>
                </td>

                {/* Acciones */}
                <td className="verify-cell verify-cell--actions">
                    <button
                        id={`btn-reject-${item.request_id}`}
                        className="action-btn action-btn--reject"
                        onClick={handleReject}
                        disabled={!selectedReason || processing}
                        title="Rechazar verificación"
                    >
                        <XCircle size={20} />
                    </button>
                    <button
                        id={`btn-approve-${item.request_id}`}
                        className="action-btn action-btn--approve"
                        onClick={handleApprove}
                        disabled={processing}
                        title="Aprobar verificación"
                    >
                        <CheckCircle size={20} />
                    </button>
                </td>
            </tr>
    );
}

// ── Main Page ──────────────────────────────────────────────────────────────────

export default function AdminVerifyUsersPage() {
    const router = useRouter();
    const [items, setItems] = useState<PendingItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [lightboxUrl, setLightboxUrl] = useState<string | null>(null);

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

        fetch(`${API}/admin/users/verifications/pending`, {
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

    async function handleApprove(requestId: string) {
        const token = getToken();
        if (!token) return;

        try {
            const res = await fetch(`${API}/admin/users/verifications/${requestId}/approve`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) throw new Error('Error al aprobar');
            setItems((prev) => prev.filter((i) => i.request_id !== requestId));
        } catch {
            alert('No se pudo aprobar la verificación. Intenta de nuevo.');
        }
    }

    async function handleReject(requestId: string, reason: string) {
        const token = getToken();
        if (!token) return;

        try {
            const res = await fetch(`${API}/admin/users/verifications/${requestId}/reject`, {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ reason }),
            });
            if (!res.ok) throw new Error('Error al rechazar');
            setItems((prev) => prev.filter((i) => i.request_id !== requestId));
        } catch {
            alert('No se pudo rechazar la verificación. Intenta de nuevo.');
        }
    }

    return (
        <>
            <style>{`
                /* ── Layout ── */
                .verify-page {
                    min-height: 100vh;
                    background: #f0f4f8;
                    font-family: 'Inter', 'Segoe UI', sans-serif;
                }
                .verify-main {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 40px 24px;
                }

                /* ── Header ── */
                .verify-header {
                    margin-bottom: 28px;
                }
                .back-btn {
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    font-size: 13px;
                    font-weight: 600;
                    color: #64748b;
                    text-decoration: none;
                    margin-bottom: 16px;
                    cursor: pointer;
                    background: none;
                    border: none;
                    padding: 0;
                    transition: color 0.2s;
                }
                .back-btn:hover { color: #334155; }
                .verify-title {
                    font-size: 28px;
                    font-weight: 800;
                    color: #0f172a;
                    margin: 0 0 6px;
                    letter-spacing: -0.4px;
                }
                .verify-subtitle {
                    font-size: 14px;
                    color: #64748b;
                    margin: 0;
                }

                /* ── Card ── */
                .verify-card {
                    background: #fff;
                    border-radius: 16px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04);
                    overflow: hidden;
                }
                .verify-card-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 20px 24px;
                    border-bottom: 1px solid #f1f5f9;
                }
                .pending-badge {
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    background: #fff7ed;
                    color: #c2410c;
                    font-size: 13px;
                    font-weight: 700;
                    padding: 6px 14px;
                    border-radius: 99px;
                    letter-spacing: 0.02em;
                }
                .pending-dot {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #ea580c;
                    animation: pulse 1.5s infinite;
                }
                @keyframes pulse {
                    0%, 100% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.5; transform: scale(0.85); }
                }

                /* ── Table ── */
                .verify-table-wrap {
                    overflow-x: auto;
                }
                .verify-table {
                    width: 100%;
                    border-collapse: collapse;
                }
                .verify-table thead th {
                    padding: 12px 16px;
                    text-align: left;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 0.08em;
                    color: #94a3b8;
                    text-transform: uppercase;
                    background: #f8fafc;
                    border-bottom: 1px solid #f1f5f9;
                }
                .verify-row {
                    border-bottom: 1px solid #f1f5f9;
                    transition: background 0.15s;
                }
                .verify-row:last-child { border-bottom: none; }
                .verify-row:hover { background: #fafbfc; }
                .verify-row--processing {
                    opacity: 0.5;
                    pointer-events: none;
                }
                .verify-cell {
                    padding: 16px;
                    vertical-align: middle;
                }
                .verify-cell--actions {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    justify-content: flex-end;
                }

                /* ── User ── */
                .user-info {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                .user-avatar {
                    width: 42px;
                    height: 42px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 15px;
                    font-weight: 700;
                    color: #fff;
                    flex-shrink: 0;
                    letter-spacing: 0.5px;
                }
                .user-name {
                    font-size: 14px;
                    font-weight: 700;
                    color: #1e293b;
                    margin: 0 0 2px;
                }
                .user-email {
                    font-size: 12px;
                    color: #94a3b8;
                    margin: 0;
                }

                /* ── Details ── */
                .detail-lines {
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                }
                .detail-line {
                    display: flex;
                    align-items: center;
                    gap: 5px;
                    font-size: 13px;
                    color: #475569;
                }
                .detail-icon {
                    color: #94a3b8;
                    flex-shrink: 0;
                }

                /* ── Documents ── */
                .docs-row {
                    display: flex;
                    gap: 8px;
                    align-items: center;
                    flex-wrap: wrap;
                }
                .doc-thumb {
                    position: relative;
                    width: 72px;
                    height: 52px;
                    border-radius: 8px;
                    overflow: hidden;
                    border: 1.5px solid #e2e8f0;
                    cursor: pointer;
                    background: #f8fafc;
                    transition: border-color 0.2s, transform 0.15s;
                    padding: 0;
                    flex-shrink: 0;
                }
                .doc-thumb:hover {
                    border-color: #0074d9;
                    transform: scale(1.04);
                }
                .doc-thumb:hover .doc-thumb-zoom {
                    opacity: 1;
                }
                .doc-thumb-img {
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    display: block;
                }
                .doc-thumb-badge {
                    position: absolute;
                    bottom: 3px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: rgba(0,0,0,0.62);
                    color: #fff;
                    font-size: 9px;
                    font-weight: 700;
                    padding: 1px 6px;
                    border-radius: 4px;
                    letter-spacing: 0.05em;
                    white-space: nowrap;
                }
                .doc-thumb-zoom {
                    position: absolute;
                    inset: 0;
                    background: rgba(0,116,217,0.18);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #fff;
                    opacity: 0;
                    transition: opacity 0.15s;
                }
                .doc-missing {
                    width: 72px;
                    height: 52px;
                    border-radius: 8px;
                    border: 1.5px dashed #fca5a5;
                    background: #fff5f5;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    gap: 2px;
                }
                .doc-missing-icon { color: #f87171; }
                .badge-missing {
                    font-size: 8px;
                    font-weight: 700;
                    color: #ef4444;
                    letter-spacing: 0.04em;
                }
                .badge-incomplete {
                    display: inline-block;
                    margin-top: 6px;
                    background: #fff1f0;
                    color: #f04438;
                    font-size: 10px;
                    font-weight: 700;
                    padding: 2px 8px;
                    border-radius: 99px;
                    letter-spacing: 0.04em;
                }

                /* ── Reason Select ── */
                .reason-select {
                    font-size: 13px;
                    color: #334155;
                    background: #f8fafc;
                    border: 1.5px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 7px 10px;
                    outline: none;
                    cursor: pointer;
                    min-width: 180px;
                    transition: border-color 0.2s;
                    -webkit-appearance: auto;
                }
                .reason-select:focus { border-color: #0074d9; }
                .reason-select:disabled { opacity: 0.5; cursor: not-allowed; }

                /* ── Action Buttons ── */
                .action-btn {
                    width: 38px;
                    height: 38px;
                    border-radius: 50%;
                    border: 2px solid transparent;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    transition: all 0.18s;
                    background: #fff;
                }
                .action-btn:disabled {
                    opacity: 0.35;
                    cursor: not-allowed;
                }
                .action-btn--reject {
                    border-color: #f97316;
                    color: #f97316;
                }
                .action-btn--reject:not(:disabled):hover {
                    background: #fff7ed;
                    border-color: #ea580c;
                    color: #ea580c;
                    transform: scale(1.08);
                }
                .action-btn--approve {
                    border-color: #22c55e;
                    color: #22c55e;
                    background: #22c55e;
                    color: #fff;
                }
                .action-btn--approve:not(:disabled):hover {
                    background: #16a34a;
                    border-color: #16a34a;
                    transform: scale(1.08);
                }

                /* ── Empty / Loading / Error States ── */
                .state-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 64px 24px;
                    color: #94a3b8;
                    text-align: center;
                    gap: 12px;
                }
                .state-icon {
                    width: 56px;
                    height: 56px;
                    border-radius: 50%;
                    background: #f1f5f9;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 4px;
                }
                .state-title {
                    font-size: 16px;
                    font-weight: 700;
                    color: #334155;
                    margin: 0;
                }
                .state-body {
                    font-size: 14px;
                    color: #94a3b8;
                    margin: 0;
                }

                /* ── Lightbox ── */
                .lightbox-overlay {
                    position: fixed;
                    inset: 0;
                    background: rgba(2,8,23,0.88);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 9999;
                    animation: fadeIn 0.18s ease;
                }
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                .lightbox-container {
                    position: relative;
                    max-width: 90vw;
                    max-height: 90vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    animation: scaleIn 0.2s cubic-bezier(.34,1.56,.64,1);
                }
                @keyframes scaleIn {
                    from { transform: scale(0.88); opacity: 0; }
                    to { transform: scale(1); opacity: 1; }
                }
                .lightbox-img {
                    max-width: 90vw;
                    max-height: 88vh;
                    border-radius: 12px;
                    box-shadow: 0 24px 80px rgba(0,0,0,0.6);
                    object-fit: contain;
                    display: block;
                }
                .lightbox-close {
                    position: absolute;
                    top: -16px;
                    right: -16px;
                    width: 36px;
                    height: 36px;
                    border-radius: 50%;
                    background: #fff;
                    border: none;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    color: #334155;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                    transition: transform 0.15s, background 0.15s;
                    z-index: 10000;
                }
                .lightbox-close:hover {
                    background: #f1f5f9;
                    transform: scale(1.1);
                }

                /* ── Footer ── */
                .verify-footer {
                    margin-top: 12px;
                    padding: 16px 24px;
                    border-top: 1px solid #f1f5f9;
                    font-size: 13px;
                    color: #94a3b8;
                }

                /* ── Skeleton loader ── */
                @keyframes shimmer {
                    0% { background-position: -600px 0; }
                    100% { background-position: 600px 0; }
                }
                .skeleton {
                    border-radius: 8px;
                    background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
                    background-size: 600px 100%;
                    animation: shimmer 1.4s infinite linear;
                }
            `}</style>

            {lightboxUrl && (
                <Lightbox url={lightboxUrl} onClose={() => setLightboxUrl(null)} />
            )}

            <div className="verify-page">
                <main className="verify-main">
                    {/* Header */}
                    <div className="verify-header">
                        <button className="back-btn" onClick={() => router.push('/admin')}>
                            <ArrowLeft size={16} /> Volver al Panel
                        </button>
                        <h1 className="verify-title">Verificación de Usuarios</h1>
                        <p className="verify-subtitle">
                            Revisa la documentación adjunta para aprobar o rechazar nuevas cuentas. Asegúrate
                            de que las identificaciones sean legibles y coincidan con los datos del perfil.
                        </p>
                    </div>

                    {/* Card */}
                    <div className="verify-card">
                        <div className="verify-card-header">
                            <span style={{ fontWeight: 700, fontSize: 15, color: '#1e293b' }}>
                                Solicitudes Pendientes
                            </span>
                            <span className="pending-badge">
                                <span className="pending-dot" />
                                {loading ? '…' : items.length} pendiente{items.length !== 1 ? 's' : ''}
                            </span>
                        </div>

                        {loading ? (
                            <div className="state-container">
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 12, width: '100%', padding: '0 24px' }}>
                                    {[1, 2, 3].map((i) => (
                                        <div key={i} className="skeleton" style={{ height: 72 }} />
                                    ))}
                                </div>
                            </div>
                        ) : error ? (
                            <div className="state-container">
                                <div className="state-icon">
                                    <XCircle size={28} style={{ color: '#ef4444' }} />
                                </div>
                                <p className="state-title">Error al cargar</p>
                                <p className="state-body">{error}</p>
                            </div>
                        ) : items.length === 0 ? (
                            <div className="state-container">
                                <div className="state-icon">
                                    <UserCircle2 size={28} style={{ color: '#94a3b8' }} />
                                </div>
                                <p className="state-title">Todo al día</p>
                                <p className="state-body">No hay solicitudes de verificación pendientes en este momento.</p>
                            </div>
                        ) : (
                            <div className="verify-table-wrap">
                                <table className="verify-table">
                                    <thead>
                                        <tr>
                                            <th>Usuario</th>
                                            <th>Detalles de Registro</th>
                                            <th>Documentación Adjunta</th>
                                            <th>Motivo de Rechazo</th>
                                            <th style={{ textAlign: 'right' }}>Acciones</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {items.map((item) => (
                                            <VerificationRow
                                                key={item.request_id}
                                                item={item}
                                                onApprove={handleApprove}
                                                onReject={handleReject}
                                                onOpenLightbox={setLightboxUrl}
                                            />
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}

                        {!loading && items.length > 0 && (
                            <div className="verify-footer">
                                Mostrando {items.length} solicitud{items.length !== 1 ? 'es' : ''} pendiente{items.length !== 1 ? 's' : ''}
                            </div>
                        )}
                    </div>
                </main>
            </div>
        </>
    );
}

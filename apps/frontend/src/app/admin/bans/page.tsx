'use client'

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { AlertCircle, CheckCircle, Shield, ShieldAlert, UserX, UserCheck, Search, Loader2 } from 'lucide-react';
import { adminAPI, UserAdminRead, UserReportItem } from '@/lib/api';
import Link from 'next/link';

export default function BansDashboard() {
    const router = useRouter();
    const [users, setUsers] = useState<UserAdminRead[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    
    // Search and filters
    const [search, setSearch] = useState('');
    const [roleFilter, setRoleFilter] = useState<string>('');
    const [statusFilter, setStatusFilter] = useState<string>('');
    
    // Pagination
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [totalUsers, setTotalUsers] = useState(0);

    // Action status states
    const [actionUser, setActionUser] = useState<string | null>(null);
    const [actionLoading, setActionLoading] = useState(false);

    // User reports collapsible states
    const [expandedUser, setExpandedUser] = useState<string | null>(null);
    const [userReports, setUserReports] = useState<Record<string, UserReportItem[]>>({});
    const [reportsLoading, setReportsLoading] = useState(false);
    const [reportActionLoading, setReportActionLoading] = useState<string | null>(null);

    const fetchUsers = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            
            const params: any = {
                page,
                page_size: 15,
            };
            if (search.trim()) params.search = search.trim();
            if (roleFilter) params.role = roleFilter;
            if (statusFilter === 'active') params.is_active = true;
            if (statusFilter === 'banned') params.is_active = false;

            const response = await adminAPI.getUsersList(params);
            
            setUsers(response.items);
            setTotalPages(response.pages);
            setTotalUsers(response.total);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Error fetching users list');
        } finally {
            setLoading(false);
        }
    }, [page, search, roleFilter, statusFilter]);

    useEffect(() => {
        if (!localStorage.getItem('access_token')) {
            router.replace('/login');
            return;
        }
        fetchUsers();
    }, [fetchUsers, router]);

    // Handle Search Submit
    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        setPage(1);
        fetchUsers();
    };

    // Quick Action Handlers
    const handleBan = async (userId: string, userName: string) => {
        if (!confirm(`¿Estás seguro de que deseas suspender/banear al usuario ${userName}?`)) return;
        
        setActionUser(userId);
        setActionLoading(true);
        setError(null);
        setSuccessMessage(null);

        try {
            await adminAPI.banUser(userId);
            setSuccessMessage(`Usuario ${userName} suspendido exitosamente.`);
            fetchUsers();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Error al suspender usuario');
        } finally {
            setActionUser(null);
            setActionLoading(false);
        }
    };

    const handleUnban = async (userId: string, userName: string) => {
        setActionUser(userId);
        setActionLoading(true);
        setError(null);
        setSuccessMessage(null);

        try {
            await adminAPI.unbanUser(userId);
            setSuccessMessage(`Usuario ${userName} activado y sus strikes fueron reseteados.`);
            fetchUsers();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Error al activar usuario');
        } finally {
            setActionUser(null);
            setActionLoading(false);
        }
    };

    const toggleUserExpanded = async (userId: string) => {
        if (expandedUser === userId) {
            setExpandedUser(null);
            return;
        }

        setExpandedUser(userId);
        
        // Fetch reports if not already loaded
        if (!userReports[userId]) {
            await fetchUserReports(userId);
        }
    };

    const fetchUserReports = async (userId: string) => {
        try {
            setReportsLoading(true);
            const res = await adminAPI.getUserReports(userId);
            setUserReports(prev => ({ ...prev, [userId]: res.items }));
        } catch (err) {
            console.error("Error loading user reports", err);
        } finally {
            setReportsLoading(false);
        }
    };

    const handleReportDecision = async (
        userId: string,
        commentId: string,
        reportId: string,
        decision: 'allow' | 'remove'
    ) => {
        if (decision === 'remove' && !confirm('¿Estás seguro de confirmar la denuncia? Esto removerá el comentario y le sumará 1 strike al usuario.')) return;
        
        setReportActionLoading(reportId);
        setError(null);
        setSuccessMessage(null);

        try {
            await adminAPI.submitDecision(commentId, {
                comment_id: commentId,
                decision,
                reason: decision === 'remove' ? 'Denuncia confirmada por el administrador' : 'Denuncia desestimada por el administrador',
            });

            setSuccessMessage(
                decision === 'remove'
                    ? 'Denuncia confirmada. El comentario ha sido removido y se ha aplicado un strike al usuario.'
                    : 'Denuncia desestimada. El comentario ha sido aprobado/mantenido.'
            );

            // Reload user reports for this specific user
            await fetchUserReports(userId);
            
            // Reload user list to show updated strike counts and active status
            fetchUsers();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Error al procesar la decisión sobre el reporte');
        } finally {
            setReportActionLoading(null);
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 p-8">
            <div className="max-w-6xl mx-auto">
                
                {/* Navigation and Back button */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                            <Link href="/admin" className="hover:text-sky-600 transition-colors">Admin Panel</Link>
                            <span>/</span>
                            <span className="text-slate-500">Gestión de Baneos</span>
                        </div>
                        <h1 className="text-3xl font-black text-slate-900">Gestión de Baneos y Strikes</h1>
                        <p className="text-slate-600 mt-1">Administra cuentas de alumnos, strikes acumulados y suspende/habilita usuarios manualmente.</p>
                    </div>
                </div>

                {/* Info / Success Alerts */}
                {successMessage && (
                    <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-2xl flex items-center gap-3 text-green-700 font-bold text-sm">
                        <CheckCircle className="w-5 h-5 shrink-0" />
                        <p>{successMessage}</p>
                    </div>
                )}

                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-2xl flex items-center gap-3 text-red-700 font-bold text-sm">
                        <AlertCircle className="w-5 h-5 shrink-0" />
                        <p>{error}</p>
                    </div>
                )}

                {/* Filters Row */}
                <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm mb-6 flex flex-col md:flex-row gap-4 items-stretch md:items-center justify-between">
                    <form onSubmit={handleSearch} className="relative flex-1 max-w-md flex items-center bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 focus-within:border-sky-400 focus-within:bg-white transition-all">
                        <Search className="w-4 h-4 text-slate-400 mr-2 shrink-0" />
                        <input
                            type="text"
                            placeholder="Buscar por nombre, email o username..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="w-full bg-transparent text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none"
                        />
                        <button type="submit" className="hidden" />
                    </form>

                    <div className="flex flex-wrap gap-3">
                        <select
                            value={roleFilter}
                            onChange={(e) => { setRoleFilter(e.target.value); setPage(1); }}
                            className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-bold text-slate-700 focus:outline-none focus:border-sky-400 cursor-pointer shadow-sm"
                        >
                            <option value="">Todos los roles</option>
                            <option value="student">Estudiantes</option>
                            <option value="admin">Administradores</option>
                        </select>

                        <select
                            value={statusFilter}
                            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
                            className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-bold text-slate-700 focus:outline-none focus:border-sky-400 cursor-pointer shadow-sm"
                        >
                            <option value="">Todos los estados</option>
                            <option value="active">Activos</option>
                            <option value="banned">Suspendidos</option>
                        </select>

                        <button
                            onClick={() => {
                                setSearch('');
                                setRoleFilter('');
                                setStatusFilter('');
                                setPage(1);
                            }}
                            className="px-4 py-2 border border-slate-200 hover:bg-slate-50 rounded-xl text-xs font-bold text-slate-600 transition-colors shadow-sm cursor-pointer"
                        >
                            Limpiar
                        </button>
                    </div>
                </div>

                {/* Table / List */}
                <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                    {loading && users.length === 0 ? (
                        <div className="p-20 flex flex-col items-center gap-3">
                            <Loader2 className="w-8 h-8 animate-spin text-[#ff8a00]" />
                            <p className="text-slate-500 font-bold text-sm">Buscando usuarios...</p>
                        </div>
                    ) : users.length === 0 ? (
                        <div className="p-20 text-center text-slate-400 font-bold text-sm">
                            No se encontraron usuarios con los criterios de búsqueda.
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse text-xs">
                                <thead>
                                    <tr className="bg-slate-50/75 border-b border-slate-100 font-black text-slate-500 uppercase tracking-wider">
                                        <th className="px-6 py-4">Usuario</th>
                                        <th className="px-6 py-4">Rol</th>
                                        <th className="px-6 py-4">Strikes</th>
                                        <th className="px-6 py-4">Estado</th>
                                        <th className="px-6 py-4">F. Registro</th>
                                        <th className="px-6 py-4 text-right">Acciones</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100 font-medium">
                                    {users.map((user) => {
                                        const isCurrentUserAction = actionUser === user.id && actionLoading;
                                        const isExpanded = expandedUser === user.id;
                                        return (
                                            <>
                                                <tr key={user.id} className="hover:bg-slate-50/50 transition-colors">
                                                    <td className="px-6 py-4">
                                                        <div className="font-bold text-slate-900">{user.full_name}</div>
                                                        <div className="text-slate-400 mt-0.5 font-mono">{user.email}</div>
                                                        <div className="text-[10px] text-slate-400 mt-0.5">@{user.username}</div>
                                                    </td>
                                                    <td className="px-6 py-4 capitalize font-semibold text-slate-600">
                                                        {user.role === 'admin' ? (
                                                            <span className="flex items-center gap-1 text-red-700">
                                                                <Shield className="w-3.5 h-3.5" /> Admin
                                                            </span>
                                                        ) : (
                                                            'Estudiante'
                                                        )}
                                                    </td>
                                                    <td className="px-6 py-4">
                                                        <span className={`px-2 py-0.5 rounded-md font-bold text-[10px] ${
                                                            user.strike_count >= 3
                                                                ? 'bg-red-50 text-red-700 border border-red-200'
                                                                : user.strike_count > 0
                                                                ? 'bg-amber-50 text-amber-700 border border-amber-200'
                                                                : 'bg-slate-50 text-slate-400'
                                                        }`}>
                                                            {user.strike_count} / 3
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4">
                                                        {user.is_active ? (
                                                            <span className="inline-flex items-center gap-1 text-green-700 bg-green-50 px-2.5 py-0.5 rounded-full border border-green-200 font-bold text-[10px]">
                                                                Activo
                                                            </span>
                                                        ) : (
                                                            <span className="inline-flex items-center gap-1 text-red-700 bg-red-50 px-2.5 py-0.5 rounded-full border border-red-200 font-bold text-[10px]">
                                                                <ShieldAlert className="w-3 h-3" /> Suspendido
                                                            </span>
                                                        )}
                                                    </td>
                                                    <td className="px-6 py-4 text-slate-500 font-semibold">
                                                        {new Date(user.created_at).toLocaleDateString('es-PE')}
                                                    </td>
                                                    <td className="px-6 py-4 text-right">
                                                        <div className="flex items-center justify-end gap-2">
                                                            <button
                                                                onClick={() => toggleUserExpanded(user.id)}
                                                                className={`px-2.5 py-1.5 text-xs font-bold rounded-lg transition-colors border flex items-center gap-1 cursor-pointer ${
                                                                    isExpanded
                                                                        ? 'bg-slate-200 text-slate-800 border-slate-300'
                                                                        : 'bg-slate-50 text-slate-700 hover:bg-slate-100 border-slate-200'
                                                                }`}
                                                            >
                                                                Ver Reportes {isExpanded ? '▲' : '▼'}
                                                            </button>
                                                            {user.is_active ? (
                                                                <button
                                                                    onClick={() => handleBan(user.id, user.full_name)}
                                                                    disabled={isCurrentUserAction || user.role === 'admin'}
                                                                    className="px-2.5 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 font-bold rounded-lg transition-colors border border-red-100 flex items-center gap-1 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                                                                    title={user.role === 'admin' ? 'No se puede suspender a un administrador' : 'Suspender cuenta'}
                                                                >
                                                                    <UserX className="w-3.5 h-3.5" /> Suspender
                                                                </button>
                                                            ) : (
                                                                <button
                                                                    onClick={() => handleUnban(user.id, user.full_name)}
                                                                    disabled={isCurrentUserAction}
                                                                    className="px-2.5 py-1.5 bg-green-50 hover:bg-green-100 text-green-700 font-bold rounded-lg transition-colors border border-green-100 flex items-center gap-1 cursor-pointer disabled:opacity-50"
                                                                    title="Activar cuenta y resetear strikes"
                                                                >
                                                                    <UserCheck className="w-3.5 h-3.5" /> Reactivar
                                                                </button>
                                                            )}
                                                        </div>
                                                    </td>
                                                </tr>
                                                {isExpanded && (
                                                    <tr className="bg-slate-50/50">
                                                        <td colSpan={6} className="px-6 py-4 border-t border-b border-slate-150">
                                                            <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-inner">
                                                                <h4 className="text-xs font-black text-slate-800 uppercase tracking-wider mb-3">
                                                                    Denuncias Recibidas en sus Comentarios
                                                                </h4>
                                                                {reportsLoading ? (
                                                                    <div className="py-6 flex items-center justify-center gap-2 text-slate-400 font-semibold">
                                                                        <Loader2 className="w-4 h-4 animate-spin text-[#ff8a00]" /> Cargando reportes...
                                                                    </div>
                                                                ) : !userReports[user.id] || userReports[user.id].length === 0 ? (
                                                                    <div className="py-4 text-center text-slate-400 font-bold">
                                                                        Este usuario no registra denuncias en sus comentarios.
                                                                    </div>
                                                                ) : (
                                                                    <div className="space-y-3">
                                                                        {userReports[user.id].map((report) => {
                                                                            const isResolved = report.status === 'resolved_offensive' || report.status === 'resolved_safe';
                                                                            return (
                                                                                <div key={report.id} className="p-3.5 bg-slate-50 rounded-lg border border-slate-200 flex flex-col gap-2 text-left">
                                                                                    <div className="flex items-center justify-between">
                                                                                        <div className="flex items-center gap-2">
                                                                                            <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded text-[9px] font-black uppercase tracking-wide border border-red-200">
                                                                                                Motivo: {report.reason}
                                                                                            </span>
                                                                                            {report.status === 'resolved_offensive' ? (
                                                                                                <span className="px-2 py-0.5 bg-red-50 text-red-700 border border-red-250 rounded text-[9px] font-black uppercase tracking-wide">
                                                                                                    Denuncia Confirmada (Strike)
                                                                                                </span>
                                                                                            ) : report.status === 'resolved_safe' ? (
                                                                                                <span className="px-2 py-0.5 bg-green-50 text-green-700 border border-green-250 rounded text-[9px] font-black uppercase tracking-wide">
                                                                                                    Denuncia Desestimada
                                                                                                </span>
                                                                                            ) : (
                                                                                                <span className="px-2 py-0.5 bg-amber-50 text-amber-700 border border-amber-250 rounded text-[9px] font-black uppercase tracking-wide">
                                                                                                    Pendiente
                                                                                                </span>
                                                                                            )}
                                                                                        </div>
                                                                                        <span className="text-[10px] text-slate-400 font-semibold">
                                                                                            {new Date(report.created_at).toLocaleDateString('es-PE', {
                                                                                                year: 'numeric',
                                                                                                month: 'short',
                                                                                                day: 'numeric',
                                                                                                hour: '2-digit',
                                                                                                minute: '2-digit'
                                                                                            })}
                                                                                        </span>
                                                                                    </div>
                                                                                    <div className="text-[11px] text-slate-700 leading-relaxed bg-white p-2.5 rounded border border-slate-200">
                                                                                        <strong className="text-[10px] text-slate-400 uppercase block mb-1">Comentario:</strong>
                                                                                        {report.comment_content}
                                                                                    </div>
                                                                                    {report.description && (
                                                                                        <div className="text-[11px] text-slate-600 bg-slate-100/50 p-2 rounded border border-slate-250">
                                                                                            <strong>Detalles del reporte:</strong> {report.description}
                                                                                        </div>
                                                                                    )}
                                                                                    {!isResolved && (
                                                                                        <div className="flex items-center gap-2 mt-2 self-end">
                                                                                            <button
                                                                                                onClick={() => handleReportDecision(user.id, report.comment_id, report.id, 'remove')}
                                                                                                disabled={!!reportActionLoading}
                                                                                                className="px-2.5 py-1.5 bg-red-100 hover:bg-red-200 text-red-700 font-bold rounded text-[10px] transition-colors border border-red-200 flex items-center gap-1 cursor-pointer disabled:opacity-50"
                                                                                            >
                                                                                                {reportActionLoading === report.id ? (
                                                                                                    <Loader2 className="w-3 h-3 animate-spin" />
                                                                                                ) : null}
                                                                                                Confirmar (Añadir Strike)
                                                                                            </button>
                                                                                            <button
                                                                                                onClick={() => handleReportDecision(user.id, report.comment_id, report.id, 'allow')}
                                                                                                disabled={!!reportActionLoading}
                                                                                                className="px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded text-[10px] transition-colors border border-slate-200 flex items-center gap-1 cursor-pointer disabled:opacity-50"
                                                                                            >
                                                                                                {reportActionLoading === report.id ? (
                                                                                                    <Loader2 className="w-3 h-3 animate-spin" />
                                                                                                ) : null}
                                                                                                Desestimar
                                                                                            </button>
                                                                                        </div>
                                                                                    )}
                                                                                </div>
                                                                            );
                                                                        })}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </td>
                                                    </tr>
                                                )}
                                            </>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                {/* Pagination */}
                {!loading && totalPages > 1 && (
                    <div className="mt-8 flex items-center justify-between">
                        <button
                            onClick={() => setPage(Math.max(1, page - 1))}
                            disabled={page === 1}
                            className="px-4 py-2 bg-white border border-slate-200 rounded-xl font-bold text-xs hover:bg-slate-50 disabled:opacity-50 cursor-pointer"
                        >
                            ← Anterior
                        </button>
                        <p className="text-xs text-slate-500 font-bold">
                            Página {page} de {totalPages} ({totalUsers} usuarios)
                        </p>
                        <button
                            onClick={() => setPage(Math.min(totalPages, page + 1))}
                            disabled={page === totalPages}
                            className="px-4 py-2 bg-white border border-slate-200 rounded-xl font-bold text-xs hover:bg-slate-50 disabled:opacity-50 cursor-pointer"
                        >
                            Siguiente →
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

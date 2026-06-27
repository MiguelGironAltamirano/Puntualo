import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.modules.admin.schemas import (
    AdminStatsResponse,
    PendingProfessorsResponse,
    PendingVerificationsResponse,
    RejectVerificationRequest,
)
from app.modules.admin.service import (
    approve_professor,
    approve_verification,
    get_admin_stats,
    get_pending_professors,
    get_pending_verifications,
    reject_professor,
    reject_verification,
)
from app.modules.auth.dependencies import get_current_user

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependencia que verifica que el usuario autenticado sea admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a administradores",
        )
    return current_user


@router.get(
    "/stats",
    response_model=AdminStatsResponse,
    summary="Estadísticas del panel de administración",
)
def admin_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> AdminStatsResponse:
    return get_admin_stats(db)


# ── Verification endpoints ─────────────────────────────────────────────────────

@router.get(
    "/users/verifications/pending",
    response_model=PendingVerificationsResponse,
    summary="Lista de solicitudes de verificación pendientes",
)
def list_pending_verifications(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> PendingVerificationsResponse:
    return get_pending_verifications(db)


@router.post(
    "/users/verifications/{request_id}/approve",
    summary="Aprobar solicitud de verificación",
)
def approve_verification_endpoint(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    return approve_verification(db, request_id)


@router.post(
    "/users/verifications/{request_id}/reject",
    summary="Rechazar solicitud de verificación",
)
def reject_verification_endpoint(
    request_id: uuid.UUID,
    body: RejectVerificationRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    return reject_verification(db, request_id, body.reason)


# ── Professor validation endpoints ────────────────────────────────────────────

@router.get(
    "/teachers/validations/pending",
    response_model=PendingProfessorsResponse,
    summary="Lista de profesores pendientes de validación manual",
)
def list_pending_professors(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> PendingProfessorsResponse:
    return get_pending_professors(db)


@router.post(
    "/teachers/validations/{professor_id}/approve",
    summary="Aprobar manualmente un profesor",
)
def approve_professor_endpoint(
    professor_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    return approve_professor(db, professor_id)


@router.post(
    "/teachers/validations/{professor_id}/reject",
    summary="Rechazar manualmente un profesor",
)
def reject_professor_endpoint(
    professor_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict:
    return reject_professor(db, professor_id)

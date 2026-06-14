import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.career import Career
from app.models.professor import Professor
from app.models.uploaded_document import UploadedDocument
from app.models.user import User
from app.models.verification_request import VerificationRequest
from app.modules.admin.schemas import (
    DocumentInfo,
    PendingVerificationItem,
    PendingVerificationsResponse,
)


def get_admin_stats(db: Session) -> dict:
    """Retorna los conteos de entidades pendientes de revisión."""

    # Usuarios estudiantes que aún no han sido verificados por el admin
    users_pending: int = db.execute(
        select(func.count()).select_from(User).where(
            User.is_verified == False,  # noqa: E712
            User.role == "student",
            User.is_active == True,  # noqa: E712
        )
    ).scalar_one()

    # Profesores cuya validación no fue encontrada en el sistema externo
    professors_pending: int = db.execute(
        select(func.count()).select_from(Professor).where(
            Professor.validation_status == "not_found",
            Professor.is_active == True,  # noqa: E712
        )
    ).scalar_one()

    return {
        "users_pending": users_pending,
        "professors_pending": professors_pending,
    }


# ── Verification admin services ────────────────────────────────────────────────

def get_pending_verifications(db: Session) -> PendingVerificationsResponse:
    """Devuelve todas las solicitudes con status='pending', enriquecidas con
    datos del usuario, su carrera y los documentos adjuntos."""

    # 1. Obtener todas las solicitudes pendientes
    rows = db.execute(
        select(VerificationRequest)
        .where(VerificationRequest.status == "pending")
        .order_by(VerificationRequest.created_at.asc())
    ).scalars().all()

    items: list[PendingVerificationItem] = []

    for req in rows:
        # 2. Datos del usuario
        user: User | None = db.get(User, req.user_id)
        if not user:
            continue

        # 3. Carrera
        career_name: str | None = None
        if user.career_id is not None:
            career: Career | None = db.get(Career, user.career_id)
            if career:
                career_name = career.name

        # 4. Documentos de tipo carnet asociados al usuario
        docs = db.execute(
            select(UploadedDocument)
            .where(
                UploadedDocument.user_id == req.user_id,
                UploadedDocument.document_type == "carnet",
            )
            .order_by(UploadedDocument.created_at.asc())
        ).scalars().all()

        doc_infos = [
            DocumentInfo(
                id=d.id,
                side=d.side,
                file_path=d.file_path,
                mime_type=d.mime_type,
            )
            for d in docs
        ]

        items.append(
            PendingVerificationItem(
                request_id=req.id,
                user_id=user.id,
                full_name=user.full_name,
                email=user.email,
                username=user.username,
                dni=user.dni,
                career_name=career_name,
                documents=doc_infos,
                submitted_at=req.created_at,
            )
        )

    return PendingVerificationsResponse(total=len(items), items=items)


def approve_verification(db: Session, request_id: uuid.UUID) -> dict:
    """Aprueba la solicitud: status → 'approved', user.is_verified → True."""

    req: VerificationRequest | None = db.get(VerificationRequest, request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud de verificación no encontrada",
        )
    if req.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud ya fue procesada",
        )

    req.status = "approved"
    req.reviewed_at = datetime.now(timezone.utc)

    user: User | None = db.get(User, req.user_id)
    if user:
        user.is_verified = True

    db.commit()
    return {"detail": "Verificación aprobada"}


def reject_verification(
    db: Session, request_id: uuid.UUID, reason: str
) -> dict:
    """Rechaza la solicitud: status → 'rejected', guarda el motivo."""

    req: VerificationRequest | None = db.get(VerificationRequest, request_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud de verificación no encontrada",
        )
    if req.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud ya fue procesada",
        )

    req.status = "rejected"
    req.rejection_reason = reason
    req.reviewed_at = datetime.now(timezone.utc)

    db.commit()
    return {"detail": "Verificación rechazada"}

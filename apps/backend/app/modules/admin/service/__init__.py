"""Admin service module."""
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.career import Career
from app.models.faculty import Faculty
from app.models.professor import Professor
from app.models.professor_evidence import ProfessorEvidence
from app.models.university import University
from app.models.uploaded_document import UploadedDocument
from app.models.user import User
from app.models.verification_request import VerificationRequest
from app.modules.admin.schemas import (
    DocumentInfo,
    EvidenceInfo,
    PendingProfessorItem,
    PendingProfessorsResponse,
    PendingVerificationItem,
    PendingVerificationsResponse,
)


def get_admin_stats(db: Session) -> dict:
    # Debe medir lo mismo que get_pending_verifications: solicitudes por revisar,
    # no usuarios sin verificar (un usuario sin carnet enviado no es accionable).
    users_pending: int = db.execute(
        select(func.count()).select_from(VerificationRequest).where(
            VerificationRequest.status == "pending",
        )
    ).scalar_one()

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
    rows = db.execute(
        select(VerificationRequest)
        .where(VerificationRequest.status == "pending")
        .order_by(VerificationRequest.created_at.asc())
    ).scalars().all()

    items: list[PendingVerificationItem] = []

    for req in rows:
        user: User | None = db.get(User, req.user_id)
        if not user:
            continue

        career_name: str | None = None
        if user.career_id is not None:
            career: Career | None = db.get(Career, user.career_id)
            if career:
                career_name = career.name

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


def reject_verification(db: Session, request_id: uuid.UUID, reason: str) -> dict:
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


# ── Professor validation admin services ────────────────────────────────────────

def get_pending_professors(db: Session) -> PendingProfessorsResponse:
    rows = db.execute(
        select(Professor)
        .where(
            Professor.validation_status == "not_found",
            Professor.is_active == True,  # noqa: E712
        )
        .order_by(Professor.created_at.asc())
    ).scalars().all()

    items: list[PendingProfessorItem] = []

    for prof in rows:
        university: University | None = db.get(University, prof.university_id)
        university_name = university.name if university else "—"

        faculty: Faculty | None = db.get(Faculty, prof.faculty_id)
        faculty_name = faculty.name if faculty else "—"

        evidence_rows = db.execute(
            select(ProfessorEvidence)
            .where(ProfessorEvidence.professor_id == prof.id)
            .order_by(ProfessorEvidence.fetched_at.desc())
        ).scalars().all()

        evidence = [
            EvidenceInfo(
                source=e.source,
                role=e.role,
                found=e.found,
                affiliation_confirmed=e.affiliation_confirmed,
                confidence=float(e.confidence) if e.confidence is not None else None,
            )
            for e in evidence_rows
        ]

        items.append(
            PendingProfessorItem(
                professor_id=prof.id,
                full_name=prof.full_name,
                university_name=university_name,
                faculty_name=faculty_name,
                validation_status=prof.validation_status,
                global_score=float(prof.global_score) if prof.global_score is not None else None,
                total_evaluations=prof.total_evaluations,
                registered_at=prof.created_at,
                evidence=evidence,
            )
        )

    return PendingProfessorsResponse(total=len(items), items=items)


def approve_professor(db: Session, professor_id: uuid.UUID) -> dict:
    prof: Professor | None = db.get(Professor, professor_id)
    if not prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profesor no encontrado",
        )
    if prof.validation_status not in ("not_found", "pending_validation"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El profesor ya fue procesado",
        )

    prof.validation_status = "validated"
    db.commit()
    return {"detail": "Profesor validado correctamente"}


def reject_professor(db: Session, professor_id: uuid.UUID) -> dict:
    prof: Professor | None = db.get(Professor, professor_id)
    if not prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profesor no encontrado",
        )
    if prof.validation_status not in ("not_found", "pending_validation"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El profesor ya fue procesado",
        )

    prof.validation_status = "rejected"
    db.commit()
    return {"detail": "Profesor rechazado"}

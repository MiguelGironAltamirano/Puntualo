import logging
import uuid
from datetime import datetime, timezone
from io import BytesIO

from fastapi import HTTPException, status
from PIL import Image, ImageFilter, ImageStat
from sqlalchemy import select
from sqlalchemy.orm import Session
from supabase import create_client

from app.core.config import settings
from app.models.uploaded_document import UploadedDocument
from app.models.user import User
from app.models.verification_request import VerificationRequest


_ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}


def _get_supabase_client():
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise HTTPException(
            status_code=500,
            detail="Supabase no esta configurado",
        )
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def _validate_image_quality(file_bytes: bytes, content_type: str) -> dict:
    if content_type not in _ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no permitido",
        )

    if len(file_bytes) > settings.VERIFICATION_MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La imagen supera el tamano permitido",
        )

    try:
        image = Image.open(BytesIO(file_bytes))
        image.load()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo leer la imagen",
        ) from exc

    if image.format not in {"JPEG", "PNG"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de imagen no permitido",
        )

    width, height = image.size
    if width < settings.VERIFICATION_MIN_WIDTH or height < settings.VERIFICATION_MIN_HEIGHT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resolucion demasiado baja",
        )

    gray = image.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    variance = ImageStat.Stat(edges).var[0]

    if variance < settings.VERIFICATION_MIN_SHARPNESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La imagen esta borrosa",
        )

    return {
        "width": width,
        "height": height,
        "quality_score": float(variance),
    }


def _get_or_create_request(db: Session, user_id: uuid.UUID) -> VerificationRequest:
    existing = db.execute(
        select(VerificationRequest)
        .where(VerificationRequest.user_id == user_id)
        .order_by(VerificationRequest.created_at.desc())
    ).scalars().first()

    if existing and existing.status == "pending":
        return existing

    request = VerificationRequest(user_id=user_id, status="pending")
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def _store_document(
    db: Session,
    user: User,
    side: str,
    content_type: str,
    file_bytes: bytes,
    width: int,
    height: int,
    quality_score: float,
) -> UploadedDocument:
    if not settings.SUPABASE_BUCKET_NAME:
        raise HTTPException(
            status_code=500,
            detail="Bucket de Supabase no configurado",
        )

    file_ext = "png" if content_type == "image/png" else "jpg"
    object_key = f"verification/{user.id}/{side}/{uuid.uuid4().hex}.{file_ext}"
    public_url = (
        f"{settings.SUPABASE_URL}/storage/v1/object/public/"
        f"{settings.SUPABASE_BUCKET_NAME}/{object_key}"
    )

    logger = logging.getLogger(__name__)
    supabase = _get_supabase_client()
    logger.info(
        "Uploading verification document user=%s side=%s key=%s size=%d",
        user.id,
        side,
        object_key,
        len(file_bytes),
    )

    try:
        response = supabase.storage.from_(settings.SUPABASE_BUCKET_NAME).upload(
            object_key,
            file_bytes,
            file_options={"content-type": content_type, "upsert": "true"},
        )
    except Exception as exc:
        logger.exception("Supabase upload failed")
        raise HTTPException(
            status_code=500,
            detail="No se pudo subir la imagen",
        ) from exc

    error = None
    if isinstance(response, dict):
        error = response.get("error")
    else:
        error = getattr(response, "error", None)

    if error:
        logger.warning("Supabase returned error: %s", error)
        raise HTTPException(
            status_code=500,
            detail="No se pudo subir la imagen",
        )

    document = UploadedDocument(
        user_id=user.id,
        document_type="carnet",
        side=side,
        file_path=public_url,
        mime_type=content_type,
        file_size_bytes=len(file_bytes),
        width_px=width,
        height_px=height,
        quality_score=quality_score,
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def _has_both_sides(db: Session, user_id: uuid.UUID) -> bool:
    rows = db.execute(
        select(UploadedDocument.side)
        .where(
            UploadedDocument.user_id == user_id,
            UploadedDocument.document_type == "carnet",
            UploadedDocument.side.in_(["front", "back"]),
        )
    ).scalars().all()

    return {side for side in rows if side} >= {"front", "back"}


def upload_carnet_side(
    db: Session,
    user: User,
    side: str,
    content_type: str,
    file_bytes: bytes,
) -> dict:
    if side not in {"front", "back"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lado de carnet invalido",
        )

    if user.is_verified and _has_both_sides(db, user.id):
        return {
            "detail": "El usuario ya esta verificado",
            "side": side,
            "is_verified": True,
            "request_status": "approved",
        }

    metrics = _validate_image_quality(file_bytes, content_type)
    _get_or_create_request(db, user.id)
    _store_document(
        db,
        user,
        side,
        content_type,
        file_bytes,
        metrics["width"],
        metrics["height"],
        metrics["quality_score"],
    )

    request_status = "pending"

    # Notificamos que la solicitud esta lista para revision (ambos lados subidos)
    # pero NO la aprobamos automaticamente, ya que requiere revision manual (1 dia habil).
    if _has_both_sides(db, user.id):
        # Opcional: aqui podriamos emitir un evento, enviar un email a admins, etc.
        pass

    return {
        "detail": "Imagen subida correctamente",
        "side": side,
        "is_verified": user.is_verified,
        "request_status": request_status,
    }

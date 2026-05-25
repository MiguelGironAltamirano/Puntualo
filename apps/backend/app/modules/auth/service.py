from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import logging
import secrets

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.core.security import create_refresh_token
from app.core.security import hash_password
from app.core.security import verify_password
from app.models.career import Career
from app.models.email_verification import EmailVerification
from app.models.password_reset import PasswordReset
from app.models.user import User
from app.modules.auth.schemas import LoginRequest
from app.modules.auth.schemas import RegisterRequest
from app.modules.auth.schemas import RegisterVerifyRequest
from app.modules.auth.schemas import PasswordResetConfirmRequest
from app.modules.auth.schemas import PasswordResetStartRequest
from app.modules.auth.schemas import PasswordResetVerifyRequest
from app.utils.email import send_email

logger = logging.getLogger(__name__)


def get_user_by_email(
    db: Session,
    email: str
) -> User | None:

    statement = select(User).where(
        User.email == email
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


def generate_tokens(
    user: User
) -> dict:

    token_data = {
        "sub": user.email,
        "role": user.role
    }

    access_token = create_access_token(
        token_data
    )

    refresh_token = create_refresh_token(
        token_data
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def _generate_verification_code() -> str:

    return f"{secrets.randbelow(1000000):06d}"


def _hash_verification_code(
    code: str,
    email: str
) -> str:

    secret = settings.SECRET_KEY or settings.JWT_SECRET
    if not secret:
        raise RuntimeError("SECRET_KEY no configurado")

    value = f"{email.lower()}:{code}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), value, hashlib.sha256).hexdigest()


def _get_pending_by_email(
    db: Session,
    email: str
) -> EmailVerification | None:

    statement = select(EmailVerification).where(EmailVerification.email == email)
    return db.execute(statement).scalar_one_or_none()


def _get_password_reset_by_email(
    db: Session,
    email: str
) -> PasswordReset | None:

    statement = select(PasswordReset).where(PasswordReset.email == email)
    return db.execute(statement).scalar_one_or_none()


def start_registration(
    db: Session,
    payload: RegisterRequest
) -> dict:

    existing_user = get_user_by_email(
        db,
        payload.email
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )

    existing_username = db.execute(
        select(User).where(User.username == payload.username)
    ).scalar_one_or_none()

    if existing_username:

        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario ya está en uso"
        )

    if payload.dni:
        existing_dni = db.execute(
            select(User).where(User.dni == payload.dni)
        ).scalar_one_or_none()
        
        if existing_dni:
            raise HTTPException(
                status_code=400,
                detail="El DNI ya está registrado"
            )

    if payload.career_id is not None:
        career = db.get(Career, payload.career_id)
        if career is None:
            raise HTTPException(
                status_code=400,
                detail="La carrera indicada no existe"
            )

    pending_by_username = db.execute(
        select(EmailVerification).where(
            EmailVerification.username == payload.username,
            EmailVerification.email != payload.email,
        )
    ).scalar_one_or_none()

    if pending_by_username:
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario ya está en uso",
        )

    if payload.dni:
        pending_by_dni = db.execute(
            select(EmailVerification).where(
                EmailVerification.dni == payload.dni,
                EmailVerification.email != payload.email,
            )
        ).scalar_one_or_none()

        if pending_by_dni:
            raise HTTPException(
                status_code=400,
                detail="El DNI ya está registrado",
            )

    code = _generate_verification_code()
    code_hash = _hash_verification_code(code, payload.email)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.EMAIL_VERIFICATION_TTL_MINUTES
    )

    pending = _get_pending_by_email(db, payload.email)
    hashed_password = hash_password(payload.password)

    if pending:
        pending.full_name = payload.full_name
        pending.username = payload.username
        pending.dni = payload.dni
        pending.career_id = payload.career_id
        pending.hashed_password = hashed_password
        pending.code_hash = code_hash
        pending.expires_at = expires_at
        pending.attempts = 0
    else:
        pending = EmailVerification(
            email=payload.email,
            full_name=payload.full_name,
            username=payload.username,
            dni=payload.dni,
            career_id=payload.career_id,
            hashed_password=hashed_password,
            code_hash=code_hash,
            expires_at=expires_at,
        )
        db.add(pending)

    db.commit()
    db.refresh(pending)

    try:
        send_email(
            payload.email,
            "Codigo de verificacion - Puntualo",
            (
                "Tu codigo de verificacion es: "
                f"{code}\n\n"
                "Este codigo vence en "
                f"{settings.EMAIL_VERIFICATION_TTL_MINUTES} minutos."
            ),
        )
    except Exception as exc:
        logger.exception("email send failed", exc_info=exc)
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=500,
            detail="No se pudo enviar el codigo de verificacion",
        ) from exc

    return {
        "detail": "Codigo enviado",
        "expires_in_seconds": settings.EMAIL_VERIFICATION_TTL_MINUTES * 60,
    }


def verify_registration(
    db: Session,
    payload: RegisterVerifyRequest
) -> User:

    pending = _get_pending_by_email(db, payload.email)

    if not pending:
        raise HTTPException(
            status_code=400,
            detail="No hay registro pendiente para ese correo",
        )

    now = datetime.now(timezone.utc)

    if pending.expires_at < now:
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="El codigo ha expirado",
        )

    if pending.attempts >= settings.EMAIL_VERIFICATION_MAX_ATTEMPTS:
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Se agotaron los intentos del codigo",
        )

    expected_hash = _hash_verification_code(payload.code, payload.email)
    if not hmac.compare_digest(expected_hash, pending.code_hash):
        pending.attempts += 1
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Codigo invalido",
        )

    if get_user_by_email(db, pending.email):
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado",
        )

    existing_username = db.execute(
        select(User).where(User.username == pending.username)
    ).scalar_one_or_none()

    if existing_username:
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario ya está en uso",
        )

    if pending.dni:
        existing_dni = db.execute(
            select(User).where(User.dni == pending.dni)
        ).scalar_one_or_none()

        if existing_dni:
            db.delete(pending)
            db.commit()
            raise HTTPException(
                status_code=400,
                detail="El DNI ya está registrado",
            )

    if pending.career_id is not None:
        career = db.get(Career, pending.career_id)
        if career is None:
            db.delete(pending)
            db.commit()
            raise HTTPException(
                status_code=400,
                detail="La carrera indicada no existe",
            )

    user = User(
        email=pending.email,
        full_name=pending.full_name,
        username=pending.username,
        dni=pending.dni,
        career_id=pending.career_id,
        hashed_password=pending.hashed_password,
    )

    db.add(user)
    db.delete(pending)
    db.commit()
    db.refresh(user)

    return user


def start_password_reset(
    db: Session,
    payload: PasswordResetStartRequest
) -> dict:

    user = get_user_by_email(db, payload.email)

    if not user:
        raise HTTPException(
            status_code=400,
            detail="El correo no está registrado",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Usuario inactivo",
        )

    code = _generate_verification_code()
    code_hash = _hash_verification_code(code, payload.email)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_TTL_MINUTES
    )

    pending = _get_password_reset_by_email(db, payload.email)

    if pending:
        pending.code_hash = code_hash
        pending.expires_at = expires_at
        pending.attempts = 0
    else:
        pending = PasswordReset(
            email=payload.email,
            code_hash=code_hash,
            expires_at=expires_at,
        )
        db.add(pending)

    db.commit()
    db.refresh(pending)

    try:
        send_email(
            payload.email,
            "Codigo para restablecer tu contrasena - Puntualo",
            (
                "Tu codigo de restablecimiento es: "
                f"{code}\n\n"
                "Este codigo vence en "
                f"{settings.PASSWORD_RESET_TTL_MINUTES} minutos."
            ),
        )
    except Exception as exc:
        logger.exception("password reset email failed", exc_info=exc)
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=500,
            detail="No se pudo enviar el codigo de restablecimiento",
        ) from exc

    return {
        "detail": "Codigo enviado",
        "expires_in_seconds": settings.PASSWORD_RESET_TTL_MINUTES * 60,
    }


def _validate_password_reset_code(
    db: Session,
    email: str,
    code: str,
) -> PasswordReset:

    pending = _get_password_reset_by_email(db, email)

    if not pending:
        raise HTTPException(
            status_code=400,
            detail="No hay solicitud pendiente",
        )

    now = datetime.now(timezone.utc)

    if pending.expires_at < now:
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="El codigo ha expirado",
        )

    if pending.attempts >= settings.PASSWORD_RESET_MAX_ATTEMPTS:
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Se agotaron los intentos del codigo",
        )

    expected_hash = _hash_verification_code(code, email)
    if not hmac.compare_digest(expected_hash, pending.code_hash):
        pending.attempts += 1
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Codigo invalido",
        )

    return pending


def verify_password_reset(
    db: Session,
    payload: PasswordResetVerifyRequest,
) -> dict:

    _validate_password_reset_code(db, payload.email, payload.code)

    return {
        "detail": "Codigo valido",
    }


def confirm_password_reset(
    db: Session,
    payload: PasswordResetConfirmRequest,
) -> dict:

    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Las contrasenas no coinciden",
        )

    pending = _validate_password_reset_code(db, payload.email, payload.code)

    user = get_user_by_email(db, payload.email)

    if not user:
        db.delete(pending)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="El correo no está registrado",
        )

    user.hashed_password = hash_password(payload.new_password)

    db.delete(pending)
    db.commit()

    return {
        "detail": "Contrasena actualizada",
    }


def authenticate_user(
    db: Session,
    payload: LoginRequest
) -> dict:

    user = get_user_by_email(
        db,
        payload.email
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

    valid_password = verify_password(
        payload.password,
        user.hashed_password
    )

    if not valid_password:

        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

    if not user.is_active:

        raise HTTPException(
            status_code=403,
            detail="Usuario inactivo"
        )

    tokens = generate_tokens(user)

    return tokens
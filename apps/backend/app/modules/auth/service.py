from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.core.security import create_refresh_token
from app.core.security import hash_password
from app.core.security import verify_password
from app.models.user import User
from app.modules.auth.schemas import LoginRequest
from app.modules.auth.schemas import RegisterRequest


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


def register_user(
    db: Session,
    payload: RegisterRequest
) -> User:

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

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        username=payload.username,
        dni=payload.dni,
        career=payload.career,
        hashed_password=hash_password(
            payload.password
        )
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


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
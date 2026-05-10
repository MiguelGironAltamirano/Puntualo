from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.service import (
    register_user,
    authenticate_user,
)
from app.modules.auth.dependencies import get_current_user
from app.models.user import User
from app.modules.auth.schemas import RefreshTokenRequest
from app.core.security import (
    decode_token,
    create_access_token,
)
router = APIRouter()

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    user = register_user(db, payload)
    return user

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    return authenticate_user(db, payload)

@router.get(
    "/me",
    response_model=UserResponse,
)
def me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/refresh")
def refresh_token(payload: RefreshTokenRequest):
    decoded = decode_token(payload.refresh_token)

    if not decoded:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    email = decoded.get("sub")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    access_token = create_access_token(
        {
            "sub": email,
            "role": decoded.get("role"),
            "type": "access",
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
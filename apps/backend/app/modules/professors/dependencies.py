from fastapi import Depends, HTTPException, status

from app.models.user import User
from app.modules.auth.dependencies import get_current_user


def is_admin(user: User) -> bool:
    return user.role == "admin"


def require_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "USER_NOT_VERIFIED",
                "message": "El usuario debe estar verificado para realizar esta acción",
            },
        )
    return current_user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Se requiere rol de administrador",
            },
        )
    return current_user

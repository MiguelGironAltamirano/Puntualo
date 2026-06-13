from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.modules.admin.schemas import AdminStatsResponse
from app.modules.admin.service import get_admin_stats
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
    """Retorna los conteos de entidades pendientes de acción por parte del administrador."""
    return get_admin_stats(db)

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.professor import Professor
from app.models.user import User


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

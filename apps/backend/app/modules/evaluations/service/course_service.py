"""Course service — Tarea 5 (find-or-create + busqueda).

Operaciones del catalogo de cursos para la 2.6. El frontend siempre llama a
`find_or_create` antes de crear una evaluacion (el usuario puede tipear un
curso nuevo o seleccionar uno existente).

Matching de duplicados: `lower(name)` + `university_id` y solo cursos
`is_active = True`. La unicidad fuerte la garantiza el indice
`uq_courses_name_university_active` a nivel DB.
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.db import escape_like

from app.models.course import Course


class CourseService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_or_create(
        self,
        name: str,
        university_id: int,
        faculty_id: int,
    ) -> tuple[Course, bool]:
        """Devuelve `(course, created)`. `created=True` solo si se insertó fila nueva."""
        normalized = name.strip()
        existing = await self._find_active(normalized, university_id)
        if existing is not None:
            return existing, False

        course = Course(
            name=normalized,
            university_id=university_id,
            faculty_id=faculty_id,
        )
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)
        return course, True

    def list_query(
        self,
        q: str | None = None,
        university_id: int | None = None,
    ):
        """Query base de cursos activos. Se pasa al helper `paginate` desde el router."""
        base = select(Course).where(Course.is_active.is_(True))
        if q:
            term = f"%{escape_like(q.strip().lower())}%"
            base = base.where(func.lower(Course.name).like(term, escape="\\"))
        if university_id is not None:
            base = base.where(Course.university_id == university_id)
        return base.order_by(Course.created_at.desc())

    async def _find_active(
        self,
        name: str,
        university_id: int,
    ) -> Course | None:
        stmt = select(Course).where(
            func.lower(Course.name) == name.lower(),
            Course.university_id == university_id,
            Course.is_active.is_(True),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

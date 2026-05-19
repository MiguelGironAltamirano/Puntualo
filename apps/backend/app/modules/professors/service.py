import logging
from datetime import datetime, timezone

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.professor import Professor
from app.models.professor_evidence import ProfessorEvidence
from app.modules.professors.schemas import (
    VALIDATION_STATUSES,
    ProfessorCreate,
    ProfessorUpdate,
)

logger = logging.getLogger(__name__)


class ProfessorAlreadyExistsError(Exception):
    pass


class InvalidValidationStatusError(Exception):
    pass


class ProfessorService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: ProfessorCreate,
        registered_by_id: str | None = None,
    ) -> Professor:
        if await self._find_duplicate(data.full_name, data.university):
            raise ProfessorAlreadyExistsError(
                f"Ya existe un profesor activo llamado '{data.full_name}' en {data.university}"
            )

        professor = Professor(
            full_name=data.full_name.strip(),
            university=data.university.strip(),
            faculty=data.faculty.strip(),
            registered_by_id=registered_by_id,
        )

        self.db.add(professor)
        await self.db.commit()
        await self.db.refresh(professor)

        # Disparar validación asíncrona — si el broker está caído, el POST no falla
        try:
            from app.tasks.professor_validation_tasks import run_professor_validation
            run_professor_validation.delay(professor.id, professor.full_name)
        except Exception as exc:
            logger.warning(
                f"could not enqueue validation | professor_id={professor.id} | error={exc}"
            )

        return professor

    async def get_by_id(self, professor_id: str) -> Professor | None:
        stmt = select(Professor).where(
            Professor.id == professor_id,
            Professor.is_active.is_(True),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    def list_query(self, search: str | None = None):
        """Construye la query base para listar profesores activos con filtro opcional."""
        base = select(Professor).where(Professor.is_active.is_(True))

        if search:
            term = f"%{search.strip().lower()}%"
            base = base.where(
                or_(
                    func.lower(Professor.full_name).like(term),
                    func.lower(Professor.university).like(term),
                    func.lower(Professor.faculty).like(term),
                )
            )

        return base.order_by(Professor.created_at.desc())

    async def update(
        self,
        professor_id: str,
        data: ProfessorUpdate,
    ) -> Professor | None:
        professor = await self.get_by_id(professor_id)
        if not professor:
            return None

        payload = data.model_dump(exclude_unset=True)

        if "validation_status" in payload:
            if payload["validation_status"] not in VALIDATION_STATUSES:
                raise InvalidValidationStatusError(
                    f"validation_status debe ser uno de {sorted(VALIDATION_STATUSES)}"
                )

        new_name = payload.get("full_name", professor.full_name)
        new_university = payload.get("university", professor.university)
        if (new_name, new_university) != (professor.full_name, professor.university):
            duplicate = await self._find_duplicate(
                new_name,
                new_university,
                exclude_id=professor.id,
            )
            if duplicate:
                raise ProfessorAlreadyExistsError(
                    f"Ya existe un profesor activo llamado '{new_name}' en {new_university}"
                )

        for field, value in payload.items():
            setattr(professor, field, value.strip() if isinstance(value, str) else value)

        await self.db.commit()
        await self.db.refresh(professor)
        return professor

    async def revalidate(self, professor_id: str) -> bool:
        professor = await self.get_by_id(professor_id)
        if not professor:
            return False

        from app.utils.cache import redis_client

        cache_keys = [
            f"openalex:validate:{professor.full_name}",
            f"openalex:author:name:{professor.full_name}",
            f"orcid:validate:{professor.full_name}",
            *(f"unmsm_directory:parsed:{url}" for url in settings.UNMSM_DIRECTORY_URLS),
        ]
        for key in cache_keys:
            await redis_client.delete(key)

        await self.db.execute(
            delete(ProfessorEvidence).where(ProfessorEvidence.professor_id == professor_id)
        )

        professor.validation_status = "pending_validation"
        await self.db.commit()

        try:
            from app.tasks.professor_validation_tasks import run_professor_validation
            run_professor_validation.delay(professor.id, professor.full_name)
        except Exception as exc:
            logger.warning(
                f"could not enqueue revalidation | professor_id={professor_id} | error={exc}"
            )

        return True

    async def soft_delete(self, professor_id: str) -> bool:
        professor = await self.get_by_id(professor_id)
        if not professor:
            return False

        professor.is_active = False
        professor.deleted_at = datetime.now(timezone.utc)
        await self.db.commit()
        return True

    async def _find_duplicate(
        self,
        full_name: str,
        university: str,
        exclude_id: str | None = None,
    ) -> Professor | None:
        stmt = select(Professor).where(
            func.lower(Professor.full_name) == full_name.strip().lower(),
            func.lower(Professor.university) == university.strip().lower(),
            Professor.is_active.is_(True),
        )
        if exclude_id:
            stmt = stmt.where(Professor.id != exclude_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

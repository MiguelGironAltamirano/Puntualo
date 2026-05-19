import logging
from datetime import datetime, timezone

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.faculty import Faculty
from app.models.professor import Professor
from app.models.professor_evidence import ProfessorEvidence
from app.models.university import University
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


class UniversityNotFoundError(Exception):
    pass


class FacultyNotFoundError(Exception):
    pass


class ProfessorService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        data: ProfessorCreate,
        registered_by_id: str | None = None,
    ) -> Professor:
        await self._validate_university_and_faculty(
            data.university_id, data.faculty_id
        )

        if await self._find_duplicate(data.full_name, data.university_id):
            raise ProfessorAlreadyExistsError(
                f"Ya existe un profesor activo llamado '{data.full_name}' "
                f"en la universidad id={data.university_id}"
            )

        professor = Professor(
            full_name=data.full_name.strip(),
            university_id=data.university_id,
            faculty_id=data.faculty_id,
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
        base = (
            select(Professor)
            .join(University, Professor.university_id == University.id)
            .join(Faculty, Professor.faculty_id == Faculty.id)
            .where(Professor.is_active.is_(True))
        )

        if search:
            term = f"%{search.strip().lower()}%"
            base = base.where(
                or_(
                    func.lower(Professor.full_name).like(term),
                    func.lower(University.name).like(term),
                    func.lower(Faculty.name).like(term),
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

        new_university_id = payload.get("university_id", professor.university_id)
        new_faculty_id = payload.get("faculty_id", professor.faculty_id)

        if (
            new_university_id != professor.university_id
            or new_faculty_id != professor.faculty_id
        ):
            await self._validate_university_and_faculty(
                new_university_id, new_faculty_id
            )

        new_name = payload.get("full_name", professor.full_name)
        if (new_name, new_university_id) != (
            professor.full_name,
            professor.university_id,
        ):
            duplicate = await self._find_duplicate(
                new_name,
                new_university_id,
                exclude_id=professor.id,
            )
            if duplicate:
                raise ProfessorAlreadyExistsError(
                    f"Ya existe un profesor activo llamado '{new_name}' "
                    f"en la universidad id={new_university_id}"
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
        university_id: int,
        exclude_id: str | None = None,
    ) -> Professor | None:
        stmt = select(Professor).where(
            func.lower(Professor.full_name) == full_name.strip().lower(),
            Professor.university_id == university_id,
            Professor.is_active.is_(True),
        )
        if exclude_id:
            stmt = stmt.where(Professor.id != exclude_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _validate_university_and_faculty(
        self,
        university_id: int,
        faculty_id: int,
    ) -> None:
        """Valida que university_id exista y que faculty_id pertenezca a esa university."""
        university = await self.db.get(University, university_id)
        if university is None:
            raise UniversityNotFoundError(
                f"No existe universidad con id={university_id}"
            )

        faculty = await self.db.get(Faculty, faculty_id)
        if faculty is None or faculty.university_id != university_id:
            raise FacultyNotFoundError(
                f"No existe facultad con id={faculty_id} en la universidad id={university_id}"
            )

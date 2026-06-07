import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.academic_degree import AcademicDegree
from app.models.course import Course
from app.models.faculty import Faculty
from app.models.professor import Professor
from app.models.professor_ai_summary import ProfessorAiSummary
from app.models.professor_course import ProfessorCourse
from app.models.professor_degree import ProfessorDegree
from app.models.professor_evidence import ProfessorEvidence
from app.models.university import University
from app.services.nlp.summary_generator import published_comment_count
from app.modules.professors.schemas import (
    VALIDATION_STATUSES,
    DegreeRef,
    ProfessorCreate,
    ProfessorUpdate,
    SortField,
    SortOrder,
)

logger = logging.getLogger(__name__)


class ProfessorAlreadyExistsError(Exception):
    pass


class UniversityNotFoundError(Exception):
    pass


class FacultyNotFoundError(Exception):
    pass


class CourseNotFoundError(Exception):
    pass


class CoursesNotFoundError(Exception):
    def __init__(self, ids: list[int]):
        self.ids = ids
        super().__init__(f"Cursos no encontrados o inactivos: {ids}")


class InvalidCourseFacultyError(Exception):
    pass


class InvalidStateTransitionError(Exception):
    def __init__(self, current_status: str):
        self.current_status = current_status
        super().__init__(
            f"Solo se puede rechazar profesores en estado 'not_found' (actual: '{current_status}')"
        )


class ProfessorService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # ---------- writes ----------

    async def create(
        self,
        data: ProfessorCreate,
        registered_by_id: str | uuid.UUID | None = None,
    ) -> Professor:
        await self._validate_university_and_faculty(
            data.university_id, data.faculty_id
        )

        if await self._find_duplicate(data.full_name, data.university_id):
            raise ProfessorAlreadyExistsError(
                f"Ya existe un profesor activo llamado '{data.full_name}' "
                f"en la universidad id={data.university_id}"
            )

        unique_course_ids = list(dict.fromkeys(data.course_ids))
        courses = (
            await self.db.execute(
                select(Course).where(
                    Course.id.in_(unique_course_ids),
                    Course.is_active.is_(True),
                )
            )
        ).scalars().all()

        found_ids = {c.id for c in courses}
        missing = [cid for cid in unique_course_ids if cid not in found_ids]
        if missing:
            raise CoursesNotFoundError(ids=missing)

        wrong_faculty = [c.id for c in courses if c.faculty_id != data.faculty_id]
        if wrong_faculty:
            raise InvalidCourseFacultyError(
                f"Los cursos {wrong_faculty} no pertenecen a la facultad id={data.faculty_id}"
            )

        professor = Professor(
            full_name=data.full_name.strip(),
            university_id=data.university_id,
            faculty_id=data.faculty_id,
            registered_by_id=registered_by_id,
        )
        self.db.add(professor)
        await self.db.flush()  # populate professor.id without committing

        for cid in unique_course_ids:
            self.db.add(ProfessorCourse(professor_id=professor.id, course_id=cid))

        await self.db.commit()
        await self.db.refresh(professor)

        self._enqueue_validation(professor.id, professor.full_name, op="create")
        return professor

    async def update(
        self,
        professor_id: str | uuid.UUID,
        data: ProfessorUpdate,
    ) -> Professor | None:
        professor = await self.get_by_id(professor_id)
        if not professor:
            return None

        payload = data.model_dump(exclude_unset=True)

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

    async def soft_delete(self, professor_id: str | uuid.UUID) -> bool:
        professor = await self.get_by_id(professor_id)
        if not professor:
            return False

        professor.is_active = False
        professor.deleted_at = datetime.now(timezone.utc)
        await self.db.commit()
        return True

    async def revalidate(self, professor_id: str | uuid.UUID) -> bool:
        professor = await self.get_by_id(professor_id, include_inactive=True)
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
            try:
                await redis_client.delete(key)
            except Exception as exc:
                logger.warning(
                    f"could not clear cache key {key} | error={exc}"
                )

        await self.db.execute(
            delete(ProfessorEvidence).where(ProfessorEvidence.professor_id == professor_id)
        )

        professor.validation_status = "pending_validation"
        await self.db.commit()

        return self._enqueue_validation(
            professor.id, professor.full_name, op="revalidate"
        )

    async def reject(self, professor_id: str | uuid.UUID) -> Professor | None:
        professor = await self.get_by_id(professor_id, include_inactive=True)
        if not professor:
            return None

        if professor.validation_status == "rejected":
            return professor  # idempotente

        if professor.validation_status != "not_found":
            raise InvalidStateTransitionError(professor.validation_status)

        professor.validation_status = "rejected"
        await self.db.commit()
        await self.db.refresh(professor)
        return professor

    async def add_course(self, professor_id: str | uuid.UUID, course_id: int) -> bool:
        professor = await self.get_by_id(professor_id)
        if not professor:
            return False

        course = await self.db.get(Course, course_id)
        if course is None or not course.is_active:
            raise CourseNotFoundError(f"No existe curso con id={course_id}")

        if course.faculty_id != professor.faculty_id:
            raise InvalidCourseFacultyError(
                f"El curso id={course_id} no pertenece a la facultad del profesor"
            )

        existing = await self.db.execute(
            select(ProfessorCourse).where(
                ProfessorCourse.professor_id == professor_id,
                ProfessorCourse.course_id == course_id,
            )
        )
        if existing.scalar_one_or_none():
            return True  # idempotente

        self.db.add(ProfessorCourse(professor_id=professor_id, course_id=course_id))
        await self.db.commit()
        return True

    async def remove_course(self, professor_id: str | uuid.UUID, course_id: int) -> bool:
        result = await self.db.execute(
            delete(ProfessorCourse).where(
                ProfessorCourse.professor_id == professor_id,
                ProfessorCourse.course_id == course_id,
            )
        )
        await self.db.commit()
        return result.rowcount > 0

    # ---------- reads ----------

    async def get_by_id(
        self,
        professor_id: str | uuid.UUID,
        include_inactive: bool = False,
    ) -> Professor | None:
        stmt = select(Professor).where(Professor.id == professor_id)
        if not include_inactive:
            stmt = stmt.where(Professor.is_active.is_(True))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    def list_query(
        self,
        *,
        search: str | None = None,
        university_id: int | None = None,
        faculty_id: int | None = None,
        course_id: int | None = None,
        validation_status: str | None = None,
        include_deleted: bool = False,
        hide_rejected: bool = True,
        sort_by: SortField = "created_at",
        sort_order: SortOrder = "desc",
        min_clarity: int | None = None,
        max_clarity: int | None = None,
        min_easiness: int | None = None,
        max_easiness: int | None = None,
        min_helpfulness: int | None = None,
        max_helpfulness: int | None = None,
        min_punctuality: int | None = None,
        max_punctuality: int | None = None,
        min_global_score: float | None = None,
        max_global_score: float | None = None,
        min_evaluations: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ):
        from datetime import datetime
        
        base = (
            select(Professor)
            .join(University, Professor.university_id == University.id)
            .join(Faculty, Professor.faculty_id == Faculty.id)
        )

        if not include_deleted:
            base = base.where(Professor.is_active.is_(True))

        if search:
            term = f"%{search.strip().lower()}%"
            base = base.where(
                or_(
                    func.lower(Professor.full_name).like(term),
                    func.lower(University.name).like(term),
                    func.lower(Faculty.name).like(term),
                )
            )

        if university_id is not None:
            base = base.where(Professor.university_id == university_id)

        if faculty_id is not None:
            base = base.where(Professor.faculty_id == faculty_id)

        if course_id is not None:
            base = base.where(
                select(ProfessorCourse.professor_id)
                .where(
                    ProfessorCourse.professor_id == Professor.id,
                    ProfessorCourse.course_id == course_id,
                )
                .exists()
            )

        # Score range filters on evaluations
        if any(
            f is not None
            for f in [
                min_clarity,
                max_clarity,
                min_easiness,
                max_easiness,
                min_helpfulness,
                max_helpfulness,
                min_punctuality,
                max_punctuality,
            ]
        ):
            from app.models.evaluation import Evaluation
            
            eval_subquery = select(Evaluation.professor_id).where(
                Evaluation.professor_id == Professor.id
            )
            
            if min_clarity is not None:
                eval_subquery = eval_subquery.where(Evaluation.clarity >= min_clarity)
            if max_clarity is not None:
                eval_subquery = eval_subquery.where(Evaluation.clarity <= max_clarity)
            if min_easiness is not None:
                eval_subquery = eval_subquery.where(Evaluation.easiness >= min_easiness)
            if max_easiness is not None:
                eval_subquery = eval_subquery.where(Evaluation.easiness <= max_easiness)
            if min_helpfulness is not None:
                eval_subquery = eval_subquery.where(Evaluation.helpfulness >= min_helpfulness)
            if max_helpfulness is not None:
                eval_subquery = eval_subquery.where(Evaluation.helpfulness <= max_helpfulness)
            if min_punctuality is not None:
                eval_subquery = eval_subquery.where(Evaluation.punctuality >= min_punctuality)
            if max_punctuality is not None:
                eval_subquery = eval_subquery.where(Evaluation.punctuality <= max_punctuality)
            
            base = base.where(eval_subquery.exists())

        # Global score filters
        if min_global_score is not None:
            base = base.where(Professor.global_score >= min_global_score)
        if max_global_score is not None:
            base = base.where(Professor.global_score <= max_global_score)

        # Minimum evaluations filter
        if min_evaluations is not None:
            base = base.where(Professor.total_evaluations >= min_evaluations)

        # Date range filters
        if date_from is not None:
            try:
                from_date = datetime.fromisoformat(date_from)
                base = base.where(Professor.created_at >= from_date)
            except (ValueError, TypeError):
                pass  # Ignore invalid dates
        
        if date_to is not None:
            try:
                to_date = datetime.fromisoformat(date_to)
                base = base.where(Professor.created_at <= to_date)
            except (ValueError, TypeError):
                pass  # Ignore invalid dates

        if validation_status is not None:
            base = base.where(Professor.validation_status == validation_status)
        elif hide_rejected:
            base = base.where(Professor.validation_status != "rejected")

        sort_column = {
            "created_at": Professor.created_at,
            "global_score": Professor.global_score,
            "total_evaluations": Professor.total_evaluations,
        }[sort_by]

        order = sort_column.desc() if sort_order == "desc" else sort_column.asc()
        return base.order_by(order, Professor.id.desc())

    async def list_courses(self, professor_id: str | uuid.UUID) -> list[Course]:
        stmt = (
            select(Course)
            .join(ProfessorCourse, ProfessorCourse.course_id == Course.id)
            .where(
                ProfessorCourse.professor_id == professor_id,
                Course.is_active.is_(True),
            )
            .order_by(Course.name.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_detail(
        self,
        professor_id: str | uuid.UUID,
        include_deleted: bool = False,
    ) -> tuple[
        Professor,
        list[Course],
        list[DegreeRef],
        list[ProfessorEvidence],
        str | None,
        str | None,
        str | None,
        ProfessorAiSummary | None,
        str | None,
    ] | None:
        professor = await self.get_by_id(
            professor_id, include_inactive=include_deleted
        )
        if not professor:
            return None

        university = await self.db.get(University, professor.university_id)
        faculty = await self.db.get(Faculty, professor.faculty_id)
        university_name = university.name if university else None
        faculty_name = faculty.name if faculty else None

        courses = await self.list_courses(professor_id)

        degree_stmt = (
            select(
                AcademicDegree.id,
                AcademicDegree.name,
                AcademicDegree.level,
                ProfessorDegree.institution,
                ProfessorDegree.year_obtained,
            )
            .join(ProfessorDegree, ProfessorDegree.degree_id == AcademicDegree.id)
            .where(ProfessorDegree.professor_id == professor_id)
            .order_by(ProfessorDegree.year_obtained.desc().nulls_last())
        )
        degree_rows = (await self.db.execute(degree_stmt)).all()
        degrees = [
            DegreeRef(
                id=row.id,
                name=row.name,
                level=row.level,
                institution=row.institution,
                year_obtained=row.year_obtained,
            )
            for row in degree_rows
        ]

        evidence_stmt = (
            select(ProfessorEvidence)
            .where(
                ProfessorEvidence.professor_id == professor_id,
                ProfessorEvidence.affiliation_confirmed.is_(True),
            )
            .order_by(ProfessorEvidence.fetched_at.desc())
        )
        evidence = list((await self.db.execute(evidence_stmt)).scalars().all())

        summary = await self._build_summary(professor, courses, degrees)

        ai_summary_row = (
            await self.db.execute(
                select(ProfessorAiSummary)
                .where(ProfessorAiSummary.professor_id == professor.id)
                .limit(1)
            )
        ).scalar_one_or_none()
        # El motivo se basa en el MISMO criterio que el guard de generación
        # (comentarios publicados), no en total_evaluations: un profesor puede
        # tener evaluaciones cuyo comentario está oculto/eliminado y aun así no
        # llegar al mínimo de texto para resumir.
        ai_summary_reason = None
        if ai_summary_row is None:
            published = await published_comment_count(professor.id, self.db)
            if published < settings.NLP_SUMMARY_MIN_REVIEWS:
                ai_summary_reason = "insufficient_data"

        return (
            professor, courses, degrees, evidence, summary,
            university_name, faculty_name, ai_summary_row, ai_summary_reason,
        )

    # ---------- helpers ----------

    async def _build_summary(
        self,
        professor: Professor,
        courses: list[Course],
        degrees: list[DegreeRef],
    ) -> str | None:
        """Texto del resumen para `executive_summary`.

        Si existe un resumen NLP (Tarea 4.4) en professor_ai_summaries, devuelve
        su texto; si no, genera un texto factual a partir de los datos disponibles
        (fallback para perfiles aún sin resumen generado).
        """
        try:
            summary_stmt = (
                select(ProfessorAiSummary)
                .where(ProfessorAiSummary.professor_id == professor.id)
                .limit(1)
            )
            existing = (await self.db.execute(summary_stmt)).scalar_one_or_none()
            if existing is not None:
                return existing.summary
        except Exception as exc:
            # En tests SQLite la tabla puede no existir; en prod cualquier error
            # de lectura no debe romper el detalle del profesor.
            logger.debug(f"ai_summary read fallback: {exc}")

        parts: list[str] = [f"{professor.full_name}"]
        if courses:
            course_names = ", ".join(c.name for c in courses[:5])
            extra = f" y {len(courses) - 5} más" if len(courses) > 5 else ""
            parts.append(f"dicta {course_names}{extra}")
        if professor.total_evaluations:
            parts.append(f"con {professor.total_evaluations} evaluaciones registradas")
        if professor.global_score is not None:
            parts.append(f"y un puntaje global de {float(professor.global_score):.2f}/5")
        if degrees:
            top = degrees[0]
            parts.append(f"Grado destacado: {top.name}")
        return ". ".join(parts) + "."

    def _enqueue_validation(
        self,
        professor_id: str | uuid.UUID,
        full_name: str,
        op: str,
    ) -> bool:
        # Celery serializa los args a JSON; pasar str evita ambigüedad de serializer.
        pid = str(professor_id)
        try:
            from app.tasks.professor_validation_tasks import run_professor_validation
            run_professor_validation.delay(pid, full_name)
            return True
        except Exception as exc:
            logger.warning(
                f"could not enqueue {op} | professor_id={pid} | error={exc}"
            )
            return False

    async def _find_duplicate(
        self,
        full_name: str,
        university_id: int,
        exclude_id: str | uuid.UUID | None = None,
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

"""Evaluation service — Tarea 6.

Crea una evaluacion (5 metricas) + comentario embebido opcional + recalcula
el score del profesor en una sola transaccion atomica. Post-commit dispara
invalidacion de cache (Tarea 11 stub) y SummaryTrigger (Tarea 10 stub).
"""
import logging
from dataclasses import dataclass

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.comment import Comment, CommentStatus
from app.models.course import Course
from app.models.evaluation import Evaluation
from app.models.professor import Professor
from app.models.user import User
from app.modules.evaluations.errors import (
    CommentTooShortError,
    CourseNotFoundError,
    EvaluationDuplicateError,
    ProfessorNotFoundError,
)
from app.modules.evaluations.profanity import check as profanity_check
from app.modules.evaluations.schemas import EvaluationCreate
from app.modules.evaluations.scoring import compute_global_score
from app.modules.evaluations.semester import current_semester
from app.modules.evaluations.summary_hook import SummaryTrigger
from app.utils.cache import invalidate_professor

logger = logging.getLogger(__name__)


@dataclass
class EvaluationCreateResult:
    """Resultado de `create()`: lo que el router necesita para armar la respuesta."""

    evaluation: Evaluation
    comment: Comment | None
    professor: Professor


class EvaluationService:

    def __init__(self, db: AsyncSession):
        self.db = db

    # -----------------------------------------------------------------------
    # create
    # -----------------------------------------------------------------------

    async def create(
        self,
        user: User,
        payload: EvaluationCreate,
    ) -> EvaluationCreateResult:
        """Crea evaluacion + comentario opcional + recalcula score (todo en una tx)."""
        # 1) Pre-tx: validar comentario (longitud + profanity) antes de tocar DB.
        normalized_comment = self._validate_comment(payload.comment_text)

        semester = current_semester()

        # 2) Existencia de profesor y curso (cheap reads).
        professor = await self._get_active_professor(payload.professor_id)
        course = await self._get_active_course(payload.course_id)

        # 3) Tx unica: INSERT eval -> [INSERT comment] -> UPDATE professor.
        evaluation = Evaluation(
            user_id=user.id,
            professor_id=payload.professor_id,
            course_id=payload.course_id,
            semester=semester,
            clarity=payload.clarity,
            easiness=payload.easiness,
            helpfulness=payload.helpfulness,
            punctuality=payload.punctuality,
            modality=payload.modality,
        )
        self.db.add(evaluation)
        try:
            await self.db.flush()
        except IntegrityError as exc:
            # Unica IntegrityError esperada aca: violacion del UNIQUE
            # (user, professor, course, semester). Otras CHECK constraints
            # estan cubiertas por Pydantic upstream.
            await self.db.rollback()
            raise EvaluationDuplicateError() from exc

        comment: Comment | None = None
        if normalized_comment is not None:
            comment = Comment(
                evaluation_id=evaluation.id,
                user_id=user.id,
                professor_id=payload.professor_id,
                course_id=payload.course_id,
                text=normalized_comment,
                modality=payload.modality,
                status=CommentStatus.PUBLISHED.value,
            )
            self.db.add(comment)
            await self.db.flush()

        await self._recompute_professor_score(payload.professor_id)
        await self.db.commit()

        await self.db.refresh(evaluation)
        if comment is not None:
            await self.db.refresh(comment)
        await self.db.refresh(professor)

        # 4) Post-commit hooks (errores no rompen la respuesta).
        await self._post_commit_hooks(payload.professor_id)

        return EvaluationCreateResult(
            evaluation=evaluation,
            comment=comment,
            professor=professor,
        )

    # -----------------------------------------------------------------------
    # get_my_evaluations — para que el frontend prevenga doble-evaluacion
    # -----------------------------------------------------------------------

    async def get_my_evaluations(
        self,
        user: User,
        professor_id: str | None = None,
        course_id: str | None = None,
        semester: str | None = None,
    ) -> list[Evaluation]:
        stmt = select(Evaluation).where(Evaluation.user_id == user.id)
        if professor_id is not None:
            stmt = stmt.where(Evaluation.professor_id == professor_id)
        if course_id is not None:
            stmt = stmt.where(Evaluation.course_id == course_id)
        if semester is not None:
            stmt = stmt.where(Evaluation.semester == semester)
        stmt = stmt.order_by(Evaluation.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # -----------------------------------------------------------------------
    # Helpers privados
    # -----------------------------------------------------------------------

    def _validate_comment(self, comment_text: str | None) -> str | None:
        """Devuelve el texto stripped si es valido, None si no hay comentario."""
        if comment_text is None:
            return None
        stripped = comment_text.strip()
        if len(stripped) < settings.COMMENT_MIN_LENGTH:
            raise CommentTooShortError(
                f"El comentario debe tener al menos {settings.COMMENT_MIN_LENGTH} caracteres."
            )
        # profanity.check raisea OffensiveContentError si matchea
        profanity_check(stripped)
        return stripped

    async def _get_active_professor(self, professor_id: str) -> Professor:
        professor = await self.db.get(Professor, professor_id)
        if professor is None or not professor.is_active:
            raise ProfessorNotFoundError()
        return professor

    async def _get_active_course(self, course_id: str) -> Course:
        course = await self.db.get(Course, course_id)
        if course is None or not course.is_active:
            raise CourseNotFoundError()
        return course

    async def _recompute_professor_score(self, professor_id: str) -> None:
        """Recalcula `global_score` + `total_evaluations` desde scratch.

        Solo 4 metricas entran al score (clarity, easiness, helpfulness,
        punctuality). `course_difficulty` se ignora a nivel agregado — se
        captura por evaluacion como metadato del curso, no del profe.
        """
        stmt = select(
            func.avg(Evaluation.clarity),
            func.avg(Evaluation.easiness),
            func.avg(Evaluation.helpfulness),
            func.avg(Evaluation.punctuality),
            func.count(Evaluation.id),
        ).where(Evaluation.professor_id == professor_id)
        avg_c, avg_e, avg_h, avg_p, count = (await self.db.execute(stmt)).one()

        if not count:
            await self.db.execute(
                update(Professor)
                .where(Professor.id == professor_id)
                .values(global_score=None, total_evaluations=0)
            )
            return

        score = compute_global_score(
            float(avg_c),
            float(avg_e),
            float(avg_h),
            float(avg_p),
        )
        await self.db.execute(
            update(Professor)
            .where(Professor.id == professor_id)
            .values(global_score=score, total_evaluations=int(count))
        )

    async def _post_commit_hooks(self, professor_id: str) -> None:
        """Llama a cache.invalidate_professor + SummaryTrigger.maybe_dispatch.

        Los errores de hooks se loggean pero no propagan — la evaluacion ya
        esta commiteada y no queremos romper la respuesta por fallas de Redis
        o del broker.
        """
        try:
            await invalidate_professor(professor_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "post_commit.cache_invalidate_failed | professor_id=%s | error=%s",
                professor_id,
                exc,
            )

        try:
            await SummaryTrigger().maybe_dispatch(professor_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "post_commit.summary_trigger_failed | professor_id=%s | error=%s",
                professor_id,
                exc,
            )

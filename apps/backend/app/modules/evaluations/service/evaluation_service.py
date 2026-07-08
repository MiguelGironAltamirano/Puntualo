"""Evaluation service.

Crea atomicamente: evaluacion + comentario opcional + hashtags opcionales.
Delega el recalculo de professor.global_score a una task Celery
(`recalculate_professor_score`) — fuera de la transaccion.

Validaciones (en orden):
  1. Comentario: longitud + banned_terms (severity threshold 'medium').
  2. Profesor activo y validation_status='validated'.
  3. Curso activo.
  4. Curso pertenece a professor_courses.
  5. Hashtags: normalizar + limit + banned_terms (severity threshold 'low').
  6. UNIQUE(user, professor, course, semester) — IntegrityError -> 409.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.comment import Comment, CommentStatus
from app.models.course import Course
from app.models.evaluation import Evaluation
from app.models.evaluation_hashtag import EvaluationHashtag
from app.models.professor import Professor
from app.models.professor_course import ProfessorCourse
from app.models.user import User
from app.modules.evaluations.errors import (
    CommentTooShortError,
    CourseNotFoundError,
    CourseNotTaughtByProfessorError,
    EvaluationDuplicateError,
    OffensiveContentError,
    ProfessorNotFoundError,
    ProfessorNotValidatedError,
)
from app.modules.evaluations.schemas import EvaluationCreate
from app.modules.evaluations.semester import current_semester
from app.modules.evaluations.service.hashtag_service import HashtagService
from app.modules.evaluations.summary_hook import SummaryTrigger
from app.services.moderation.moderation_pipeline import ModerationCheckpoint
from app.utils.cache import invalidate_professor
from app.utils.moderation import heuristic_filter

logger = logging.getLogger(__name__)


@dataclass
class EvaluationCreateResult:
    """Resultado de `create()`: lo que el router necesita para armar la respuesta."""

    evaluation: Evaluation
    comment: Comment | None
    professor: Professor
    hashtags: list[str] = field(default_factory=list)


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
        """Crea evaluacion + comentario opcional + hashtags + delega recalc score."""
        # 1) Pre-tx: validar longitud + heuristic filter del comment.
        normalized_comment, comment_status = await self._validate_comment(payload.comment_text)

        semester = current_semester()

        # 2) Profesor existe, activo, validated.
        professor = await self._get_validated_professor(payload.professor_id)

        # 3) Curso existe y activo.
        course = await self._get_active_course(payload.course_id)

        # 4) Curso es dictado por el profesor.
        await self._assert_course_taught_by_professor(
            professor_id=professor.id, course_id=course.id
        )

        # 5) Procesar hashtags (puede levantar HashtagLimitExceededError /
        #    HashtagInvalidFormatError / HashtagBannedTermsError ANTES de insertar
        #    la evaluacion — si revientan, no se persiste nada).
        hashtag_svc = HashtagService(self.db)
        hashtags = await hashtag_svc.normalize_upsert_many(
            raw_labels=payload.hashtags, created_by_id=user.id
        )

        # 6) Tx: INSERT eval -> [INSERT comment] -> INSERT eval_hashtags.
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
                status=comment_status.value,  # Use status from heuristic filter
            )
            self.db.add(comment)
            await self.db.flush()

        for h in hashtags:
            self.db.add(EvaluationHashtag(evaluation_id=evaluation.id, hashtag_id=h.id))
        if hashtags:
            await self.db.flush()

        await self.db.commit()
        await self.db.refresh(evaluation)
        if comment is not None:
            await self.db.refresh(comment)
        await self.db.refresh(professor)

        # 7) Post-commit: hooks idempotentes (errores no rompen la respuesta).
        await self._enqueue_score_recalc(str(payload.professor_id))
        await self._post_commit_hooks(str(payload.professor_id))

        return EvaluationCreateResult(
            evaluation=evaluation,
            comment=comment,
            professor=professor,
            hashtags=[h.label for h in hashtags],
        )

    # -----------------------------------------------------------------------
    # get_my_evaluations — para que el frontend prevenga doble-evaluacion
    # -----------------------------------------------------------------------

    async def get_my_evaluations(
        self,
        user: User,
        professor_id: str | None = None,
        course_id: int | None = None,
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

    async def _validate_comment(self, comment_text: str | None) -> tuple[str | None, CommentStatus]:
        """Validates comment text using heuristic filter and returns status.
        
        Returns:
            (normalized_text: str | None, status: CommentStatus)
            
        If heuristic blocks -> raises OffensiveContentError
        If heuristic flags -> returns (text, HIDDEN_PENDING_REVIEW)
        If heuristic allows -> returns (text, PUBLISHED)
        """
        if comment_text is None:
            return None, CommentStatus.PUBLISHED

        stripped = comment_text.strip()
        if len(stripped) < settings.COMMENT_MIN_LENGTH:
            raise CommentTooShortError(
                f"El comentario debe tener al menos {settings.COMMENT_MIN_LENGTH} caracteres."
            )

        # Use enhanced heuristic filter
        heuristic_result = await heuristic_filter(stripped, db=self.db)
        
        if heuristic_result.action == "block":
            raise OffensiveContentError(
                f"El comentario contiene contenido prohibido: {', '.join(heuristic_result.reasons)}."
            )
        
        # If flagged, return pending review status; otherwise published
        status = (
            CommentStatus.HIDDEN_PENDING_REVIEW
            if heuristic_result.action == "flag"
            else CommentStatus.PUBLISHED
        )
        
        return stripped, status

    async def _get_validated_professor(self, professor_id: str) -> Professor:
        """Obtiene el profesor validando existencia, estado activo y validation_status."""
        professor = await self.db.get(Professor, professor_id)
        if professor is None or not professor.is_active:
            raise ProfessorNotFoundError()
        if professor.validation_status != "validated":
            raise ProfessorNotValidatedError()
        return professor

    async def _get_active_course(self, course_id: int) -> Course:
        course = await self.db.get(Course, course_id)
        if course is None or not course.is_active:
            raise CourseNotFoundError()
        return course

    async def _assert_course_taught_by_professor(
        self, *, professor_id, course_id: int
    ) -> None:
        stmt = select(ProfessorCourse).where(
            ProfessorCourse.professor_id == professor_id,
            ProfessorCourse.course_id == course_id,
        )
        row = (await self.db.execute(stmt)).first()
        if row is None:
            raise CourseNotTaughtByProfessorError()

    async def _enqueue_score_recalc(self, professor_id: str) -> None:
        """Encola la recalculacion del score del profesor via Celery y la ejecuta localmente."""
        try:
            from app.tasks.score_recalculation_tasks import _do_recalc
            await _do_recalc(professor_id, self.db)
            await self.db.commit()
        except Exception as exc:
            logger.warning(
                "sync_score_recalc_failed | professor_id=%s | error=%s",
                professor_id, exc,
            )

        try:
            from app.tasks.score_recalculation_tasks import recalculate_professor_score
            recalculate_professor_score.delay(professor_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "score_recalc_enqueue_failed | professor_id=%s | error=%s",
                professor_id, exc,
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

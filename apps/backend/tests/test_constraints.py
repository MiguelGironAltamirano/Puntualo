import pytest
import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.evaluation import Evaluation
from app.models.comment import Comment, CommentStatus
from app.models.user import User
from app.models.professor import Professor
from app.models.course import Course

@pytest.mark.asyncio
async def test_foreign_key_violation(test_db: AsyncSession, test_user: User, test_course: Course, test_evaluation: Evaluation):
    """Verifica que una violación de clave foránea levante un IntegrityError con PRAGMA foreign_keys=ON."""
    invalid_prof_id = uuid.uuid4()
    
    # Intentar insertar un comentario con un profesor inexistente
    comment = Comment(
        id=uuid.uuid4(),
        evaluation_id=test_evaluation.id,
        user_id=test_user.id,
        professor_id=invalid_prof_id,
        course_id=test_course.id,
        text="Comentario inválido",
        modality="presencial",
    )
    test_db.add(comment)
    with pytest.raises(IntegrityError):
        await test_db.flush()
    await test_db.rollback()

@pytest.mark.asyncio
async def test_check_constraints_evaluation_clarity(test_db: AsyncSession, test_user: User, test_professor: Professor, test_course: Course):
    """Verifica que los CHECK constraints de claridad (escala 1..5) funcionen."""
    # Intentar insertar claridad fuera del rango 1..5
    eval_invalid = Evaluation(
        id=uuid.uuid4(),
        user_id=test_user.id,
        professor_id=test_professor.id,
        course_id=test_course.id,
        semester="2026-I",
        clarity=10,  # Inválido (> 5)
        easiness=3,
        helpfulness=3,
        punctuality=3,
        modality="presencial",
    )
    test_db.add(eval_invalid)
    with pytest.raises(IntegrityError):
        await test_db.flush()
    await test_db.rollback()

@pytest.mark.asyncio
async def test_unique_constraint_evaluation(test_db: AsyncSession, test_user: User, test_professor: Professor, test_course: Course, test_evaluation: Evaluation):
    """Verifica la restricción UNIQUE por (user, professor, course, semester) en evaluaciones."""
    # Intentar insertar una segunda evaluación duplicada con el mismo usuario, docente, curso y semestre
    dup_eval = Evaluation(
        id=uuid.uuid4(),
        user_id=test_user.id,
        professor_id=test_professor.id,
        course_id=test_course.id,
        semester=test_evaluation.semester,
        clarity=4,
        easiness=4,
        helpfulness=4,
        punctuality=4,
        modality="presencial",
    )
    test_db.add(dup_eval)
    with pytest.raises(IntegrityError):
        await test_db.flush()
    await test_db.rollback()

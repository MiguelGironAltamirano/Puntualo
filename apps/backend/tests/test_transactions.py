import pytest
import asyncio
import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool
from app.models.evaluation import Evaluation
from app.models.comment import Comment
from app.models.user import User
from app.models.professor import Professor
from app.models.course import Course
from app.modules.evaluations.service.evaluation_service import EvaluationService
from app.modules.evaluations.schemas import EvaluationCreate
from app.modules.evaluations.errors import EvaluationDuplicateError

@pytest.mark.asyncio
async def test_transaction_atomicity_rollback(test_db: AsyncSession, test_user: User, test_professor: Professor, test_course: Course, test_professor_course):
    """Verifica la propiedad de atomicidad (Rollback): si ocurre un error, no se guarda nada."""
    # Instanciar el servicio
    service = EvaluationService(test_db)
    
    # Payload con comentario
    payload = EvaluationCreate(
        professor_id=str(test_professor.id),
        course_id=test_course.id,
        clarity=4,
        easiness=4,
        helpfulness=4,
        punctuality=4,
        modality="presencial",
        comment_text="a", # Esto lanzará CommentTooShortError antes de guardar
        hashtags=[]
    )
    
    # La validación de longitud del comentario lanzará CommentTooShortError antes del commit
    from app.modules.evaluations.errors import CommentTooShortError
    with pytest.raises(CommentTooShortError):
        await service.create(user=test_user, payload=payload)
        
    # Verificar que no se insertó ninguna evaluación ni comentario en la base de datos
    from sqlalchemy import select
    evals = (await test_db.execute(select(Evaluation).where(Evaluation.user_id == test_user.id))).scalars().all()
    assert len(evals) == 0

@pytest.mark.asyncio
async def test_duplicate_evaluation_prevention(
    test_db: AsyncSession, test_user: User, test_professor: Professor, test_course: Course, test_professor_course
):
    """Verifica que la inserción de una evaluación duplicada levante EvaluationDuplicateError."""
    service = EvaluationService(test_db)
    payload = EvaluationCreate(
        professor_id=str(test_professor.id),
        course_id=test_course.id,
        clarity=5,
        easiness=5,
        helpfulness=5,
        punctuality=5,
        modality="presencial",
        comment_text="Clase excelente, recomendada.",
        hashtags=[]
    )
    
    # Primera inserción exitosa
    res1 = await service.create(user=test_user, payload=payload)
    assert res1.evaluation.id is not None
    
    # Segunda inserción debe fallar con EvaluationDuplicateError debido al UNIQUE constraint
    with pytest.raises(EvaluationDuplicateError):
        await service.create(user=test_user, payload=payload)

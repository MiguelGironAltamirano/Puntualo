import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.professor import Professor
from app.models.comment import Comment, CommentStatus
from app.models.evaluation import Evaluation
from app.models.ai_job import AiJob
from app.models.professor_ai_summary import ProfessorAiSummary
from app.services.nlp.summary_generator import generate_and_store, select_reviews, published_comment_count
from app.services.nlp.gemini_client import SummaryResult
from app.tasks.nlp_tasks import _run_summary

@pytest.mark.asyncio
async def test_select_reviews_and_comment_count(test_db: AsyncSession, test_comment: Comment, test_professor: Professor):
    """Verifica el conteo y la selección de comentarios para el resumen."""
    count = await published_comment_count(test_professor.id, test_db)
    assert count == 1
    
    reviews = await select_reviews(str(test_professor.id), test_db)
    assert len(reviews) == 1
    assert reviews[0]["comment"] == "This is a test comment about the professor."

@pytest.mark.asyncio
@patch("app.services.nlp.summary_generator.settings.NLP_SUMMARY_MIN_REVIEWS", 1)
async def test_generate_and_store_success(test_db: AsyncSession, test_professor: Professor, test_comment: Comment):
    """Verifica que se genere y almacene el resumen ejecutivo correctamente."""
    mock_client = MagicMock()
    mock_client.generate = AsyncMock(return_value=SummaryResult(
        summary="Excelente profesor.",
        pros=["Claro", "Puntual"],
        cons=["Exigente"],
        token_usage={"total": 100}
    ))
    
    # Ejecutar generate_and_store con GeminiClient mockeado
    result = await generate_and_store(
        professor_id=str(test_professor.id),
        db=test_db,
        client=mock_client,
        force=True
    )
    
    assert result is not None
    assert result["summary"] == "Excelente profesor."
    assert result["pros"] == ["Claro", "Puntual"]
    
    # Verificar persistencia en base de datos
    summary_db = (await test_db.execute(
        select(ProfessorAiSummary).where(ProfessorAiSummary.professor_id == test_professor.id)
    )).scalar_one()
    
    assert summary_db.summary == "Excelente profesor."
    assert list(summary_db.pros) == ["Claro", "Puntual"]

@pytest.mark.asyncio
@patch("app.services.nlp.summary_generator.settings.NLP_SUMMARY_MIN_REVIEWS", 1)
async def test_run_summary_task_flow(test_db: AsyncSession, test_professor: Professor, test_comment: Comment):
    """Prueba el flujo de la tarea _run_summary (AiJob cycle)."""
    mock_client = MagicMock()
    mock_client.generate = AsyncMock(return_value=SummaryResult(
        summary="Resumen de prueba.",
        pros=["Pro"],
        cons=["Con"],
        token_usage={"total": 50}
    ))
    
    with patch("app.services.nlp.summary_generator.GeminiClient", return_value=mock_client):
        # Ejecutar la corutina de la tarea Celery
        await _run_summary(
            professor_id=str(test_professor.id),
            session_factory=lambda: test_db,
            force=True
        )
        
    # Verificar el estado de la tarea (AiJob) en la DB
    job = (await test_db.execute(
        select(AiJob).where(AiJob.job_type == "summary_generation")
    )).scalars().first()
    
    assert job is not None
    assert job.status == "completed"
    assert job.result_payload["reviews_used"] == 1

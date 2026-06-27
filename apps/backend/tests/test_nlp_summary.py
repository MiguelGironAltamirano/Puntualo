"""tests/test_nlp_summary.py - Tests for NLP summary generation, jobs workflow, and stale detection."""
import pytest
import uuid
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.comment import Comment, CommentStatus
from app.models.evaluation import Evaluation
from app.models.professor import Professor
from app.models.professor_ai_summary import ProfessorAiSummary
from app.models.ai_job import AiJob
from app.services.nlp.summary_generator import select_reviews, generate_and_store
from app.services.nlp.gemini_client import SummaryResult
from app.tasks.nlp_tasks import _run_summary, find_stale_professor_ids


@pytest.fixture
def mock_gemini_client():
    client = AsyncMock()
    client.generate.return_value = SummaryResult(
        summary="This is a mocked summary of the professor's performance.",
        pros=["Punctual", "Clear explanations"],
        cons=["Strict grading"],
        token_usage={"prompt": 100, "output": 50, "total": 150},
    )
    return client


@pytest.mark.asyncio
async def test_select_reviews_sampling(
    test_db: AsyncSession,
    test_university,
    test_faculty,
    test_course,
    test_professor: Professor,
    test_user,
):
    """Test that select_reviews retrieves, filters, and samples comments correctly."""
    # Add 12 published comments to trigger sampling (assuming NLP_SUMMARY_MAX_REVIEWS is smaller, say 10)
    # Let's override setting for the test
    with patch.object(settings, "NLP_SUMMARY_MAX_REVIEWS", 5):
        with patch.object(settings, "NLP_SUMMARY_SAMPLE_RECENT", 3):
            with patch.object(settings, "NLP_SUMMARY_SAMPLE_RANDOM", 2):
                # We need to insert evaluations and comments first
                for i in range(10):
                    evaluation = Evaluation(
                        id=uuid.uuid4(),
                        user_id=test_user.id,
                        professor_id=test_professor.id,
                        course_id=test_course.id,
                        semester=f"2023-{i}",
                        clarity=5,
                        easiness=4,
                        helpfulness=5,
                        punctuality=5,
                        modality="presencial",
                    )
                    test_db.add(evaluation)
                    await test_db.flush()

                    comment = Comment(
                        id=uuid.uuid4(),
                        evaluation_id=evaluation.id,
                        user_id=test_user.id,
                        professor_id=test_professor.id,
                        course_id=test_course.id,
                        text=f"Comment number {i}",
                        modality="presencial",
                        status=CommentStatus.PUBLISHED.value,
                    )
                    test_db.add(comment)
                
                await test_db.flush()

                reviews = await select_reviews(str(test_professor.id), test_db)
                # Should sample down to max 5 reviews
                assert len(reviews) <= 5


@pytest.mark.asyncio
async def test_generate_and_store_guards_and_upsert(
    test_db: AsyncSession,
    test_professor: Professor,
    test_user,
    test_course,
    mock_gemini_client,
):
    """Test generate_and_store guard checks and upsert logic."""
    # 1. Guard check: Professor validation status (starts as validated in fixture)
    # Set to pending_validation
    test_professor.validation_status = "pending_validation"
    await test_db.flush()

    result = await generate_and_store(
        str(test_professor.id), test_db, client=mock_gemini_client
    )
    assert result is None

    # Reset validation status to validated
    test_professor.validation_status = "validated"
    await test_db.flush()

    # 2. Guard check: Minimum reviews count
    # Currently professor has 0 comments, NLP_SUMMARY_MIN_REVIEWS defaults to 5
    with patch.object(settings, "NLP_SUMMARY_MIN_REVIEWS", 3):
        result = await generate_and_store(
            str(test_professor.id), test_db, client=mock_gemini_client
        )
        assert result is None

        # Add 3 comments to meet the guard
        for i in range(3):
            evaluation = Evaluation(
                id=uuid.uuid4(),
                user_id=test_user.id,
                professor_id=test_professor.id,
                course_id=test_course.id,
                semester=f"2023-{i}",
                clarity=5,
                easiness=5,
                helpfulness=5,
                punctuality=5,
                modality="presencial",
            )
            test_db.add(evaluation)
            await test_db.flush()

            comment = Comment(
                id=uuid.uuid4(),
                evaluation_id=evaluation.id,
                user_id=test_user.id,
                professor_id=test_professor.id,
                course_id=test_course.id,
                text=f"Check comment {i}",
                modality="presencial",
                status=CommentStatus.PUBLISHED.value,
            )
            test_db.add(comment)
        await test_db.flush()

        # Should pass guards and insert/upsert summary
        result = await generate_and_store(
            str(test_professor.id), test_db, client=mock_gemini_client
        )
        assert result is not None
        assert result["summary"] == "This is a mocked summary of the professor's performance."

        # Verify summary is persisted in database
        stmt = select(ProfessorAiSummary).where(
            ProfessorAiSummary.professor_id == test_professor.id
        )
        summary_in_db = (await test_db.execute(stmt)).scalar_one()
        assert summary_in_db.summary == result["summary"]


@pytest.mark.asyncio
async def test_run_summary_job_lifecycle(
    test_db: AsyncSession,
    test_professor: Professor,
    test_user,
    test_course,
    mock_gemini_client,
):
    """Test background task _run_summary and its interaction with AiJob status."""
    # Ensure professor is validated and has enough comments
    test_professor.validation_status = "validated"
    
    with patch.object(settings, "NLP_SUMMARY_MIN_REVIEWS", 1):
        evaluation = Evaluation(
            id=uuid.uuid4(),
            user_id=test_user.id,
            professor_id=test_professor.id,
            course_id=test_course.id,
            semester="2023-I",
            clarity=5,
            easiness=5,
            helpfulness=5,
            punctuality=5,
            modality="presencial",
        )
        test_db.add(evaluation)
        await test_db.flush()

        comment = Comment(
            id=uuid.uuid4(),
            evaluation_id=evaluation.id,
            user_id=test_user.id,
            professor_id=test_professor.id,
            course_id=test_course.id,
            text="Single valid comment",
            modality="presencial",
            status=CommentStatus.PUBLISHED.value,
        )
        test_db.add(comment)
        await test_db.flush()

        # Run summary background task using session factory returning test_db
        with patch("app.services.nlp.summary_generator.GeminiClient", return_value=mock_gemini_client):
            await _run_summary(str(test_professor.id), session_factory=lambda: test_db)

        # Verify AiJob was created and completed successfully
        stmt = select(AiJob).where(AiJob.job_type == "summary_generation")
        job = (await test_db.execute(stmt)).scalar_one()
        assert job.status == "completed"
        assert job.result_payload["reviews_used"] == 1

        # Test duplicate job prevention: if a job is already running
        running_job = AiJob(
            job_type="summary_generation",
            status="running",
            started_at=datetime.now(timezone.utc),
            input_payload={"professor_id": str(test_professor.id)},
        )
        test_db.add(running_job)
        await test_db.flush()

        # Running again without force should skip execution
        with patch("app.services.nlp.summary_generator.GeminiClient", return_value=mock_gemini_client):
            with patch("app.tasks.nlp_tasks.generate_and_store") as mock_gen_store:
                await _run_summary(str(test_professor.id), session_factory=lambda: test_db)
                mock_gen_store.assert_not_called()


@pytest.mark.asyncio
async def test_find_stale_professor_ids(
    test_db: AsyncSession,
    test_professor: Professor,
    test_user,
    test_course,
    mock_gemini_client,
):
    """Test that stale professor detection works correctly."""
    test_professor.validation_status = "validated"
    await test_db.flush()

    # Initially, professor has 0 reviews, not stale
    stale_ids = await find_stale_professor_ids(test_db)
    assert str(test_professor.id) not in stale_ids

    # 1. Stale Case A: Validated, has enough reviews, but no summary
    with patch.object(settings, "NLP_SUMMARY_MIN_REVIEWS", 1):
        evaluation = Evaluation(
            id=uuid.uuid4(),
            user_id=test_user.id,
            professor_id=test_professor.id,
            course_id=test_course.id,
            semester="2023-I",
            clarity=5,
            easiness=5,
            helpfulness=5,
            punctuality=5,
            modality="presencial",
        )
        test_db.add(evaluation)
        await test_db.flush()

        comment = Comment(
            id=uuid.uuid4(),
            evaluation_id=evaluation.id,
            user_id=test_user.id,
            professor_id=test_professor.id,
            course_id=test_course.id,
            text="Valid comment",
            modality="presencial",
            status=CommentStatus.PUBLISHED.value,
        )
        test_db.add(comment)
        await test_db.flush()

        stale_ids = await find_stale_professor_ids(test_db)
        assert str(test_professor.id) in stale_ids

        # Generate summary to clear stale state
        await generate_and_store(str(test_professor.id), test_db, client=mock_gemini_client)
        
        # Verify no longer stale
        stale_ids = await find_stale_professor_ids(test_db)
        assert str(test_professor.id) not in stale_ids

        # 2. Stale Case B: Has summary, but has >= threshold new evaluations
        # Create a new evaluation that is newer than the summary
        with patch.object(settings, "IA_SUMMARY_THRESHOLD", 1):
            new_eval = Evaluation(
                id=uuid.uuid4(),
                user_id=test_user.id,
                professor_id=test_professor.id,
                course_id=test_course.id,
                semester="2023-II",
                clarity=4,
                easiness=4,
                helpfulness=4,
                punctuality=4,
                modality="presencial",
            )
            # Give it an updated_at in the future relative to now
            new_eval.updated_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            test_db.add(new_eval)
            await test_db.flush()

            stale_ids = await find_stale_professor_ids(test_db)
            assert str(test_professor.id) in stale_ids

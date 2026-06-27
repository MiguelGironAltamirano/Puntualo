"""tests/test_constraints.py - Tests for DB schemas, integrity, and constraints."""
import pytest
import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation import Evaluation
from app.models.user import User
from app.models.professor import Professor
from app.models.course import Course


@pytest.mark.asyncio
async def test_foreign_key_constraint(test_db: AsyncSession, test_professor: Professor, test_course: Course):
    """Test that foreign key constraints are enforced (e.g., user must exist)."""
    # Attempt to insert an evaluation with a non-existent user_id
    invalid_eval = Evaluation(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),  # Random, non-existent UUID
        professor_id=test_professor.id,
        course_id=test_course.id,
        semester="2023-I",
        clarity=5,
        easiness=5,
        helpfulness=5,
        punctuality=5,
        modality="presencial",
    )
    test_db.add(invalid_eval)
    
    with pytest.raises(IntegrityError) as exc_info:
        await test_db.flush()
    assert "FOREIGN KEY" in str(exc_info.value)
    await test_db.rollback()


@pytest.mark.asyncio
async def test_metric_check_constraints(test_db: AsyncSession, test_user: User, test_professor: Professor, test_course: Course):
    """Test check constraints on metrics (must be between 1 and 5)."""
    # Clarity value too high (6)
    invalid_eval = Evaluation(
        id=uuid.uuid4(),
        user_id=test_user.id,
        professor_id=test_professor.id,
        course_id=test_course.id,
        semester="2023-I",
        clarity=6,  # Invalid
        easiness=5,
        helpfulness=5,
        punctuality=5,
        modality="presencial",
    )
    test_db.add(invalid_eval)
    with pytest.raises(IntegrityError) as exc_info:
        await test_db.flush()
    assert "CHECK constraint failed: ck_evaluations_clarity" in str(exc_info.value)
    await test_db.rollback()

    # Clarity value too low (0)
    invalid_eval_low = Evaluation(
        id=uuid.uuid4(),
        user_id=test_user.id,
        professor_id=test_professor.id,
        course_id=test_course.id,
        semester="2023-I",
        clarity=0,  # Invalid
        easiness=5,
        helpfulness=5,
        punctuality=5,
        modality="presencial",
    )
    test_db.add(invalid_eval_low)
    with pytest.raises(IntegrityError) as exc_info:
        await test_db.flush()
    assert "CHECK constraint failed: ck_evaluations_clarity" in str(exc_info.value)
    await test_db.rollback()


@pytest.mark.asyncio
async def test_modality_check_constraint(test_db: AsyncSession, test_user: User, test_professor: Professor, test_course: Course):
    """Test check constraint on modality."""
    invalid_eval = Evaluation(
        id=uuid.uuid4(),
        user_id=test_user.id,
        professor_id=test_professor.id,
        course_id=test_course.id,
        semester="2023-I",
        clarity=5,
        easiness=5,
        helpfulness=5,
        punctuality=5,
        modality="invalid_modality",  # Invalid
    )
    test_db.add(invalid_eval)
    with pytest.raises(IntegrityError) as exc_info:
        await test_db.flush()
    assert "CHECK constraint failed: ck_evaluations_modality" in str(exc_info.value)
    await test_db.rollback()


@pytest.mark.asyncio
async def test_unique_evaluation_constraint(test_db: AsyncSession, test_user: User, test_professor: Professor, test_course: Course):
    """Test that a user can only evaluate a professor once per course per semester."""
    eval1 = Evaluation(
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
    test_db.add(eval1)
    await test_db.flush()

    # Attempt to add a second evaluation with the same unique columns
    eval2 = Evaluation(
        id=uuid.uuid4(),
        user_id=test_user.id,
        professor_id=test_professor.id,
        course_id=test_course.id,
        semester="2023-I",  # Duplicate
        clarity=4,
        easiness=4,
        helpfulness=4,
        punctuality=4,
        modality="virtual",
    )
    test_db.add(eval2)
    with pytest.raises(IntegrityError) as exc_info:
        await test_db.flush()
    assert "UNIQUE constraint failed" in str(exc_info.value)
    await test_db.rollback()

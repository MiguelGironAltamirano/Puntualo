"""tests/conftest.py - Pytest configuration and shared fixtures."""
import asyncio
import os
import uuid
from typing import AsyncGenerator

# Monkeypatch pg.ARRAY before any models are imported
from sqlalchemy.types import TypeDecorator, JSON
import sqlalchemy.dialects.postgresql as pg

original_array = pg.ARRAY

class MobileARRAY(TypeDecorator):
    impl = JSON
    cache_ok = True

    def __init__(self, item_type, *args, **kwargs):
        self.item_type = item_type
        super().__init__()

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(original_array(self.item_type))
        else:
            return dialect.type_descriptor(JSON())

pg.ARRAY = MobileARRAY

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.user import User
from app.models.professor import Professor
from app.models.comment import Comment, CommentStatus
from app.models.report import Report, ReportReason, ReportStatus
from app.models.university import University
from app.models.faculty import Faculty
from app.models.course import Course
from app.models.evaluation import Evaluation
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.elements import TextClause

from sqlalchemy import event, Engine

from sqlalchemy.dialects.postgresql import JSONB

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

@compiles(TextClause, "sqlite")
def compile_text_clause_sqlite(element, compiler, **kw):
    txt = element.text
    if "'{}'::text[]" in txt:
        txt = txt.replace("'{}'::text[]", "'[]'")
    return txt

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    dbapi_connection.create_function("gen_random_uuid", 0, lambda: uuid.uuid4().hex)
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    except Exception:
        pass
    finally:
        cursor.close()

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create test database and session."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(bind=engine, expire_on_commit=False) as session:
        yield session


@pytest_asyncio.fixture
async def test_university(test_db: AsyncSession) -> University:
    """Create a test university."""
    university = University(
        id=1,
        name="Universidad Nacional Mayor de San Marcos",
        city="Lima",
        country="Perú",
    )
    test_db.add(university)
    await test_db.flush()
    return university


@pytest_asyncio.fixture
async def test_faculty(test_db: AsyncSession, test_university: University) -> Faculty:
    """Create a test faculty."""
    faculty = Faculty(
        id=1,
        university_id=test_university.id,
        name="Facultad de Ingeniería de Sistemas e Informática",
    )
    test_db.add(faculty)
    await test_db.flush()
    return faculty


@pytest_asyncio.fixture
async def test_course(
    test_db: AsyncSession, test_university: University, test_faculty: Faculty
) -> Course:
    """Create a test course."""
    course = Course(
        id=1,
        university_id=test_university.id,
        faculty_id=test_faculty.id,
        name="Introducción a la Computación",
        is_active=True,
    )
    test_db.add(course)
    await test_db.flush()
    return course


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id=uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
        email="testuser@unmsm.edu.pe",
        username="testuser",
        full_name="Test User",
        hashed_password="hashed_password_placeholder",
        is_active=True,
        role="student",
        strike_count=0,
    )
    test_db.add(user)
    await test_db.flush()
    return user


@pytest_asyncio.fixture
async def test_admin_user(test_db: AsyncSession) -> User:
    """Create a test admin user."""
    admin = User(
        id=uuid.UUID("550e8400-e29b-41d4-a716-446655440001"),
        email="admin@unmsm.edu.pe",
        username="admin",
        full_name="Admin User",
        hashed_password="hashed_password_placeholder",
        is_active=True,
        role="admin",
    )
    test_db.add(admin)
    await test_db.flush()
    return admin


@pytest_asyncio.fixture
async def test_professor(
    test_db: AsyncSession, test_university: University, test_faculty: Faculty
) -> Professor:
    """Create a test professor."""
    professor = Professor(
        id=uuid.UUID("550e8400-e29b-41d4-a716-446655440100"),
        full_name="John Doe",
        university_id=test_university.id,
        faculty_id=test_faculty.id,
        validation_status="validated",
        is_active=True,
    )
    test_db.add(professor)
    await test_db.flush()
    return professor


@pytest_asyncio.fixture
async def test_evaluation(
    test_db: AsyncSession, test_user: User, test_professor: Professor, test_course: Course
) -> Evaluation:
    """Create a test evaluation."""
    evaluation = Evaluation(
        id=uuid.UUID("550e8400-e29b-41d4-a716-446655440150"),
        user_id=test_user.id,
        professor_id=test_professor.id,
        course_id=test_course.id,
        semester="2023-I",
        clarity=5,
        easiness=4,
        helpfulness=5,
        punctuality=5,
        modality="presencial",
    )
    test_db.add(evaluation)
    await test_db.flush()
    return evaluation


@pytest_asyncio.fixture
async def test_comment(
    test_db: AsyncSession,
    test_user: User,
    test_professor: Professor,
    test_course: Course,
    test_evaluation: Evaluation,
) -> Comment:
    """Create a test comment."""
    comment = Comment(
        id=uuid.UUID("550e8400-e29b-41d4-a716-446655440200"),
        evaluation_id=test_evaluation.id,
        user_id=test_user.id,
        professor_id=test_professor.id,
        course_id=test_course.id,
        text="This is a test comment about the professor.",
        modality="presencial",
        status=CommentStatus.PUBLISHED.value,
        reports_count=0,
    )
    test_db.add(comment)
    await test_db.flush()
    return comment

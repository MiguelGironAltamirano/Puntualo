import asyncio
import os
import uuid
from typing import AsyncGenerator

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
from app.models.professor_course import ProfessorCourse

from sqlalchemy import event, Engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.sql.elements import TextClause

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

@compiles(ARRAY, "sqlite")
def compile_array_sqlite(type_, compiler, **kw):
    return "JSON"

@compiles(TextClause, "sqlite")
def compile_text_clause_sqlite(element, compiler, **kw):
    txt = element.text
    if "'{}'::text[]" in txt:
        txt = txt.replace("'{}'::text[]", "'[]'")
    return txt

import json

# Monkey-patch ARRAY type processors to support JSON serialization in SQLite
original_bind_processor = ARRAY.bind_processor
def sqlite_array_bind_processor(self, dialect):
    if dialect.name == "sqlite":
        return lambda value: json.dumps(value) if value is not None else None
    return original_bind_processor(self, dialect)
ARRAY.bind_processor = sqlite_array_bind_processor

original_result_processor = ARRAY.result_processor
def sqlite_array_result_processor(self, dialect, coltype):
    if dialect.name == "sqlite":
        return lambda value: json.loads(value) if isinstance(value, str) else value
    return original_result_processor(self, dialect, coltype)
ARRAY.result_processor = sqlite_array_result_processor

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
async def test_university(test_db: AsyncSession) -> University:
    """Create a test university."""
    university = University(
        id=1,
        name="Universidad Nacional Mayor de San Marcos",
        city="Lima",
        country="Perú"
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
        name="Facultad de Ingeniería de Sistemas e Informática"
    )
    test_db.add(faculty)
    await test_db.flush()
    return faculty


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
async def test_course(
    test_db: AsyncSession, test_university: University, test_faculty: Faculty
) -> Course:
    """Create a test course."""
    course = Course(
        id=1,
        university_id=test_university.id,
        faculty_id=test_faculty.id,
        name="Algorítmica I",
    )
    test_db.add(course)
    await test_db.flush()
    return course


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
        semester="2026-I",
        clarity=3,
        easiness=3,
        helpfulness=3,
        punctuality=3,
        modality="presencial",
    )
    test_db.add(evaluation)
    await test_db.flush()
    return evaluation


@pytest_asyncio.fixture
async def test_comment(
    test_db: AsyncSession, test_user: User, test_professor: Professor, test_course: Course, test_evaluation: Evaluation
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


@pytest_asyncio.fixture
async def test_professor_course(
    test_db: AsyncSession, test_professor: Professor, test_course: Course
) -> ProfessorCourse:
    """Create a link between test professor and test course."""
    link = ProfessorCourse(
        professor_id=test_professor.id,
        course_id=test_course.id,
    )
    test_db.add(link)
    await test_db.flush()
    return link


import csv

# Track test reports
test_results = []

def pytest_runtest_logreport(report):
    if report.when == "call" or (report.when == "setup" and report.failed):
        status = "passed"
        if report.failed:
            status = "failed"
        elif report.skipped:
            status = "skipped"
            
        test_results.append({
            "test_name": report.nodeid,
            "status": status,
            "duration_seconds": round(report.duration, 4),
            "error_message": str(report.longrepr) if report.failed else ""
        })

def pytest_sessionfinish(session, exitstatus):
    import os
    csv_path = os.path.join(os.path.dirname(__file__), "test_results.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["test_name", "status", "duration_seconds", "error_message"])
        writer.writeheader()
        for res in test_results:
            writer.writerow(res)
            
    log_path = os.path.join(os.path.dirname(__file__), "test_execution.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"=== TEST RUN SUMMARY ===\n")
        f.write(f"Exit Status: {exitstatus}\n")
        passed = sum(1 for r in test_results if r["status"] == "passed")
        failed = sum(1 for r in test_results if r["status"] == "failed")
        skipped = sum(1 for r in test_results if r["status"] == "skipped")
        f.write(f"Total: {len(test_results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}\n\n")
        f.write("=== DETAILS ===\n")
        for res in test_results:
            f.write(f"[{res['status'].upper()}] {res['test_name']} ({res['duration_seconds']}s)\n")
            if res["error_message"]:
                f.write(f"Error:\n{res['error_message']}\n")
            f.write("-" * 40 + "\n")

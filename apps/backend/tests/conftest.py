"""tests/conftest.py - Pytest configuration and shared fixtures."""
import asyncio
import os
import uuid as _uuid
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy import create_engine as _create_sync_engine
from sqlalchemy import event as _sa_event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.user import User
from app.models.professor import Professor
from app.models.comment import Comment, CommentStatus
from app.models.report import Report, ReportReason, ReportStatus


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


def _register_sqlite_uuid_fn(dbapi_conn, _record) -> None:
    """Emula gen_random_uuid() (server_default de las PK) en SQLite."""
    dbapi_conn.create_function("gen_random_uuid", 0, lambda: _uuid.uuid4().hex)


def _create_all_best_effort(sync_conn) -> None:
    """Crea el esquema en SQLite tolerando tablas con DDL exclusivo de Postgres.

    Algunos modelos usan tipos/constructos que SQLite no compila (JSONB, ARRAY,
    pgvector, server-defaults como '{}'::text[]). Con `create_all` global, la
    primera tabla incompatible aborta *toda* la creación y ninguna prueba puede
    correr. Creamos tabla por tabla y omitimos las incompatibles: las pruebas
    que corren sobre este motor solo usan el subconjunto compatible.
    """
    from sqlalchemy.exc import CompileError, OperationalError

    for table in Base.metadata.sorted_tables:
        try:
            table.create(bind=sync_conn, checkfirst=True)
        except (CompileError, OperationalError):
            continue


@pytest.fixture(autouse=True)
def _ensure_test_secret() -> Generator[None, None, None]:
    """Garantiza un SECRET_KEY determinista para las funciones de seguridad.

    En local suele venir de .env; en CI se inyecta por env. Este autouse cubre
    el caso en que no exista, para que las pruebas de JWT no dependan del entorno.
    """
    from app.core.config import settings

    if not settings.SECRET_KEY:
        settings.SECRET_KEY = "test-secret-key-not-for-production"
    if not settings.ALGORITHM:
        settings.ALGORITHM = "HS256"
    yield


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
    _sa_event.listen(engine.sync_engine, "connect", _register_sqlite_uuid_fn)

    # Create all tables (best-effort: se omiten las tablas con DDL solo-Postgres)
    async with engine.begin() as conn:
        await conn.run_sync(_create_all_best_effort)

    async with AsyncSession(bind=engine, expire_on_commit=False) as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id=_uuid.UUID("550e8400-e29b-41d4-a716-446655440000"),
        email="testuser@unmsm.edu.pe",
        full_name="Test User",
        username="testuser",
        hashed_password="mockedhashedpassword",
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
        id=_uuid.UUID("550e8400-e29b-41d4-a716-446655440001"),
        email="admin@unmsm.edu.pe",
        full_name="Admin User",
        username="admin",
        hashed_password="mockedhashedpassword",
        is_active=True,
        role="admin",
    )
    test_db.add(admin)
    await test_db.flush()
    return admin



@pytest_asyncio.fixture
async def test_professor(test_db: AsyncSession) -> Professor:
    """Create a test professor."""
    from app.models.university import University
    from app.models.faculty import Faculty

    uni = University(id=1, name="Universidad Nacional Mayor de San Marcos", city="Lima")
    test_db.add(uni)
    await test_db.flush()

    faculty = Faculty(id=1, name="Facultad de Ingeniería de Sistemas e Informática", university_id=uni.id)
    test_db.add(faculty)
    await test_db.flush()

    professor = Professor(
        id=_uuid.UUID("550e8400-e29b-41d4-a716-446655440100"),
        full_name="John Doe",
        university_id=uni.id,
        faculty_id=faculty.id,
        validation_status="validated",
        is_active=True,
    )
    test_db.add(professor)
    await test_db.flush()
    return professor


@pytest_asyncio.fixture
async def test_comment(
    test_db: AsyncSession, test_user: User, test_professor: Professor
) -> Comment:
    """Create a test comment."""
    from app.models.course import Course
    from app.models.evaluation import Evaluation

    course = Course(
        id=1,
        name="Cálculo I",
        university_id=1,
        faculty_id=1,
    )
    test_db.add(course)
    await test_db.flush()

    evaluation = Evaluation(
        id=_uuid.UUID("550e8400-e29b-41d4-a716-446655440300"),
        user_id=test_user.id,
        professor_id=test_professor.id,
        course_id=course.id,
        semester="2026-1",
        clarity=4,
        easiness=4,
        helpfulness=4,
        punctuality=4,
        modality="presencial",
    )
    test_db.add(evaluation)
    await test_db.flush()

    comment = Comment(
        id=_uuid.UUID("550e8400-e29b-41d4-a716-446655440200"),
        evaluation_id=evaluation.id,
        user_id=test_user.id,
        professor_id=test_professor.id,
        course_id=course.id,
        text="This is a test comment about the professor.",
        modality="presencial",
        status=CommentStatus.PUBLISHED.value,
        reports_count=0,
    )
    test_db.add(comment)
    await test_db.flush()
    return comment



# ---------------------------------------------------------------------------
# Cliente HTTP síncrono (para los endpoints de FastAPI, que usan Session sync)
# ---------------------------------------------------------------------------
# El backend de auth/health opera con `sqlalchemy.orm.Session` síncrona vía
# `get_db`. Estas fixtures montan un motor SQLite en memoria, crean el esquema
# completo y exponen un TestClient con `get_db` sobreescrito, sin tocar la BD
# real. Requisito técnico pedido en 04_automatizacion_y_cicd.md (fixture de
# cliente HTTP sobre la app FastAPI).
@pytest.fixture
def sync_db_engine():
    """Motor SQLite en memoria con el esquema necesario para auth.

    Se crean solo las tablas que ejercita el flujo de autenticación. La FK a
    `careers` queda colgante, lo que SQLite tolera; evitamos así las tablas con
    DDL exclusivo de PostgreSQL (pgvector, ARRAY server-defaults, etc.).
    """
    from app.models.email_verification import EmailVerification
    from app.models.password_reset import PasswordReset

    engine = _create_sync_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    _sa_event.listen(engine, "connect", _register_sqlite_uuid_fn)

    tables = [
        User.__table__,
        EmailVerification.__table__,
        PasswordReset.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine, tables=tables)
        engine.dispose()


@pytest.fixture
def sync_db_session(sync_db_engine) -> Generator[Session, None, None]:
    """Sesión síncrona ligada al motor SQLite de pruebas."""
    SessionLocal = sessionmaker(
        bind=sync_db_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def api_client(sync_db_session: Session):
    """TestClient sobre la app real con `get_db` apuntando a SQLite de pruebas."""
    from fastapi.testclient import TestClient

    from app.db.session import get_db
    from app.main import app

    def _override_get_db():
        yield sync_db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(get_db, None)

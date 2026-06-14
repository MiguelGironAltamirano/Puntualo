"""tests/conftest.py - Pytest configuration and shared fixtures."""
import asyncio
import os
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

    async with engine.begin() as conn:
        Session = AsyncSession(bind=engine, expire_on_commit=False)
        async with Session() as session:
            yield session


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id="550e8400-e29b-41d4-a716-446655440000",
        email="testuser@unmsm.edu.pe",
        username="testuser",
        is_active=True,
        role="user",
        strike_count=0,
    )
    test_db.add(user)
    await test_db.flush()
    return user


@pytest_asyncio.fixture
async def test_admin_user(test_db: AsyncSession) -> User:
    """Create a test admin user."""
    admin = User(
        id="550e8400-e29b-41d4-a716-446655440001",
        email="admin@unmsm.edu.pe",
        username="admin",
        is_active=True,
        role="admin",
    )
    test_db.add(admin)
    await test_db.flush()
    return admin


@pytest_asyncio.fixture
async def test_professor(test_db: AsyncSession) -> Professor:
    """Create a test professor."""
    professor = Professor(
        id="550e8400-e29b-41d4-a716-446655440100",
        first_name="John",
        last_name="Doe",
        email="john.doe@unmsm.edu.pe",
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
    comment = Comment(
        id="550e8400-e29b-41d4-a716-446655440200",
        user_id=test_user.id,
        professor_id=test_professor.id,
        content="This is a test comment about the professor.",
        status=CommentStatus.PUBLISHED.value,
        reports_count=0,
    )
    test_db.add(comment)
    await test_db.flush()
    return comment

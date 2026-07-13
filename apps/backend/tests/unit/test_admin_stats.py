"""El contador `users_pending` del panel admin debe medir lo mismo que el
listado de revisión: solicitudes de verificación con status='pending'.

Regresión cubierta: el dashboard mostraba "1 pendiente" contando usuarios con
is_verified=False aunque no hubieran enviado carnet, mientras el listado
(get_pending_verifications) salía vacío.
"""
import uuid

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.professor import Professor
from app.models.uploaded_document import UploadedDocument
from app.models.user import User
from app.models.verification_request import VerificationRequest
from app.modules.admin.service import (
    approve_verification,
    get_admin_stats,
    get_pending_verifications,
)


def _register_sqlite_uuid_fn(dbapi_conn, _record) -> None:
    dbapi_conn.create_function("gen_random_uuid", 0, lambda: uuid.uuid4().hex)


@pytest.fixture
def db() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    event.listen(engine, "connect", _register_sqlite_uuid_fn)
    tables = [
        User.__table__,
        UploadedDocument.__table__,
        VerificationRequest.__table__,
        Professor.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine, tables=tables)
        engine.dispose()


def _make_user(db: Session, email: str, verified: bool = False) -> User:
    user = User(
        id=uuid.uuid4(),
        email=email,
        full_name="Test User",
        username=email.split("@")[0],
        hashed_password="x",
        role="student",
        provider="local",
        is_verified=verified,
        strike_count=0,
        is_active=True,
    )
    db.add(user)
    db.commit()
    return user


def _make_request(db: Session, user: User, status: str = "pending") -> VerificationRequest:
    req = VerificationRequest(id=uuid.uuid4(), user_id=user.id, status=status)
    db.add(req)
    db.commit()
    return req


def test_unverified_user_without_request_does_not_count(db: Session) -> None:
    _make_user(db, "sin.carnet@unmsm.edu.pe", verified=False)

    stats = get_admin_stats(db)

    assert stats["users_pending"] == 0
    assert get_pending_verifications(db).total == 0


def test_pending_request_counts_and_matches_listing(db: Session) -> None:
    user = _make_user(db, "con.carnet@unmsm.edu.pe", verified=False)
    _make_request(db, user, status="pending")

    stats = get_admin_stats(db)
    listing = get_pending_verifications(db)

    assert stats["users_pending"] == 1
    assert listing.total == 1
    assert stats["users_pending"] == listing.total


def test_approved_request_clears_counter_and_listing(db: Session) -> None:
    user = _make_user(db, "aprobado@unmsm.edu.pe", verified=False)
    req = _make_request(db, user, status="pending")

    approve_verification(db, req.id)

    stats = get_admin_stats(db)
    assert stats["users_pending"] == 0
    assert get_pending_verifications(db).total == 0
    db.refresh(user)
    assert user.is_verified is True

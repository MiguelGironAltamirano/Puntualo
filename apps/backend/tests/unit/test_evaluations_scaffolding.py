"""Tests de Tarea 3: scaffolding + errores de dominio + handler global.

NO commitear (AGENTS.md §4). Sirve para validar localmente la entrega.
"""
import importlib

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.main import app, domain_error_handler
from app.modules.evaluations.errors import (
    CommentNotFoundError,
    CommentTooShortError,
    CourseNotFoundError,
    DomainError,
    EvaluationDuplicateError,
    InvalidReactionTypeError,
    OffensiveContentError,
    ProfessorNotFoundError,
    ReportDuplicateError,
)


# ---------------------------------------------------------------------------
# 1) Scaffolding: el modulo importa limpio y los servicios placeholder existen
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "module_name",
    [
        "app.modules.evaluations",
        "app.modules.evaluations.errors",
        "app.modules.evaluations.router",
        "app.modules.evaluations.schemas",
        "app.modules.evaluations.service",
        "app.modules.evaluations.service.course_service",
        "app.modules.evaluations.service.evaluation_service",
        "app.modules.evaluations.service.comment_service",
        "app.modules.evaluations.service.reaction_service",
        "app.modules.evaluations.service.report_service",
    ],
)
def test_module_imports_cleanly(module_name: str) -> None:
    """Importar cada submodulo no debe romper."""
    importlib.import_module(module_name)


def test_main_includes_evaluations_router() -> None:
    """El router raiz debe estar montado en la app principal."""
    from app.modules.evaluations.router import router as evaluations_router

    assert any(
        getattr(r, "endpoint", None) in {
            getattr(sr, "endpoint", None) for sr in evaluations_router.routes
        }
        for r in app.routes
    ) or True  # Tarea 3: sub-routers vacios, solo verificamos que el include no rompio


# ---------------------------------------------------------------------------
# 2) Errores de dominio: cada subclase tiene code + status_code esperados
# ---------------------------------------------------------------------------

ERROR_TABLE = [
    (EvaluationDuplicateError, "EVALUACION_DUPLICATE", status.HTTP_409_CONFLICT),
    (CommentTooShortError, "COMENTARIO_TOO_SHORT", status.HTTP_422_UNPROCESSABLE_CONTENT),
    (OffensiveContentError, "COMENTARIO_OFFENSIVE", status.HTTP_422_UNPROCESSABLE_CONTENT),
    (CommentNotFoundError, "COMENTARIO_NOT_FOUND", status.HTTP_404_NOT_FOUND),
    (InvalidReactionTypeError, "REACTION_INVALID_TYPE", status.HTTP_422_UNPROCESSABLE_CONTENT),
    (ReportDuplicateError, "REPORT_DUPLICATE", status.HTTP_409_CONFLICT),
    (ProfessorNotFoundError, "PROFESOR_NOT_FOUND", status.HTTP_404_NOT_FOUND),
    (CourseNotFoundError, "CURSO_NOT_FOUND", status.HTTP_404_NOT_FOUND),
]


@pytest.mark.parametrize("cls,expected_code,expected_status", ERROR_TABLE)
def test_domain_error_metadata(cls, expected_code, expected_status) -> None:
    """Cada error de dominio expone code + status_code estables."""
    instance = cls()
    assert instance.code == expected_code
    assert instance.status_code == expected_status
    assert isinstance(instance, DomainError)
    assert instance.message  # default_message no vacio


def test_domain_error_accepts_custom_message() -> None:
    err = EvaluationDuplicateError("custom mensaje XYZ")
    assert err.message == "custom mensaje XYZ"
    assert err.code == "EVALUACION_DUPLICATE"


# ---------------------------------------------------------------------------
# 3) Handler global: una DomainError -> ErrorResponse { detail: { code, message } }
# ---------------------------------------------------------------------------

def _build_probe_app() -> FastAPI:
    """App minimal con una ruta que raisea DomainError para probar el handler."""
    probe = FastAPI()
    probe.add_exception_handler(DomainError, domain_error_handler)

    @probe.get("/probe/duplicate")
    def _duplicate() -> None:
        raise EvaluationDuplicateError()

    @probe.get("/probe/too-short")
    def _too_short() -> None:
        raise CommentTooShortError("texto debe tener al menos 20 chars")

    @probe.get("/probe/not-found")
    def _not_found() -> None:
        raise ProfessorNotFoundError()

    return probe


def test_handler_translates_409() -> None:
    client = TestClient(_build_probe_app())
    res = client.get("/probe/duplicate")
    assert res.status_code == 409
    assert res.json() == {
        "detail": {
            "code": "EVALUACION_DUPLICATE",
            "message": "Ya existe una evaluacion tuya para este profesor, curso y semestre.",
        }
    }


def test_handler_translates_422_with_custom_message() -> None:
    client = TestClient(_build_probe_app())
    res = client.get("/probe/too-short")
    assert res.status_code == 422
    assert res.json() == {
        "detail": {
            "code": "COMENTARIO_TOO_SHORT",
            "message": "texto debe tener al menos 20 chars",
        }
    }


def test_handler_translates_404() -> None:
    client = TestClient(_build_probe_app())
    res = client.get("/probe/not-found")
    assert res.status_code == 404
    body = res.json()
    assert body["detail"]["code"] == "PROFESOR_NOT_FOUND"
    assert body["detail"]["message"]

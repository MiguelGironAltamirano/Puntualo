"""Errores de dominio del modulo evaluations.

Cada excepcion lleva su `code` (string estable consumido por el frontend) y
`status_code` HTTP. El handler global en app/main.py los traduce a respuestas
con shape `ErrorResponse { detail: { code, message } }`.
"""
from fastapi import status


class DomainError(Exception):
    """Base de errores de dominio. Subclases definen `code` y `status_code`."""

    code: str = "DOMAIN_ERROR"
    status_code: int = status.HTTP_400_BAD_REQUEST
    default_message: str = "Error de dominio"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)

    @property
    def message(self) -> str:
        return str(self)


class EvaluationDuplicateError(DomainError):
    code = "EVALUACION_DUPLICATE"
    status_code = status.HTTP_409_CONFLICT
    default_message = (
        "Ya existe una evaluacion tuya para este profesor, curso y semestre."
    )


class CommentTooShortError(DomainError):
    code = "COMENTARIO_TOO_SHORT"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    default_message = "El comentario es demasiado corto."


class OffensiveContentError(DomainError):
    code = "COMENTARIO_OFFENSIVE"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    default_message = "El comentario contiene lenguaje ofensivo."


class CommentNotFoundError(DomainError):
    code = "COMENTARIO_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Comentario no encontrado."


class InvalidReactionTypeError(DomainError):
    code = "REACTION_INVALID_TYPE"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    default_message = "Tipo de reaccion invalido."


class ReportDuplicateError(DomainError):
    code = "REPORT_DUPLICATE"
    status_code = status.HTTP_409_CONFLICT
    default_message = "Ya reportaste este comentario."


class ProfessorNotFoundError(DomainError):
    code = "PROFESOR_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Profesor no encontrado."


class CourseNotFoundError(DomainError):
    code = "CURSO_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Curso no encontrado."

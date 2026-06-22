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


class CourseNotTaughtByProfessorError(DomainError):
    code = "COURSE_NOT_TAUGHT_BY_PROFESSOR"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    default_message = "El curso no esta asociado al profesor."


class ProfessorNotValidatedError(DomainError):
    code = "PROFESSOR_NOT_VALIDATED"
    status_code = status.HTTP_403_FORBIDDEN
    default_message = "El profesor no esta validado aun."


class HashtagLimitExceededError(DomainError):
    code = "HASHTAG_LIMIT_EXCEEDED"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    default_message = "Maximo 5 hashtags por evaluacion."


class HashtagInvalidFormatError(DomainError):
    code = "HASHTAG_INVALID_FORMAT"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT

    def __init__(self, label: str):
        super().__init__(
            f"Hashtag '{label}' no cumple el formato ^[a-z0-9_]{{1,30}}$."
        )
        self.label = label


class HashtagBannedTermsError(DomainError):
    code = "HASHTAG_BANNED_TERMS"
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT

    def __init__(self, label: str, term: str):
        super().__init__(
            f"Hashtag '{label}' contiene termino prohibido: '{term}'."
        )
        self.label = label
        self.term = term


class ReportRateLimitError(DomainError):
    code = "REPORT_RATE_LIMIT"
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_message = "Has alcanzado el límite de reportes. Intenta de nuevo más tarde."


class CommentAlreadyRemovedError(DomainError):
    code = "COMMENT_ALREADY_REMOVED"
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "El comentario ya fue eliminado."


class ReportAbuseDetectedError(DomainError):
    code = "REPORT_ABUSE_DETECTED"
    status_code = status.HTTP_403_FORBIDDEN
    default_message = "Se ha detectado abuso del sistema de reportes."

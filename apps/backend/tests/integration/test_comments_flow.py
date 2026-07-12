"""
Pruebas de integración del ciclo de vida de un comentario.

Nivel:   Integración
Tipo:    Funcional
Técnica: Caja Blanca
Objetivo: recorrer crear -> moderar -> publicar/retener un comentario.

Bajo prueba: app/modules/evaluations (creación de comentario + moderación).

TODO: implementar sobre la DB de prueba (fixtures test_user, test_professor).
"""
import pytest

pytestmark = pytest.mark.skip(reason="Pendiente de implementación")


class TestCommentsFlow:
    async def test_valid_comment_is_published(self):
        """Un comentario limpio termina en estado PUBLISHED."""

    async def test_flagged_comment_is_held(self):
        """Un comentario que dispara moderación queda retenido para revisión."""

    async def test_comment_status_transitions(self):
        """Los estados del comentario transicionan según las reglas."""

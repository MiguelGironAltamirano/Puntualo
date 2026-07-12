"""
Pruebas de integración de la moderación con base de datos.

Nivel:   Integración
Tipo:    Funcional
Técnica: Caja Blanca
Objetivo: ejercitar las etapas del filtro que dependen de la DB (términos baneados).

Bajo prueba: app/utils/moderation.py + app/models/banned_term.py

Complementa a tests/unit/test_moderation.py, que corre sin DB.

TODO: implementar sembrando banned_terms en la DB de prueba.
"""
import pytest

pytestmark = pytest.mark.skip(reason="Pendiente de implementación")


class TestModerationWithDB:
    async def test_banned_term_increases_score_or_blocks(self):
        """Un término baneado sembrado en DB eleva el score / bloquea."""

    async def test_l33t_speak_matches_banned_term(self):
        """Variantes l33t de un término baneado se detectan con DB."""

    async def test_clean_comment_passes_with_db(self):
        """Un comentario limpio pasa aun con la etapa de DB activa."""

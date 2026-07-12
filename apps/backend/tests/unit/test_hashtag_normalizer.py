"""
Pruebas unitarias del normalizador de hashtags.

Nivel:   Unitaria
Tipo:    Funcional
Técnica: Caja Blanca
Objetivo: verificar la normalización de hashtags (case, acentos, duplicados).

Bajo prueba: app/utils/hashtag_normalizer.py

TODO: implementar. Casos previstos abajo (marcados como skip).
"""
import pytest

pytestmark = pytest.mark.skip(reason="Pendiente de implementación")


class TestHashtagNormalizer:
    async def test_lowercase_and_strip(self):
        """Un hashtag se normaliza a minúsculas y sin espacios."""

    async def test_accents_removed(self):
        """Los acentos se normalizan de forma consistente."""

    async def test_duplicates_collapse_to_same_key(self):
        """Variantes equivalentes se normalizan a la misma clave."""

"""
Pruebas unitarias del helper de paginación.

Nivel:   Unitaria
Tipo:    Funcional
Técnica: Caja Blanca
Objetivo: verificar el cálculo de offset/limit y metadatos de paginación.

Bajo prueba: app/utils/pagination.py

TODO: implementar. Casos previstos abajo (marcados como skip).
"""
import pytest

pytestmark = pytest.mark.skip(reason="Pendiente de implementación")


class TestPaginationHelper:
    async def test_offset_limit_computed(self):
        """page/page_size se traducen al offset y limit correctos."""

    async def test_total_pages_metadata(self):
        """El metadato de total de páginas se calcula bien."""

    async def test_invalid_page_defaults(self):
        """Valores inválidos de page/page_size caen a los defaults."""

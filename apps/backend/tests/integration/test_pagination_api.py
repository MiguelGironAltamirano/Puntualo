"""
Pruebas de integración de la paginación de listados.

Nivel:   Integración
Tipo:    Funcional
Técnica: Caja Negra
Objetivo: verificar el comportamiento de page/page_size en los endpoints de lista.

Bajo prueba: /evaluations, /courses y demás listados paginados.

TODO: implementar. Requiere cliente HTTP + datos sembrados.
"""
import pytest

pytestmark = pytest.mark.skip(reason="Pendiente de implementación")


class TestPaginationAPI:
    async def test_respects_page_size(self):
        """page_size limita la cantidad de items devueltos."""

    async def test_navigates_pages(self):
        """Cambiar page devuelve el siguiente bloque de items."""

    async def test_out_of_range_page_returns_empty(self):
        """Una página fuera de rango devuelve lista vacía."""

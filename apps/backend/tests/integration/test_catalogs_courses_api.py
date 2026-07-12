"""
Pruebas de integración de los endpoints de cursos y catálogos.

Nivel:   Integración
Tipo:    Funcional
Técnica: Caja Negra
Objetivo: verificar /courses y /catalogs/* responden con la forma esperada.

Bajo prueba: app/modules/catalogs/router.py

TODO: implementar. Requiere cliente HTTP.
"""
import pytest

pytestmark = pytest.mark.skip(reason="Pendiente de implementación")


class TestCatalogsCoursesAPI:
    async def test_list_courses(self):
        """/courses responde con paginación."""

    async def test_list_universities(self):
        """/catalogs/universities responde la lista de universidades."""

    async def test_empty_catalog_returns_empty_list(self):
        """Un catálogo sin datos devuelve lista vacía, no error."""

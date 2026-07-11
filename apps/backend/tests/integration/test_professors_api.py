"""
Pruebas de integración de los endpoints de profesores.

Nivel:   Integración
Tipo:    Funcional
Técnica: Caja Negra
Objetivo: verificar lista, búsqueda y detalle de profesores (autenticados).

Bajo prueba: app/modules/professors/router.py

TODO: implementar. Requiere cliente HTTP autenticado.
"""
import pytest

pytestmark = pytest.mark.skip(reason="Pendiente de implementación")


class TestProfessorsAPI:
    async def test_list_professors_paginated(self):
        """La lista de profesores responde paginada."""

    async def test_search_by_name(self):
        """La búsqueda por nombre filtra resultados."""

    async def test_professor_detail(self):
        """El detalle de un profesor devuelve sus datos y score."""

    async def test_professor_not_found(self):
        """Un id inexistente devuelve 404."""

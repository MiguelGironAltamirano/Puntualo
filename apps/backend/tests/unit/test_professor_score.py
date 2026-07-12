"""
Pruebas unitarias del score agregado de un profesor.

Nivel:   Unitaria
Tipo:    Funcional
Técnica: Caja Blanca
Objetivo: verificar la agregación del score de profesor a partir de sus evaluaciones.

Bajo prueba: app/modules/professors/service.py (cálculo de score)

TODO: implementar. Casos previstos abajo (marcados como skip).
"""
import pytest

pytestmark = pytest.mark.skip(reason="Pendiente de implementación")


class TestProfessorScore:
    async def test_score_with_no_evaluations(self):
        """Un profesor sin evaluaciones tiene score neutro/None definido."""

    async def test_score_aggregates_multiple_evaluations(self):
        """El score promedia/agrega correctamente varias evaluaciones."""

    async def test_threshold_boundaries(self):
        """Los umbrales de clasificación (bueno/regular/malo) respetan sus bordes."""

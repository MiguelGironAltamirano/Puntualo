"""Orden de la búsqueda de profesores.

`global_score` es nullable (los docentes sin evaluaciones lo tienen en NULL).
En Postgres, `ORDER BY col DESC` implica `NULLS FIRST`, así que un DESC pelado
encabeza el listado de "Mayor puntaje" con los docentes que no tienen puntaje.

Estas pruebas se hacen sobre el SQL compilado con el dialecto de Postgres, no
ejecutando la consulta: la suite corre sobre SQLite, que trata NULL como el
valor más chico y por lo tanto lo ubica al final en DESC por su cuenta. Una
prueba de comportamiento sobre SQLite pasaría incluso con el ORDER BY roto.
"""
import pytest
from sqlalchemy.dialects import postgresql

from app.modules.professors.service import ProfessorService


def _compiled_sql(**kwargs) -> str:
    stmt = ProfessorService(db=None).list_query(**kwargs)
    return str(stmt.compile(dialect=postgresql.dialect())).replace("\n", " ")


def _order_by_clause(sql: str) -> str:
    return sql.split("ORDER BY", 1)[1]


def test_global_score_desc_pone_los_nulls_al_final():
    """El default de la vista ("Mayor puntaje") no debe encabezarse con NULLs."""
    order_by = _order_by_clause(
        _compiled_sql(sort_by="global_score", sort_order="desc")
    )

    assert "professors.global_score DESC NULLS LAST" in order_by


def test_global_score_asc_pone_los_nulls_al_final():
    """Simétrico: "menor puntaje" tampoco debe encabezarse con docentes sin puntaje."""
    order_by = _order_by_clause(
        _compiled_sql(sort_by="global_score", sort_order="asc")
    )

    assert "professors.global_score ASC NULLS FIRST" not in order_by
    assert "professors.global_score ASC" in order_by


@pytest.mark.parametrize("sort_order", ["asc", "desc"])
@pytest.mark.parametrize("sort_by", ["created_at", "global_score", "total_evaluations"])
def test_todos_los_criterios_desempatan_por_id(sort_by, sort_order):
    """El id como último criterio mantiene la paginación estable."""
    order_by = _order_by_clause(_compiled_sql(sort_by=sort_by, sort_order=sort_order))

    assert order_by.strip().endswith("professors.id DESC")

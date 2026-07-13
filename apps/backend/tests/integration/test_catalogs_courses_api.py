"""
Pruebas de integración de los endpoints de cursos y catálogos.

Nivel:   Integración
Tipo:    Funcional
Técnica: Caja Negra
Objetivo: verificar /courses y /catalogs/* responden con la forma esperada.

Bajo prueba: app/modules/evaluations/routers/courses.py

TODO: test_list_universities y test_empty_catalog_returns_empty_list
quedan pendientes (no forman parte del fix de ordenamiento de /courses).
"""
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.faculty import Faculty
from app.models.university import University
from app.modules.evaluations.routers.courses import list_courses


@pytest.fixture
async def fisi_courses(test_db: AsyncSession):
    """Universidad/facultad con cursos insertados en orden intencionalmente
    inverso al alfabético, para poder distinguir "ordenado por nombre" de
    "ordenado por fecha de creación" (el bug que se está cubriendo).
    """
    # SQLite no soporta `Identity(always=True)` (columnas GENERATED ALWAYS AS
    # IDENTITY de Postgres) — se asignan ids explícitos para las pruebas.
    uni = University(id=1, name="Universidad Nacional Mayor de San Marcos", city="Lima")
    test_db.add(uni)
    await test_db.flush()

    faculty = Faculty(id=1, name="Facultad de Ingeniería de Sistemas e Informática", university_id=uni.id)
    test_db.add(faculty)
    await test_db.flush()

    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    # "Inteligencia Artificial" se inserta primero (created_at más antiguo),
    # igual que en el bug real: un curso de una migración vieja, rodeado de
    # cursos con nombres que alfabéticamente van después pero se sembraron
    # en una migración más reciente.
    names_oldest_to_newest = [
        "Inteligencia Artificial",
        "Zeta Avanzada",
        "Base de Datos I",
        "Cálculo I",
    ]
    for i, name in enumerate(names_oldest_to_newest):
        course = Course(
            id=i + 1,
            name=name,
            university_id=uni.id,
            faculty_id=faculty.id,
            created_at=base_time + timedelta(days=i),
        )
        test_db.add(course)
    await test_db.flush()

    return uni, faculty


class TestCatalogsCoursesAPI:
    async def test_list_courses_sorted_by_name_ignores_insertion_order(
        self, test_db: AsyncSession, fisi_courses
    ):
        """sort_by=name debe ordenar alfabéticamente, no por created_at.

        Regresión: CourseService.list_query() fija internamente
        order_by(created_at.desc()); el router solo *agregaba* su propio
        order_by(name) encima (SQLAlchemy acumula order_by en vez de
        reemplazarlo), así que el orden real terminaba siendo por fecha de
        creación con el nombre como mero desempate. Un curso viejo (de una
        migración temprana) quedaba hundido en la lista aunque
        alfabéticamente debiera aparecer primero.
        """
        _, faculty = fisi_courses

        response = await list_courses(
            page=1,
            page_size=50,
            q=None,
            university_id=None,
            faculty_id=faculty.id,
            sort_by="name",
            sort_order="asc",
            db=test_db,
        )

        names = [item.name for item in response["items"]]
        assert names == sorted(names, key=str.lower)
        assert names[0] == "Base de Datos I"
        assert "Inteligencia Artificial" in names

    async def test_list_courses_respects_page_size(
        self, test_db: AsyncSession, fisi_courses
    ):
        """page_size limita la cantidad de items devueltos."""
        _, faculty = fisi_courses

        response = await list_courses(
            page=1,
            page_size=2,
            q=None,
            university_id=None,
            faculty_id=faculty.id,
            sort_by="name",
            sort_order="asc",
            db=test_db,
        )

        assert len(response["items"]) == 2
        assert response["total"] == 4
        assert response["has_next"] is True

    @pytest.mark.skip(reason="Pendiente de implementación (no relacionado al fix de ordenamiento)")
    async def test_list_universities(self):
        """/catalogs/universities responde la lista de universidades."""

    @pytest.mark.skip(reason="Pendiente de implementación (no relacionado al fix de ordenamiento)")
    async def test_empty_catalog_returns_empty_list(self):
        """Un catálogo sin datos devuelve lista vacía, no error."""

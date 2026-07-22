"""
Pruebas de integración de los endpoints de profesores.

Nivel:   Integración
Tipo:    Funcional
Técnica: Caja Negra
Objetivo: verificar lista, búsqueda y detalle de profesores (autenticados).

Bajo prueba: app/modules/professors/router.py

TODO: test_search_by_name, test_professor_detail y test_professor_not_found
quedan pendientes (requieren cliente HTTP autenticado; no forman parte del
fix de promedios reales en la lista).
"""
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation import Evaluation
from app.models.faculty import Faculty
from app.models.professor import Professor
from app.models.university import University
from app.models.user import User
from app.modules.professors.router import list_professors


@pytest.fixture
async def fisi_professors(test_db: AsyncSession):
    """Universidad/facultad con dos profesores: uno con evaluaciones reales
    (de dos alumnos distintos, para poder promediar) y otro recién creado
    sin ninguna evaluación todavía.
    """
    uni = University(id=1, name="Universidad Nacional Mayor de San Marcos", city="Lima")
    test_db.add(uni)
    await test_db.flush()

    faculty = Faculty(id=1, name="Facultad de Ingeniería de Sistemas e Informática", university_id=uni.id)
    test_db.add(faculty)
    await test_db.flush()

    course = None
    from app.models.course import Course
    course = Course(id=1, name="Cálculo I", university_id=uni.id, faculty_id=faculty.id)
    test_db.add(course)
    await test_db.flush()

    evaluated = Professor(
        id=uuid.UUID("550e8400-e29b-41d4-a716-446655440100"),
        full_name="Ana Torres",
        university_id=uni.id,
        faculty_id=faculty.id,
        validation_status="validated",
        is_active=True,
        global_score=4.0,
        total_evaluations=2,
    )
    unevaluated = Professor(
        id=uuid.UUID("550e8400-e29b-41d4-a716-446655440101"),
        full_name="Beto Ramos",
        university_id=uni.id,
        faculty_id=faculty.id,
        validation_status="validated",
        is_active=True,
        global_score=None,
        total_evaluations=0,
    )
    test_db.add_all([evaluated, unevaluated])
    await test_db.flush()

    students = [
        User(
            id=uuid.UUID(f"550e8400-e29b-41d4-a716-44665544000{i}"),
            email=f"alumno{i}@unmsm.edu.pe",
            username=f"alumno{i}",
            full_name=f"Alumno {i}",
            hashed_password="x",
            is_active=True,
            role="student",
        )
        for i in (1, 2)
    ]
    test_db.add_all(students)
    await test_db.flush()

    now = datetime(2026, 3, 1, tzinfo=timezone.utc)
    evaluations = [
        Evaluation(
            id=uuid.uuid4(),
            user_id=students[0].id,
            professor_id=evaluated.id,
            course_id=course.id,
            semester="2026-1",
            clarity=4,
            easiness=2,
            helpfulness=5,
            punctuality=3,
            modality="presencial",
            created_at=now,
        ),
        Evaluation(
            id=uuid.uuid4(),
            user_id=students[1].id,
            professor_id=evaluated.id,
            course_id=course.id,
            semester="2026-1",
            clarity=2,
            easiness=4,
            helpfulness=3,
            punctuality=5,
            modality="virtual",
            created_at=now,
        ),
    ]
    test_db.add_all(evaluations)
    await test_db.flush()

    return evaluated, unevaluated


class TestProfessorsAPI:
    async def test_list_professors_paginated(self, test_db: AsyncSession, fisi_professors):
        """La lista de profesores responde paginada."""
        _, _ = fisi_professors
        reader = User(
            id=uuid.UUID("550e8400-e29b-41d4-a716-446655440099"),
            email="reader@unmsm.edu.pe",
            username="reader",
            full_name="Reader One",
            hashed_password="x",
            is_active=True,
            role="student",
        )
        test_db.add(reader)
        await test_db.flush()

        response = await list_professors(
            page=1,
            page_size=1,
            search=None,
            university_id=None,
            faculty_id=None,
            course_id=None,
            validation_status=None,
            include_deleted=False,
            sort_by="created_at",
            sort_order="desc",
            min_clarity=None,
            max_clarity=None,
            min_easiness=None,
            max_easiness=None,
            min_helpfulness=None,
            max_helpfulness=None,
            min_punctuality=None,
            max_punctuality=None,
            min_global_score=None,
            max_global_score=None,
            min_evaluations=None,
            date_from=None,
            date_to=None,
            db=test_db,
            current_user=reader,
        )

        assert response["total"] == 2
        assert len(response["items"]) == 1
        assert response["total_pages"] == 2

    async def test_list_computes_real_metric_averages(self, test_db: AsyncSession, fisi_professors):
        """Las cards del buscador deben mostrar promedios reales, no valores
        inventados: un profesor con evaluaciones trae avg_clarity/avg_easiness
        calculados desde `evaluations`, y uno sin evaluaciones trae None
        (no un número fabricado como el 3.5/2.5 hardcodeado anterior).
        """
        evaluated, unevaluated = fisi_professors
        reader = User(
            id=uuid.UUID("550e8400-e29b-41d4-a716-446655440098"),
            email="reader2@unmsm.edu.pe",
            username="reader2",
            full_name="Reader Two",
            hashed_password="x",
            is_active=True,
            role="student",
        )
        test_db.add(reader)
        await test_db.flush()

        response = await list_professors(
            page=1,
            page_size=20,
            search=None,
            university_id=None,
            faculty_id=None,
            course_id=None,
            validation_status=None,
            include_deleted=False,
            sort_by="created_at",
            sort_order="desc",
            min_clarity=None,
            max_clarity=None,
            min_easiness=None,
            max_easiness=None,
            min_helpfulness=None,
            max_helpfulness=None,
            min_punctuality=None,
            max_punctuality=None,
            min_global_score=None,
            max_global_score=None,
            min_evaluations=None,
            date_from=None,
            date_to=None,
            db=test_db,
            current_user=reader,
        )

        by_id = {item.id: item for item in response["items"]}

        evaluated_out = by_id[str(evaluated.id)]
        # promedio real de (4,2) y (2,4) -> 3.0 en ambas métricas
        assert evaluated_out.avg_clarity == pytest.approx(3.0)
        assert evaluated_out.avg_easiness == pytest.approx(3.0)
        assert evaluated_out.avg_helpfulness == pytest.approx(4.0)
        assert evaluated_out.avg_punctuality == pytest.approx(4.0)

        unevaluated_out = by_id[str(unevaluated.id)]
        assert unevaluated_out.avg_clarity is None
        assert unevaluated_out.avg_easiness is None
        assert unevaluated_out.avg_helpfulness is None
        assert unevaluated_out.avg_punctuality is None

    @pytest.mark.skip(reason="Pendiente de implementación (requiere cliente HTTP autenticado)")
    async def test_search_by_name(self):
        """La búsqueda por nombre filtra resultados."""

    @pytest.mark.skip(reason="Pendiente de implementación (requiere cliente HTTP autenticado)")
    async def test_professor_detail(self):
        """El detalle de un profesor devuelve sus datos y score."""

    @pytest.mark.skip(reason="Pendiente de implementación (requiere cliente HTTP autenticado)")
    async def test_professor_not_found(self):
        """CP-API-05 · Integración · Pruebas de API · Ninguno · Ninguna · 1. GET /professors/{uuid_aleatorio} · 404 Not Found"""

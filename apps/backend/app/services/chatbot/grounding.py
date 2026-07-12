"""Validación de grounding profesor-curso antes de entregar la respuesta final.

El LLM puede citar un profesor que no dicta el curso que el usuario está
pidiendo (p. ej. uno devuelto por search_professors_by_topic, cuya similitud
semántica no codifica cursos). Este módulo hace un chequeo server-side,
independiente de qué tools usó el LLM: detecta qué cursos activos se mencionan
en la conversación y verifica en `professor_courses` que cualquier profesor
citado en la respuesta final efectivamente dicte alguno de ellos.

El orquestador usa `check_grounding` como compuerta: si hay profesores sin
confirmar, pide al modelo una ronda de corrección (`correction_instruction`)
antes de emitir; `append_grounding_warnings` queda como último recurso si la
corrección tampoco pasa la validación.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from sqlalchemy import select, text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.professor_course import ProfessorCourse

_MENTIONED_COURSES_SQL = sa_text(
    """
    SELECT id, name FROM courses
    WHERE is_active = true AND :convo ILIKE '%' || name || '%'
    """
)

# Profesores reales cuyo nombre completo aparece textualmente en la respuesta
# (para distinguir un profesor citado de memoria/historial de uno inventado).
_NAMED_PROFESSORS_SQL = sa_text(
    """
    SELECT id, full_name FROM professors
    WHERE :resp ILIKE '%' || full_name || '%'
    """
)

# Los nombres en la BD llevan título académico ("Dr. X", "Ing. Y") y el modelo
# imita ese formato: un nombre con título que no venga de las tools ni exista
# en `professors` es una invención del LLM.
_TITLED_NAME_RE = re.compile(
    r"\b(?:Dr|Dra|Mg|Mtro|Mtra|Ing|Lic|Prof|MSc|PhD)\.?\s+"
    r"[A-ZÁÉÍÓÚÑ][\wáéíóúñü'-]*"
    r"(?:\s+(?:de|del|la|las|los|y|[A-ZÁÉÍÓÚÑ][\wáéíóúñü'-]*|[A-ZÁÉÍÓÚÑ]+,?))*"
)

_WARNING_TEMPLATE = (
    "\n\n⚠️ No pude confirmar en el sistema que **{name}** dicte el curso del "
    "que estamos hablando; verifica su ficha antes de tomarlo como recomendación."
)

_INVENTED_TEMPLATE = (
    "\n\n⚠️ **{name}** no aparece registrado en el sistema; "
    "ignora esa recomendación."
)


@dataclass
class GroundingCheck:
    """Resultado de validar la respuesta final contra la base de datos."""

    ungrounded: list[tuple[str, str]] = field(default_factory=list)  # (full_name, professor_id)
    invented: list[str] = field(default_factory=list)  # nombres que no existen en `professors`
    courses: list[tuple[int, str]] = field(default_factory=list)  # (course_id, name)

    @property
    def ok(self) -> bool:
        return not self.ungrounded and not self.invented


async def courses_mentioned_in(db: AsyncSession, convo_text: str) -> list[tuple[int, str]]:
    """Cursos activos cuyo nombre aparece como substring del texto de la conversación."""
    if not convo_text.strip():
        return []
    rows = await db.execute(_MENTIONED_COURSES_SQL, {"convo": convo_text})
    return [(r[0], r[1]) for r in rows]


def professors_mentioned_in(
    text: str, known_professors: dict[str, str]
) -> list[tuple[str, str]]:
    """[(full_name, professor_id)] de `known_professors` citados textualmente en `text`."""
    return [
        (name, pid)
        for name, pid in known_professors.items()
        if name and re.search(re.escape(name), text, re.IGNORECASE)
    ]


async def _teaching_pairs(
    db: AsyncSession, professor_ids: list[str], course_ids: list[int]
) -> set[tuple[str, int]]:
    if not professor_ids or not course_ids:
        return set()
    rows = await db.execute(
        select(ProfessorCourse.professor_id, ProfessorCourse.course_id).where(
            ProfessorCourse.professor_id.in_(professor_ids),
            ProfessorCourse.course_id.in_(course_ids),
        )
    )
    return {(str(pid), cid) for pid, cid in rows}


def _covered_by(candidate: str, names) -> bool:
    """True si `candidate` coincide (como substring, sin case) con algún nombre."""
    cand = candidate.lower().strip()
    return any(cand in n.lower() or n.lower() in cand for n in names if n)


async def check_grounding(
    *,
    db: AsyncSession,
    text: str,
    convo_text: str,
    known_professors: dict[str, str],
) -> GroundingCheck:
    """Valida la respuesta final contra la base de datos.

    Detecta dos fallas: (a) nombres con título académico que no vienen de las
    tools ni existen en `professors` (profesores inventados por el LLM), y
    (b) profesores reales citados que no dictan ningún curso mencionado en la
    conversación. `ok` == sin fallas.
    """
    if not text:
        return GroundingCheck()

    candidates = [m.group(0).strip().rstrip(",") for m in _TITLED_NAME_RE.finditer(text)]
    known_cited = professors_mentioned_in(text, known_professors)
    if not candidates and not known_cited:
        return GroundingCheck()

    # Candidatos que no salieron de las tools: ¿existen siquiera en la BD?
    unmatched = [c for c in candidates if not _covered_by(c, known_professors)]
    db_named: list[tuple[str, str]] = []
    if unmatched:
        rows = await db.execute(_NAMED_PROFESSORS_SQL, {"resp": text})
        db_named = [(r[1], str(r[0])) for r in rows]
    invented = list(dict.fromkeys(
        c for c in unmatched if not _covered_by(c, [n for n, _pid in db_named])
    ))

    # Profesores reales citados (de tools o hallados en la BD): validar curso.
    cited: dict[str, str] = dict(known_cited)
    for name, pid in db_named:
        cited.setdefault(name, pid)

    courses = await courses_mentioned_in(db, convo_text) if cited else []
    ungrounded: list[tuple[str, str]] = []
    if courses and cited:
        course_ids = [cid for cid, _name in courses]
        teaching = await _teaching_pairs(db, list(cited.values()), course_ids)
        ungrounded = [
            (name, pid)
            for name, pid in cited.items()
            if not any((pid, cid) in teaching for cid in course_ids)
        ]
    return GroundingCheck(ungrounded=ungrounded, invented=invented, courses=courses)


def correction_instruction(check: GroundingCheck) -> str:
    """Mensaje de corrección para que el modelo reescriba su respuesta sin los
    profesores inventados/no confirmados, en una ronda extra sin tools."""
    problems: list[str] = []
    if check.invented:
        problems.append(
            "estos profesores NO existen en el sistema (los inventaste): "
            + ", ".join(dict.fromkeys(check.invented))
        )
    if check.ungrounded:
        names = ", ".join(dict.fromkeys(name for name, _pid in check.ungrounded))
        courses = ", ".join(dict.fromkeys(name for _cid, name in check.courses))
        problems.append(
            f"estos profesores NO dictan ninguno de los cursos mencionados ({courses}): {names}"
        )
    return (
        "CORRECCIÓN DEL SISTEMA: según la base de datos, "
        + "; ".join(problems) + ". "
        "Reescribe tu respuesta anterior completa sin recomendarlos. "
        "Usa únicamente los profesores ya confirmados por los resultados de búsqueda; "
        "si no obtuviste resultados de búsqueda en este turno, di que no pudiste "
        "verificar profesores en este momento e invita a reintentar (no afirmes que "
        "el curso no tiene profesores). No menciones esta corrección."
    )


def warnings_for(check: GroundingCheck) -> str:
    """Advertencias visibles para los profesores no confirmados (último recurso)."""
    warnings = [_INVENTED_TEMPLATE.format(name=name) for name in check.invented]
    warnings += [_WARNING_TEMPLATE.format(name=name) for name, _pid in check.ungrounded]
    return "".join(dict.fromkeys(warnings))


async def append_grounding_warnings(
    *,
    db: AsyncSession,
    text: str,
    convo_text: str,
    known_professors: dict[str, str],
) -> str:
    """Agrega una advertencia visible si un profesor citado no dicta ningún curso
    mencionado en la conversación, en vez de dejar pasar la alucinación en silencio.

    No bloquea ni reescribe la respuesta del LLM: es el fallback cuando la ronda
    de corrección del orquestador no logró una respuesta validada.
    """
    check = await check_grounding(
        db=db, text=text, convo_text=convo_text, known_professors=known_professors
    )
    if check.ok:
        return text
    return text + warnings_for(check)

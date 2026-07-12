"""Tool: búsqueda semántica de profesores por tema/estilo/reputación.

Envuelve el Retriever (pgvector + Cohere, con fallback textual). Reemplaza al
antiguo contexto RAG "ambiental" que se inyectaba en cada pregunta: ahora el
modelo solo recibe estos resultados cuando los pide explícitamente, y la
descripción de la tool deja claro que NO confirman qué curso dicta cada profesor.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.chatbot.retriever import Retriever


async def search_professors_by_topic(*, db: AsyncSession, query: str) -> dict:
    retriever = Retriever(db)
    profs = await retriever.retrieve(query)
    if not profs:
        return {
            "result": [],
            "note": (
                "Sin resultados. Informa honestamente al usuario; NUNCA "
                "inventes nombres de profesores ni cursos."
            ),
        }
    return {
        "note": (
            "Resultados por similitud semántica (tema/estilo/reputación). "
            "NO confirman qué curso dicta cada profesor; para eso usa "
            "search_professors con course_id."
        ),
        "result": [
            {
                "professor_id": p.professor_id,
                "full_name": p.full_name,
                "global_score": p.global_score,
                "summary": p.summary,
                "pros": p.pros,
                "cons": p.cons,
                "hashtags": p.hashtags,
            }
            for p in profs
        ],
    }

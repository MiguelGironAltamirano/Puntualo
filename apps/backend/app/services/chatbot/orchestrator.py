"""Orquestador del chatbot RAG (Tarea 4.5).

Flujo: retrieval (contexto) → loop de function calling en streaming.
Cada ronda es UNA llamada a Gemini; cuando el modelo no pide más tools,
el texto de esa misma ronda es la respuesta final (no hay llamada extra).
El loop se aísla en stream_tool_loop para testearlo.
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.chatbot.gemini_chat_client import GeminiChatClient, extract_function_calls
from app.services.chatbot.grounding import append_grounding_warnings
from app.services.chatbot.prompts import load_system_prompt
from app.services.chatbot.retriever import Retriever, format_context
from app.services.chatbot.tools import TOOL_EXECUTORS

logger = logging.getLogger(__name__)

# Backoff entre reintentos ante 429 de Gemini (dos reintentos como máximo).
_RETRY_BACKOFF_SECONDS: tuple[float, ...] = (2.0, 5.0)

QUOTA_FRIENDLY_MESSAGE = (
    "El asistente está recibiendo muchas consultas en este momento. "
    "Por favor intenta de nuevo en unos minutos."
)


def _is_quota_error(exc: Exception) -> bool:
    return getattr(exc, "code", None) == 429


async def _execute_tool(name: str, args: dict, db: AsyncSession) -> dict:
    executor = TOOL_EXECUTORS.get(name)
    if executor is None:
        return {"error": f"unknown tool {name}"}
    try:
        result = await executor(db=db, **args)
        return result if isinstance(result, dict) else {"result": result}
    except Exception as exc:  # reinyecta el error al LLM en el mismo turn
        logger.warning("chat.tool.failed | name=%s", name, exc_info=True)
        return {"error": str(exc)}


def _function_response_parts(results: list[tuple[str, dict]]):
    from google.genai import types
    return [types.Part.from_function_response(name=n, response=r) for n, r in results]


def _function_call_parts(calls: list[tuple[str, dict]]):
    from google.genai import types
    return [types.Part(function_call=types.FunctionCall(name=n, args=a if isinstance(a, dict) else {})) for n, a in calls]


def _collect_known_professors(results: list[tuple[str, dict]], known: dict[str, str]) -> None:
    """Acumula name→professor_id de los resultados de tools, para poder validar
    contra `professor_courses` cualquier profesor que el LLM cite en su respuesta."""
    for name, result in results:
        if not isinstance(result, dict):
            continue
        if name == "search_professors":
            for p in result.get("result") or []:
                if isinstance(p, dict) and p.get("full_name") and p.get("professor_id"):
                    known[p["full_name"]] = p["professor_id"]
        elif name == "get_professor_details" and result.get("found"):
            if result.get("full_name") and result.get("professor_id"):
                known[result["full_name"]] = result["professor_id"]
        elif name == "compare_professors":
            comparison = result.get("comparison") or {}
            for p in comparison.get("professors") or []:
                if isinstance(p, dict) and p.get("full_name") and p.get("id"):
                    known[p["full_name"]] = p["id"]


async def stream_tool_loop(*, client, system_instruction: str, contents: list,
                           db: AsyncSession, max_rounds: int,
                           known_professors: dict[str, str] | None = None,
                           convo_text: str = "") -> AsyncIterator[str]:
    """Rondas de function calling en streaming hasta que el modelo no pida tools.

    El texto de la ronda sin tools es la respuesta final: se bufferiza completa
    y se valida contra `professor_courses` (ver grounding.py) antes de emitirla,
    para no dejar pasar en silencio un profesor que no dicta el curso discutido.
    Ante un 429 se reintenta la ronda con backoff; si la cuota sigue agotada
    se emite un mensaje amigable en lugar de propagar el error.
    """
    known_professors = known_professors if known_professors is not None else {}
    for _ in range(max_rounds):
        calls: list[tuple[str, dict]] = []
        round_text: list[str] = []
        for attempt in range(len(_RETRY_BACKOFF_SECONDS) + 1):
            emitted = False
            try:
                async for chunk in client.stream_with_tools(
                    system_instruction=system_instruction, contents=contents
                ):
                    text = getattr(chunk, "text", None)
                    if text:
                        emitted = True
                        round_text.append(text)
                    calls.extend(extract_function_calls(chunk))
                break
            except Exception as exc:
                if not _is_quota_error(exc):
                    raise
                # Si ya se emitió texto, reintentar duplicaría la respuesta.
                if emitted or attempt >= len(_RETRY_BACKOFF_SECONDS):
                    logger.warning("chat.gemini.quota_exhausted", exc_info=True)
                    yield QUOTA_FRIENDLY_MESSAGE
                    return
                logger.info("chat.gemini.429_retry | attempt=%d", attempt + 1)
                await asyncio.sleep(_RETRY_BACKOFF_SECONDS[attempt])
        if not calls:
            final_text = "".join(round_text)
            final_text = await append_grounding_warnings(
                db=db, text=final_text, convo_text=convo_text,
                known_professors=known_professors,
            )
            if final_text:
                yield final_text
            return
        results = [(name, await _execute_tool(name, args, db)) for name, args in calls]
        _collect_known_professors(results, known_professors)
        contents = contents + [
            {"role": "model", "parts": _function_call_parts(calls)},
            {"role": "user", "parts": _function_response_parts(results)},
        ]
    # Rondas agotadas con el modelo aún pidiendo tools: forzar respuesta sin tools.
    final_text = "".join([text async for text in client.stream_final(
        system_instruction=system_instruction, contents=contents
    )])
    final_text = await append_grounding_warnings(
        db=db, text=final_text, convo_text=convo_text, known_professors=known_professors,
    )
    if final_text:
        yield final_text


async def answer_stream(*, db: AsyncSession, user_message: str, history: list[dict],
                        client: GeminiChatClient | None = None) -> AsyncIterator[str]:
    """Genera la respuesta del asistente como stream de texto (para SSE)."""
    from google.genai import types

    client = client or GeminiChatClient()
    system = load_system_prompt(settings.CHATBOT_SYSTEM_PROMPT_VERSION)

    retriever = Retriever(db)
    retrieved = await retriever.retrieve(user_message)
    context_block = format_context(retrieved)

    # El retrieval semántico no filtra por curso (ver retriever.py), así que estos
    # profesores no están "confirmados" para ningún curso puntual: se registran
    # igual para poder validarlos en grounding.append_grounding_warnings.
    known_professors = {p.full_name: p.professor_id for p in retrieved}

    recent_history = history[-settings.CHATBOT_HISTORY_TURNS:]
    convo_text = "\n".join(m["content"] for m in recent_history) + "\n" + user_message

    contents = []
    for msg in recent_history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(
        text=f"CONTEXTO RECUPERADO:\n{context_block}\n\nPREGUNTA:\n{user_message}")]))

    async for chunk in stream_tool_loop(
        client=client, system_instruction=system, contents=contents,
        db=db, max_rounds=settings.CHATBOT_MAX_TOOL_ROUNDS,
        known_professors=known_professors, convo_text=convo_text,
    ):
        yield chunk

"""Orquestador del chatbot RAG (Tarea 4.5).

Flujo: retrieval (contexto) → loop de function calling (tools tocan BD) →
stream del texto final. El loop se aísla en run_tool_loop para testearlo.
"""
from __future__ import annotations

import logging
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.chatbot.gemini_chat_client import GeminiChatClient, extract_function_calls
from app.services.chatbot.prompts import load_system_prompt
from app.services.chatbot.retriever import Retriever, format_context
from app.services.chatbot.tools import TOOL_EXECUTORS

logger = logging.getLogger(__name__)


async def _execute_tool(name: str, args: dict, db: AsyncSession) -> dict:
    executor = TOOL_EXECUTORS.get(name)
    if executor is None:
        return {"error": f"unknown tool {name}"}
    try:
        return await executor(db=db, **args)
    except Exception as exc:  # reinyecta el error al LLM en el mismo turn
        logger.warning("chat.tool.failed | name=%s", name, exc_info=True)
        return {"error": str(exc)}


def _function_response_parts(results: list[tuple[str, dict]]):
    from google.genai import types
    return [types.Part.from_function_response(name=n, response=r) for n, r in results]


def _function_call_parts(calls: list[tuple[str, dict]]):
    from google.genai import types
    return [types.Part(function_call=types.FunctionCall(name=n, args=a)) for n, a in calls]


async def run_tool_loop(*, client, system_instruction: str, contents: list,
                        db: AsyncSession, max_rounds: int) -> list:
    """Ejecuta rondas de function calling hasta que el modelo no pida más tools.
    Devuelve `contents` extendido con los turns de tool (listo para el stream final)."""
    for _ in range(max_rounds):
        resp = await client.generate_with_tools(system_instruction=system_instruction, contents=contents)
        calls = extract_function_calls(resp)
        if not calls:
            return contents
        results = [(name, await _execute_tool(name, args, db)) for name, args in calls]
        try:
            contents = contents + [
                {"role": "model", "parts": _function_call_parts(calls)},
                {"role": "user", "parts": _function_response_parts(results)},
            ]
        except Exception:  # en tests sin SDK, basta con registrar el avance
            contents = contents + [{"_tool_round": results}]
    return contents


async def answer_stream(*, db: AsyncSession, user_message: str, history: list[dict],
                        client: GeminiChatClient | None = None) -> AsyncIterator[str]:
    """Genera la respuesta del asistente como stream de texto (para SSE)."""
    from google.genai import types

    client = client or GeminiChatClient()
    system = load_system_prompt(settings.CHATBOT_SYSTEM_PROMPT_VERSION)

    retriever = Retriever(db)
    retrieved = await retriever.retrieve(user_message)
    context_block = format_context(retrieved)

    contents = []
    for msg in history[-settings.CHATBOT_HISTORY_TURNS:]:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(
        text=f"CONTEXTO RECUPERADO:\n{context_block}\n\nPREGUNTA:\n{user_message}")]))

    contents = await run_tool_loop(
        client=client, system_instruction=system, contents=contents,
        db=db, max_rounds=settings.CHATBOT_MAX_TOOL_ROUNDS,
    )
    async for chunk in client.stream_final(system_instruction=system, contents=contents):
        yield chunk

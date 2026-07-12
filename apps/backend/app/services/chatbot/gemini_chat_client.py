"""Wrapper de Gemini para el chatbot: function calling manual + streaming final."""
from __future__ import annotations

import logging
from collections.abc import AsyncIterator

from app.core.config import settings
from app.services.chatbot.tools.definitions import TOOL_DECLARATIONS

logger = logging.getLogger(__name__)


def extract_function_calls(response) -> list[tuple[str, dict]]:
    """Lee (name, args) de las parts con function_call de una respuesta Gemini."""
    out: list[tuple[str, dict]] = []
    candidates = getattr(response, "candidates", None) or []
    for cand in candidates:
        content = getattr(cand, "content", None)
        for part in getattr(content, "parts", []) or []:
            fc = getattr(part, "function_call", None)
            if fc is not None:
                out.append((fc.name, dict(fc.args or {})))
    return out


def _build_tool():
    """Construye el objeto Tool con las FunctionDeclarations registradas."""
    from google.genai import types
    decls = [types.FunctionDeclaration(**d) for d in TOOL_DECLARATIONS]
    return types.Tool(function_declarations=decls)


class GeminiChatClient:
    """Cliente fino sobre google-genai. Inyectable (`_sdk_client`) para tests."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        _sdk_client=None,
    ) -> None:
        self.model = model or settings.CHATBOT_GEMINI_MODEL
        if _sdk_client is not None:
            self._client = _sdk_client
        else:
            from google import genai  # import perezoso: el SDK solo se necesita en runtime
            if settings.CHATBOT_USE_VERTEXAI:
                # Vertex AI autentica con ADC (GOOGLE_APPLICATION_CREDENTIALS
                # o `gcloud auth application-default login`), no con API key.
                self._client = genai.Client(
                    vertexai=True,
                    project=settings.GOOGLE_CLOUD_PROJECT,
                    location=settings.GOOGLE_CLOUD_LOCATION,
                )
            else:
                self._client = genai.Client(api_key=api_key or settings.GEMINI_API_KEY)

    async def stream_with_tools(
        self, *, system_instruction: str, contents: list
    ) -> AsyncIterator:
        """Una ronda en streaming con tools habilitadas. Emite los chunks crudos:
        el caller extrae texto y function_calls de cada uno."""
        from google.genai import types
        stream = await self._client.aio.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[_build_tool()],
                # disable=True evita que el SDK llame las tools automáticamente
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            ),
        )
        async for chunk in stream:
            yield chunk

    async def stream_final(
        self, *, system_instruction: str, contents: list
    ) -> AsyncIterator[str]:
        """Stream del texto final (sin tools: el modelo ya tiene los resultados)."""
        from google.genai import types
        stream = await self._client.aio.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(system_instruction=system_instruction),
        )
        async for chunk in stream:
            text = getattr(chunk, "text", None)
            if text:
                yield text

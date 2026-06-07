"""Wrapper aislado del SDK google-genai para generación de resúmenes (Tarea 4.4).

Aísla el proveedor: cambiar de LLM no toca summary_generator ni las tasks.
Usa response_schema (JSON garantizado) + retry con tenacity. Cuenta tokens.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from pydantic import BaseModel
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.services.nlp.output_parser import OutputParseError, normalize_summary, parse_json_loose

logger = logging.getLogger(__name__)

# Límites de normalización (red de seguridad sobre el output del modelo).
_MAX_SUMMARY_CHARS = 1200
_MAX_ITEM_CHARS = 80
_MAX_ITEMS = 6


class SummarySchema(BaseModel):
    """Esquema de salida pasado a Gemini como response_schema."""
    summary: str
    pros: list[str]
    cons: list[str]


@dataclass
class SummaryResult:
    summary: str
    pros: list[str]
    cons: list[str]
    token_usage: dict


class GeminiClient:
    """Cliente fino sobre google-genai. Inyectable (`_sdk_client`) para tests."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        max_retries: int | None = None,
        _sdk_client=None,
    ) -> None:
        self.model = model or settings.GEMINI_MODEL
        self.max_retries = max_retries if max_retries is not None else settings.NLP_LLM_MAX_RETRIES
        if _sdk_client is not None:
            self._client = _sdk_client
        else:
            from google import genai  # import perezoso: el SDK solo se necesita en runtime
            self._client = genai.Client(api_key=api_key or settings.GEMINI_API_KEY)

    async def generate(self, *, system_instruction: str, user_content: str) -> SummaryResult:
        @retry(
            retry=retry_if_exception_type(OutputParseError),
            stop=stop_after_attempt(self.max_retries + 1),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            reraise=True,
        )
        async def _call() -> SummaryResult:
            from google.genai import types

            response = await self._client.aio.models.generate_content(
                model=self.model,
                contents=user_content,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=SummarySchema,
                ),
            )
            raw = parse_json_loose(response.text)
            normalized = normalize_summary(
                raw,
                max_summary_chars=_MAX_SUMMARY_CHARS,
                max_item_chars=_MAX_ITEM_CHARS,
                max_items=_MAX_ITEMS,
            )
            usage = getattr(response, "usage_metadata", None)
            token_usage = {
                "prompt": getattr(usage, "prompt_token_count", None),
                "output": getattr(usage, "candidates_token_count", None),
                "total": getattr(usage, "total_token_count", None),
            }
            return SummaryResult(
                summary=normalized["summary"],
                pros=normalized["pros"],
                cons=normalized["cons"],
                token_usage=token_usage,
            )

        return await _call()

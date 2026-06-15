"""Wrapper aislado del SDK Cohere para embeddings del chatbot (Tarea 4.5).

embed-v4.0 es multilingüe y soporta dimensión configurable (1536) e input_type
asimétrico (search_document para indexar, search_query para consultar).
"""
from __future__ import annotations

import logging

from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = logging.getLogger(__name__)


class CohereEmbedder:
    """Cliente fino sobre cohere.AsyncClientV2. Inyectable (`_sdk_client`) para tests."""

    def __init__(self, *, api_key: str | None = None, model: str | None = None,
                 dim: int | None = None, _sdk_client=None) -> None:
        self.model = model or settings.COHERE_EMBED_MODEL
        self.dim = dim or settings.COHERE_EMBED_DIM
        if _sdk_client is not None:
            self._client = _sdk_client
        else:
            import cohere  # import perezoso
            self._client = cohere.AsyncClientV2(api_key=api_key or settings.COHERE_API_KEY)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10), reraise=True)
    async def _embed(self, texts: list[str], input_type: str) -> list[list[float]]:
        resp = await self._client.embed(
            texts=texts,
            model=self.model,
            input_type=input_type,
            output_dimension=self.dim,
            embedding_types=["float"],
        )
        return list(resp.embeddings.float)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return await self._embed(texts, "search_document")

    async def embed_query(self, text: str) -> list[float]:
        out = await self._embed([text], "search_query")
        return out[0]

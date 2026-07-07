"""Tests del loop de tools en streaming + manejo de 429 (no commitear).

Cubre el rediseño del orquestador: una sola llamada Gemini por ronda
(la última ronda sin tools ES la respuesta final), retry ante 429 y
mensaje amigable cuando la cuota se agota.
"""
from types import SimpleNamespace

import pytest
from google.genai import errors as genai_errors

from app.services.chatbot import orchestrator
from app.services.chatbot.orchestrator import QUOTA_FRIENDLY_MESSAGE, stream_tool_loop


def _text_chunk(text: str):
    return SimpleNamespace(text=text, candidates=[])


def _fc_chunk(name: str, args: dict):
    part = SimpleNamespace(function_call=SimpleNamespace(name=name, args=args), text=None)
    cand = SimpleNamespace(content=SimpleNamespace(parts=[part]))
    return SimpleNamespace(text=None, candidates=[cand])


def _quota_error():
    return genai_errors.APIError(
        429, {"error": {"message": "quota exceeded", "status": "RESOURCE_EXHAUSTED"}}
    )


class FakeClient:
    """Cada elemento de `rounds` es una lista de chunks o una excepción a lanzar."""

    def __init__(self, rounds, final_rounds=None):
        self.rounds = list(rounds)
        self.final_rounds = list(final_rounds or [])
        self.tool_calls = 0
        self.final_calls = 0

    async def stream_with_tools(self, *, system_instruction, contents):
        self.tool_calls += 1
        behavior = self.rounds.pop(0)
        if isinstance(behavior, Exception):
            raise behavior
        for chunk in behavior:
            yield chunk

    async def stream_final(self, *, system_instruction, contents):
        # El stream_final real emite strings de texto, no chunks crudos.
        self.final_calls += 1
        for text in self.final_rounds.pop(0):
            yield text


async def _collect(gen):
    return [c async for c in gen]


@pytest.fixture(autouse=True)
def _no_backoff(monkeypatch):
    monkeypatch.setattr(orchestrator, "_RETRY_BACKOFF_SECONDS", (0, 0))


async def test_respuesta_sin_tools_usa_una_sola_llamada():
    client = FakeClient(rounds=[[_text_chunk("Hola "), _text_chunk("mundo")]])
    out = await _collect(stream_tool_loop(
        client=client, system_instruction="s", contents=[], db=None, max_rounds=4,
    ))
    assert "".join(out) == "Hola mundo"
    assert client.tool_calls == 1
    assert client.final_calls == 0  # no hay llamada extra de stream final


async def test_ronda_de_tool_y_luego_respuesta(monkeypatch):
    seen = {}

    async def fake_tool(*, db, **kwargs):
        seen.update(kwargs)
        return {"ok": True}

    monkeypatch.setattr(orchestrator, "TOOL_EXECUTORS", {"buscar": fake_tool})
    client = FakeClient(rounds=[
        [_fc_chunk("buscar", {"q": "calculo"})],
        [_text_chunk("Te recomiendo a X")],
    ])
    out = await _collect(stream_tool_loop(
        client=client, system_instruction="s", contents=[], db=None, max_rounds=4,
    ))
    assert "".join(out) == "Te recomiendo a X"
    assert client.tool_calls == 2
    assert seen == {"q": "calculo"}


async def test_429_reintenta_y_luego_responde():
    client = FakeClient(rounds=[_quota_error(), [_text_chunk("listo")]])
    out = await _collect(stream_tool_loop(
        client=client, system_instruction="s", contents=[], db=None, max_rounds=4,
    ))
    assert "".join(out) == "listo"
    assert client.tool_calls == 2


async def test_429_persistente_devuelve_mensaje_amigable():
    client = FakeClient(rounds=[_quota_error(), _quota_error(), _quota_error()])
    out = await _collect(stream_tool_loop(
        client=client, system_instruction="s", contents=[], db=None, max_rounds=4,
    ))
    assert "".join(out) == QUOTA_FRIENDLY_MESSAGE


async def test_error_no_429_se_propaga():
    boom = genai_errors.APIError(500, {"error": {"message": "kaput", "status": "INTERNAL"}})
    client = FakeClient(rounds=[boom])
    with pytest.raises(genai_errors.APIError):
        await _collect(stream_tool_loop(
            client=client, system_instruction="s", contents=[], db=None, max_rounds=4,
        ))


async def test_max_rounds_agotado_cae_a_stream_final(monkeypatch):
    async def fake_tool(*, db, **kwargs):
        return {"ok": True}

    monkeypatch.setattr(orchestrator, "TOOL_EXECUTORS", {"buscar": fake_tool})
    client = FakeClient(
        rounds=[[_fc_chunk("buscar", {})], [_fc_chunk("buscar", {})]],
        final_rounds=[["respuesta forzada"]],
    )
    out = await _collect(stream_tool_loop(
        client=client, system_instruction="s", contents=[], db=None, max_rounds=2,
    ))
    assert "".join(out) == "respuesta forzada"
    assert client.tool_calls == 2
    assert client.final_calls == 1

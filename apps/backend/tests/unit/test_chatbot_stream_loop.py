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


class FakeGroundingDB:
    """Enruta las tres queries de grounding (cursos, nombres, professor_courses)."""

    def __init__(self, course_rows, teaching_rows, named_rows=()):
        self.course_rows = course_rows
        self.teaching_rows = teaching_rows
        self.named_rows = list(named_rows)

    async def execute(self, stmt, params=None):
        from sqlalchemy.sql import Select
        if isinstance(stmt, Select):
            return self.teaching_rows
        return self.named_rows if "FROM professors" in str(stmt) else self.course_rows


async def test_grounding_gate_pide_correccion_y_emite_la_version_corregida():
    # Prof X no dicta "Cálculo I": la respuesta que lo cita dispara una ronda
    # correctiva sin tools y se emite la corrección (que ya no lo menciona).
    db = FakeGroundingDB(course_rows=[(10, "Cálculo I")], teaching_rows=[])
    client = FakeClient(
        rounds=[[_text_chunk("Te recomiendo a Prof X para Cálculo I")]],
        final_rounds=[["No tengo profesores confirmados para Cálculo I."]],
    )
    out = await _collect(stream_tool_loop(
        client=client, system_instruction="s", contents=[], db=db, max_rounds=4,
        known_professors={"Prof X": "p1"}, convo_text="quiero un profe de Cálculo I",
    ))
    assert "".join(out) == "No tengo profesores confirmados para Cálculo I."
    assert client.final_calls == 1


async def test_grounding_gate_correccion_fallida_anexa_advertencia():
    # La corrección sigue citando a Prof X: se emite con advertencia visible.
    db = FakeGroundingDB(course_rows=[(10, "Cálculo I")], teaching_rows=[])
    client = FakeClient(
        rounds=[[_text_chunk("Te recomiendo a Prof X")]],
        final_rounds=[["Insisto con Prof X"]],
    )
    out = await _collect(stream_tool_loop(
        client=client, system_instruction="s", contents=[], db=db, max_rounds=4,
        known_professors={"Prof X": "p1"}, convo_text="quiero un profe de Cálculo I",
    ))
    joined = "".join(out)
    assert joined.startswith("Insisto con Prof X")
    assert "No pude confirmar" in joined
    assert "Prof X" in joined


async def test_grounding_gate_no_interviene_si_el_profesor_dicta_el_curso():
    db = FakeGroundingDB(course_rows=[(10, "Cálculo I")], teaching_rows=[("p1", 10)])
    client = FakeClient(rounds=[[_text_chunk("Te recomiendo a Prof X")]])
    out = await _collect(stream_tool_loop(
        client=client, system_instruction="s", contents=[], db=db, max_rounds=4,
        known_professors={"Prof X": "p1"}, convo_text="quiero un profe de Cálculo I",
    ))
    assert "".join(out) == "Te recomiendo a Prof X"
    assert client.final_calls == 0


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

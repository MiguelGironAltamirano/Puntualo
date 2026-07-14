"""Codificación SSE del stream del chatbot.

Regresión: la respuesta final del orquestador llega como UN solo chunk
multilínea (markdown con lista de profesores). Interpolarla cruda en
``data: {chunk}\\n\\n`` la truncaba en el primer salto de línea — el usuario
veía "Para el curso X te recomiendo a:" y ningún profesor.
"""
import pytest

from app.modules.chat.router import sse_event

RECOMMENDATION = (
    "Para el curso de **Base de Datos I**, te puedo recomendar a los siguientes "
    "profesores:\n"
    "\n"
    "*   **Mtro. Gustavo Arredondo Castillo** (calificación global: 4.1)\n"
    "*   **Mtro. Jorge Luis Chávez Soto** (calificación global: 4.0)"
)


def parse_sse(stream: str) -> list[tuple[str | None, str]]:
    """Parser SSE mínimo, con la misma semántica que el cliente del frontend:
    las líneas `data:` de un evento se unen con \\n y la línea en blanco despacha."""
    events: list[tuple[str | None, str]] = []
    name: str | None = None
    data: list[str] = []
    for line in stream.split("\n"):
        if line == "":
            if data:
                events.append((name, "\n".join(data)))
            name, data = None, []
            continue
        field, _, value = line.partition(":")
        value = value[1:] if value.startswith(" ") else value
        if field == "data":
            data.append(value)
        elif field == "event":
            name = value
    if data:
        events.append((name, "\n".join(data)))
    return events


def test_multiline_chunk_survives_round_trip():
    """El markdown con lista llega completo, no truncado en el primer \\n."""
    assert parse_sse(sse_event(RECOMMENDATION)) == [(None, RECOMMENDATION)]


def test_every_payload_line_is_prefixed():
    """Ninguna línea del payload puede quedar fuera de un campo `data:`;
    una línea suelta cerraría el evento y el resto se descartaría."""
    frame = sse_event(RECOMMENDATION)
    assert frame.endswith("\n\n")
    body = frame[:-2].split("\n")
    assert all(line.startswith("data:") for line in body)
    # La línea en blanco del markdown viaja como `data:` vacío, no como línea vacía
    # (que cerraría el evento y truncaría la lista de profesores).
    assert "data: " in body


def test_named_event():
    frame = sse_event("[DONE]", event="done")
    assert frame == "event: done\ndata: [DONE]\n\n"
    assert parse_sse(frame) == [("done", "[DONE]")]


@pytest.mark.parametrize(
    "text",
    ["una sola línea", "línea\ncon salto", "\nempieza con salto", "termina con salto\n"],
)
def test_round_trip_preserves_text(text):
    assert parse_sse(sse_event(text)) == [(None, text)]

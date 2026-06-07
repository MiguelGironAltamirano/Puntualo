"""Validación/normalización defensiva del JSON producido por el LLM (Tarea 4.4).

`response_schema` ya garantiza la forma cuando la respuesta es nativa, pero este
parser es la red de seguridad: recorta largos, limita cantidad de items, descarta
items no-string y rescata JSON envuelto en texto si fuera necesario.
"""
from __future__ import annotations

import json
import re


class OutputParseError(ValueError):
    """El output del LLM no pudo normalizarse a la forma esperada."""


_JSON_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)


def parse_json_loose(text: str) -> dict:
    """Extrae el primer objeto JSON de un texto que puede traer ruido alrededor."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass
    match = _JSON_OBJ_RE.search(text or "")
    if not match:
        raise OutputParseError("No se encontró JSON en la respuesta del modelo")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise OutputParseError(f"JSON malformado: {exc}") from exc


def _clean_items(items, *, max_item_chars: int, max_items: int) -> list[str]:
    out: list[str] = []
    for item in items or []:
        if not isinstance(item, str):
            continue
        cleaned = item.strip()
        if not cleaned:
            continue
        out.append(cleaned[:max_item_chars])
        if len(out) >= max_items:
            break
    return out


def normalize_summary(
    raw: dict,
    *,
    max_summary_chars: int,
    max_item_chars: int,
    max_items: int,
) -> dict:
    """Valida y normaliza `{summary, pros, cons}`. Lanza OutputParseError si falta summary."""
    if not isinstance(raw, dict):
        raise OutputParseError("La salida no es un objeto JSON")
    summary = raw.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise OutputParseError("Falta el campo 'summary' o está vacío")
    return {
        "summary": summary.strip()[:max_summary_chars],
        "pros": _clean_items(raw.get("pros"), max_item_chars=max_item_chars, max_items=max_items),
        "cons": _clean_items(raw.get("cons"), max_item_chars=max_item_chars, max_items=max_items),
    }

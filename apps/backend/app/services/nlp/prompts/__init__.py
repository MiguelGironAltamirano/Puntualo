"""Prompts versionados para la generación de resúmenes ejecutivos (Tarea 4.4)."""
from __future__ import annotations

from pathlib import Path

CURRENT_PROMPT_VERSION = "summary_v1"

_PROMPT_DIR = Path(__file__).resolve().parent
SYSTEM_PROMPT = (_PROMPT_DIR / f"{CURRENT_PROMPT_VERSION}.txt").read_text(encoding="utf-8")


def build_user_content(professor_name: str, reviews: list[dict]) -> str:
    """Construye el bloque de usuario: nombre + reseñas con criterios numéricos.

    Cada review es un dict con `comment` (str | None) y los 4 criterios
    (`clarity`, `easiness`, `helpfulness`, `punctuality`) como int | None.
    """
    lines: list[str] = [f"Profesor: {professor_name}", "", "Reseñas:"]
    if not reviews:
        lines.append("(sin reseñas)")
    for i, r in enumerate(reviews, start=1):
        metrics = (
            f"clarity={r.get('clarity')} easiness={r.get('easiness')} "
            f"helpfulness={r.get('helpfulness')} punctuality={r.get('punctuality')}"
        )
        comment = (r.get("comment") or "").strip() or "(sin comentario)"
        lines.append(f"{i}. [{metrics}] {comment}")
    return "\n".join(lines)

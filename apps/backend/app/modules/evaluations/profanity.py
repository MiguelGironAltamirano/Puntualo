"""Validacion de profanity para comentarios (funcion pura).

Pipeline de check:
  1. Cargar blocklist lazy desde `settings.COMMENT_PROFANITY_BLOCKLIST_FILE`
     (path absoluto o relativo al directorio backend). Cacheada con lru_cache.
  2. Normalizar input: NFKD -> strip diacriticos -> lowercase.
  3. Para cada palabra del blocklist, buscar match `\\bword\\b` en el normalizado.
  4. Primera ocurrencia -> raise OffensiveContentError.
"""
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from app.core.config import settings
from app.modules.evaluations.errors import OffensiveContentError

_BACKEND_ROOT = Path(__file__).resolve().parents[3]  # apps/backend/


def _normalize(text: str) -> str:
    """NFKD -> remueve diacriticos -> lowercase."""
    decomposed = unicodedata.normalize("NFKD", text)
    no_diacritics = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return no_diacritics.lower()


def _resolve_blocklist_path() -> Path:
    raw = Path(settings.COMMENT_PROFANITY_BLOCKLIST_FILE)
    return raw if raw.is_absolute() else _BACKEND_ROOT / raw


@lru_cache(maxsize=1)
def _load_blocklist() -> tuple[str, ...]:
    """Lee + normaliza el archivo de profanity. Cacheado tras la primera llamada."""
    path = _resolve_blocklist_path()
    raw = path.read_text(encoding="utf-8").splitlines()
    words: list[str] = []
    for line in raw:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        words.append(_normalize(stripped))
    return tuple(words)


def check(text: str) -> None:
    """Raisea OffensiveContentError si `text` contiene una palabra prohibida."""
    if not text:
        return
    normalized = _normalize(text)
    for word in _load_blocklist():
        if re.search(rf"\b{re.escape(word)}\b", normalized):
            raise OffensiveContentError(
                "El comentario contiene lenguaje ofensivo."
            )

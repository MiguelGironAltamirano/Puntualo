"""app/utils/hashtag_normalizer.py

normalize(): formato libre -> canonico (lowercase, sin diacriticos, sin '#', sin espacios).
validate_format(): valida el regex ^[a-z0-9_]{1,30}$ sobre el resultado de normalize.
"""
from __future__ import annotations

import re
import unicodedata

from app.modules.evaluations.errors import HashtagInvalidFormatError

_LABEL_RE = re.compile(r"^[a-z0-9_]{1,30}$")


def normalize(raw: str) -> str:
    if raw is None:
        return ""
    stripped = raw.strip()
    if stripped.startswith("#"):
        stripped = stripped[1:]
    nfkd = unicodedata.normalize("NFKD", stripped)
    no_diacritics = "".join(c for c in nfkd if not unicodedata.combining(c))
    no_spaces = re.sub(r"\s+", "", no_diacritics)
    return no_spaces.lower()


def validate_format(label: str) -> None:
    if not _LABEL_RE.match(label):
        raise HashtagInvalidFormatError(label)

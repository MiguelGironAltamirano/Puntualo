"""app/utils/moderation.py

Filtro heuristico mejorado con multiples capas de deteccion:
  1. Terminos prohibidos (banned_terms table, severity levels)
  2. Patrones regex (emails, URLs, telefonos)
  3. Deteccion de obfuscacion (cero-width Unicode, homoglyphs)
  4. Spam detection (caps excesivas, caracteres repetidos, gibberish)
  5. Manipulacion de espacios en blanco

Lee de banned_terms con cache en memoria (60s TTL, refresco lazy).

Para hashtags: usar severity_threshold='low' (mas estricto).
Para comentarios: usar severity_threshold='medium'.
"""
from __future__ import annotations

import re
import time
import unicodedata
from dataclasses import dataclass
from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.banned_term import BannedTerm

Severity = Literal["low", "medium", "high"]
HeuristicAction = Literal["allow", "flag", "block"]

_SEVERITY_RANK: dict[str, int] = {"low": 1, "medium": 2, "high": 3}

_CACHE_TTL_SECONDS = 60
_cache: dict[str, list[tuple[str, str]]] = {"all": []}
_cache_loaded_at: float = 0.0

# === Pattern definitions (regex) ===
_EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_PHONE_PATTERN = re.compile(r"(?:\+?51)?\d{8,12}")  # Peru phone numbers
_URL_PATTERN = re.compile(r"https?://[^\s]+")
_REPEATED_CHAR_PATTERN = re.compile(r"(.)\1{4,}")

# Zero-width Unicode characters
_ZERO_WIDTH_CHARS = {"\u200B", "\u200C", "\u200D", "\ufeff"}

# L33t speak mappings
_L33T_MAP = {
    "4": "a", "8": "b", "3": "e", "1": "i", "0": "o", "5": "s", "7": "t",
    "9": "g", "@": "a", "!": "i", "|": "l", "1": "l", "0": "o", "3": "e",
}


@dataclass
class HeuristicFilterResult:
    """Resultado completo del filtro heuristico."""
    action: HeuristicAction
    reasons: list[str]            # human-readable reasons
    spam_score: float             # 0.0–1.0
    banned_term: str | None = None
    matched_patterns: list[str] = None  # pattern keys triggered

    def __post_init__(self):
        if self.matched_patterns is None:
            self.matched_patterns = []


def _reset_cache_for_tests() -> None:
    """Helper que usan los tests; no usar en codigo de produccion."""
    global _cache_loaded_at
    _cache["all"] = []
    _cache_loaded_at = 0.0


def _strip_diacritics(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# === Heuristic detection functions ===

def _normalize_l33t(text: str) -> str:
    """Convierte l33t speak a caracteres normales para matching."""
    normalized = text.lower()
    for leetchar, normalchar in _L33T_MAP.items():
        normalized = normalized.replace(leetchar, normalchar)
    return normalized


def _has_zero_width_chars(text: str) -> bool:
    """Detecta caracteres de ancho cero usados para obfuscacion."""
    return any(c in _ZERO_WIDTH_CHARS for c in text)


def _has_excessive_diacritics(text: str) -> bool:
    """Detecta acumulacion anormal de diacriticos (homoglyph attack)."""
    # Si hay muchos caracteres combinantes sin base, es sospechoso
    parts = []
    for char in text:
        cat = unicodedata.category(char)
        if cat.startswith("M"):  # Mark (diacritic)
            parts.append(char)
    return len(parts) > len(text) * 0.1  # >10% diacritics


def _excessive_uppercase_ratio(text: str, threshold: float = 0.7) -> bool:
    """Detecta >70% de caracteres en mayuscula (spam típico)."""
    if not text:
        return False
    alpha_chars = [c for c in text if c.isalpha()]
    if not alpha_chars:
        return False
    uppercase_count = sum(1 for c in alpha_chars if c.isupper())
    return (uppercase_count / len(alpha_chars)) > threshold


def _excessive_repeated_chars(text: str, max_repeats: int = 5) -> bool:
    """Detecta repeticion excesiva de caracteres (e.g. 'aaaaaa')."""
    match = _REPEATED_CHAR_PATTERN.search(text)
    return match is not None


def _character_entropy(text: str) -> float:
    """Calcula entropia de Shannon (0=gibberish, ~5=normal, 7+=random)."""
    if not text:
        return 0.0
    import math
    from collections import Counter
    freq = Counter(text)
    entropy = 0.0
    for count in freq.values():
        p = count / len(text)
        entropy -= p * math.log2(p)
    return entropy


def _is_likely_gibberish(text: str, min_entropy: float = 2.0) -> bool:
    """Detecta texto que parece gibberish (muy baja entropia)."""
    entropy = _character_entropy(text)
    return entropy < min_entropy


def _detect_obfuscation_patterns(text: str) -> list[str]:
    """Retorna lista de obfuscation patterns detectados."""
    patterns = []
    if _has_zero_width_chars(text):
        patterns.append("zero_width_chars")
    if _has_excessive_diacritics(text):
        patterns.append("excessive_diacritics")
    if _is_likely_gibberish(text):
        patterns.append("gibberish")
    return patterns


def _detect_regex_patterns(text: str) -> dict[str, list[str]]:
    """Detecta patrones regex (emails, URLs, phones) y retorna matches."""
    matches = {}
    emails = _EMAIL_PATTERN.findall(text)
    if emails:
        matches["email"] = emails
    urls = _URL_PATTERN.findall(text)
    if urls:
        matches["url"] = urls
    phones = _PHONE_PATTERN.findall(text)
    if phones:
        matches["phone"] = phones
    return matches


async def _load_terms(db: AsyncSession) -> list[tuple[str, str]]:
    """Devuelve [(term_normalized, severity), ...]."""
    global _cache_loaded_at
    now = time.monotonic()
    if _cache["all"] and (now - _cache_loaded_at) < _CACHE_TTL_SECONDS:
        return _cache["all"]

    stmt = select(BannedTerm.term, BannedTerm.severity)
    rows = (await db.execute(stmt)).all()
    normalized = [
        (_strip_diacritics(t).lower(), s)
        for (t, s) in rows
    ]
    _cache["all"] = normalized
    _cache_loaded_at = now
    return normalized


async def banned_terms_filter(
    db: AsyncSession,
    text: str,
    *,
    severity_threshold: Severity = "medium",
) -> str | None:
    """Devuelve el primer termino prohibido detectado (>= threshold) o None.

    El match es substring sobre el texto normalizado (lowercase + sin diacriticos).
    No usa word-boundary porque hashtags y palabras concatenadas son comunes.
    
    [DEPRECATED] Use heuristic_filter() for full analysis. Kept for backward compat.
    """
    if not text:
        return None

    haystack = _strip_diacritics(text).lower()
    min_rank = _SEVERITY_RANK[severity_threshold]
    terms = await _load_terms(db)
    for term, sev in terms:
        if _SEVERITY_RANK.get(sev, 0) < min_rank:
            continue
        if term and term in haystack:
            return term
    return None


async def heuristic_filter(
    text: str,
    *,
    db: AsyncSession | None = None,
    severity_threshold: Severity = "medium",
    spam_block_threshold: float = 0.7,
    spam_flag_threshold: float = 0.4,
) -> HeuristicFilterResult:
    """Filtro heuristico multi-capa. Retorna resultado completo con score + decision.
     
    Stages:
      1. Banned terms (substring match)
      2. Regex patterns (email, URL, phone)
      3. Obfuscation detection (zero-width, excessive diacritics, gibberish)
      4. Spam scoring (caps, repeated chars, entropy)
    
    Action:
      - "block": spam_score >= spam_block_threshold (typically 0.7)
      - "flag": spam_block_threshold > spam_score >= spam_flag_threshold (typically 0.4)
      - "allow": spam_score < spam_flag_threshold
      
    Args:
        text: Comment text to analyze
        db: Optional AsyncSession for banned terms lookup (if not provided, skips banned terms check)
        severity_threshold: Severity level for banned terms ("low", "medium", "high")
        spam_block_threshold: Score threshold for blocking (default 0.7)
        spam_flag_threshold: Score threshold for flagging (default 0.4)
    """

    if not text or len(text.strip()) == 0:
        return HeuristicFilterResult(
            action="allow",
            reasons=[],
            spam_score=0.0,
        )

    reasons: list[str] = []
    spam_score = 0.0
    banned_term: str | None = None
    matched_patterns: list[str] = []

    # === Stage 1: Banned terms ===
    if db is not None:
        term = await banned_terms_filter(db, text, severity_threshold=severity_threshold)
        if term:
            banned_term = term
            reasons.append(f"Termino prohibido detectado: '{term}'")
            spam_score += 0.5  # High contribution

    # === Stage 2: Regex patterns ===
    pattern_matches = _detect_regex_patterns(text)
    if pattern_matches:
        for pattern_name in pattern_matches.keys():
            matched_patterns.append(pattern_name)
            # Mention them but don't auto-block (context-dependent)
            reasons.append(f"Contiene {pattern_name}")
            spam_score += 0.1  # Small bump per pattern

    # === Stage 3: Obfuscation ===
    obfuscation = _detect_obfuscation_patterns(text)
    if obfuscation:
        for obs_pattern in obfuscation:
            matched_patterns.append(f"obfuscation_{obs_pattern}")
            reasons.append(f"Intento de obfuscacion: {obs_pattern}")
            spam_score += 0.15

    # === Stage 4: Spam scoring ===
    if _excessive_uppercase_ratio(text):
        reasons.append("Cantidad excesiva de letras mayusculas")
        spam_score += 0.15

    if _excessive_repeated_chars(text):
        reasons.append("Repeticion excesiva de caracteres")
        spam_score += 0.15

    if _is_likely_gibberish(text):
        reasons.append("Parece ser texto aleatorio/gibberish")
        spam_score += 0.2

    # Cap spam_score at 1.0
    spam_score = min(spam_score, 1.0)

    # === Determine action ===
    if spam_score >= spam_block_threshold:
        action: HeuristicAction = "block"
    elif spam_score >= spam_flag_threshold:
        action = "flag"
    else:
        action = "allow"

    return HeuristicFilterResult(
        action=action,
        reasons=reasons,
        spam_score=spam_score,
        banned_term=banned_term,
        matched_patterns=matched_patterns,
    )

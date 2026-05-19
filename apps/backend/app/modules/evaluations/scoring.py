"""Calculo del score global de profesores (funcion pura).

Las 4 metricas que entran al score (clarity, easiness, helpfulness, punctuality)
pesan 0.25 cada una por default (hardcoded en config). `course_difficulty` NO
entra al score — se captura como metadato a nivel evaluacion.
"""
from app.core.config import settings


def compute_global_score(
    avg_clarity: float,
    avg_easiness: float,
    avg_helpfulness: float,
    avg_punctuality: float,
    *,
    w_clarity: float | None = None,
    w_easiness: float | None = None,
    w_helpfulness: float | None = None,
    w_punctuality: float | None = None,
) -> float:
    """Combina los 4 promedios por categoria en un score global [1.0, 5.0].

    Pesos por default vienen de `settings.SCORE_WEIGHT_*` (hardcoded a 0.25);
    los kwargs `w_*` permiten override puntual (util para tests con pesos custom).
    Output: float redondeado a 1 decimal, clampeado a [1.0, 5.0].
    """
    wc = settings.SCORE_WEIGHT_CLARITY if w_clarity is None else w_clarity
    we = settings.SCORE_WEIGHT_EASINESS if w_easiness is None else w_easiness
    wh = settings.SCORE_WEIGHT_HELPFULNESS if w_helpfulness is None else w_helpfulness
    wp = settings.SCORE_WEIGHT_PUNCTUALITY if w_punctuality is None else w_punctuality

    weighted = (
        avg_clarity * wc
        + avg_easiness * we
        + avg_helpfulness * wh
        + avg_punctuality * wp
    )
    clamped = max(1.0, min(5.0, weighted))
    return round(clamped, 1)

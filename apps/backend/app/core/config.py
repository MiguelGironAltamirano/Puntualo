from dotenv import load_dotenv
import os


load_dotenv()


class Settings:

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        ""
    )

    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        ""
    )

    ALGORITHM: str = os.getenv(
        "ALGORITHM",
        "HS256"
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "30"
        )
    )

    JWT_SECRET: str = os.getenv(
        "JWT_SECRET",
        ""
    )

    GOOGLE_CLIENT_ID: str = os.getenv(
        "GOOGLE_CLIENT_ID",
        ""
    )

    GOOGLE_CLIENT_SECRET: str = os.getenv(
        "GOOGLE_CLIENT_SECRET",
        ""
    )

    # UNMSM directory
    UNMSM_DIRECTORY_URLS: list = [
        "https://sistemas.unmsm.edu.pe/site/docentes/directorio/directorio-dacc",
        "https://sistemas.unmsm.edu.pe/site/docentes/directorio/directorio-daisw",
        "https://sistemas.unmsm.edu.pe/posgrado/docentes/",
    ]
    UNMSM_USER_AGENT: str = os.getenv(
        "UNMSM_USER_AGENT",
        "Puntualo-Research/1.0 (mailto:contacto@puntualo.dev)"
    )
    UNMSM_RATE_LIMIT_SECONDS: float = float(
        os.getenv("UNMSM_RATE_LIMIT_SECONDS", "1.0")
    )

    # OpenAlex
    OPENALEX_API_BASE: str = os.getenv(
        "OPENALEX_API_BASE",
        "https://api.openalex.org"
    )
    OPENALEX_INSTITUTION_ID: str = os.getenv(
        "OPENALEX_INSTITUTION_ID",
        "I192513696"
    )
    OPENALEX_USER_AGENT: str = os.getenv(
        "OPENALEX_USER_AGENT",
        "Puntualo/1.0 (mailto:contacto@puntualo.dev)"
    )

    # ORCID
    ORCID_API_BASE: str = os.getenv(
        "ORCID_API_BASE",
        "https://pub.orcid.org/v3.0"
    )
    ORCID_AFFILIATION_NAME: str = os.getenv(
        "ORCID_AFFILIATION_NAME",
        "Universidad Nacional Mayor de San Marcos"
    )

    # Tavily (fallback enrichment con cuota)
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    TAVILY_API_BASE: str = os.getenv(
        "TAVILY_API_BASE",
        "https://api.tavily.com"
    )
    TAVILY_BUDGET_HARD_CAP: int = int(
        os.getenv("TAVILY_BUDGET_HARD_CAP", "950")
    )
    TAVILY_BUDGET_SOFT_WARNING: int = int(
        os.getenv("TAVILY_BUDGET_SOFT_WARNING", "760")
    )

    # Pipeline general
    PIPELINE_TIMEOUT_CONNECT: float = float(
        os.getenv("PIPELINE_TIMEOUT_CONNECT", "5.0")
    )
    PIPELINE_TIMEOUT_READ: float = float(
        os.getenv("PIPELINE_TIMEOUT_READ", "10.0")
    )
    PIPELINE_MAX_RETRIES: int = int(
        os.getenv("PIPELINE_MAX_RETRIES", "3")
    )
    PIPELINE_BACKOFF_BASE: float = float(
        os.getenv("PIPELINE_BACKOFF_BASE", "2.0")
    )
    CIRCUIT_THRESHOLD: int = int(
        os.getenv("CIRCUIT_THRESHOLD", "5")
    )
    CIRCUIT_RESET_SECONDS: int = int(
        os.getenv("CIRCUIT_RESET_SECONDS", "300")
    )
    CACHE_TTL_VALIDATION_SECONDS: int = int(
        os.getenv("CACHE_TTL_VALIDATION_SECONDS", "86400")
    )
    CACHE_TTL_ENRICHMENT_SECONDS: int = int(
        os.getenv("CACHE_TTL_ENRICHMENT_SECONDS", "604800")
    )

    # Redis + Celery
    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )
    CELERY_BROKER_URL: str = os.getenv(
        "CELERY_BROKER_URL",
        "redis://localhost:6379/1"
    )
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND",
        "redis://localhost:6379/2"
    )

    # --- Tarea 2.6: pesos del score global (hardcoded, no env)
    # Las 4 metricas que entran al score (clarity, easiness, helpfulness, punctuality)
    # pesan 0.25 cada una y suman 1.0. course_difficulty no entra al score.
    SCORE_WEIGHT_CLARITY: float = 0.25
    SCORE_WEIGHT_EASINESS: float = 0.25
    SCORE_WEIGHT_HELPFULNESS: float = 0.25
    SCORE_WEIGHT_PUNCTUALITY: float = 0.25

    # --- Tarea 2.6: validacion de comentarios
    COMMENT_MIN_LENGTH: int = int(os.getenv("COMMENT_MIN_LENGTH", "20"))
    COMMENT_MAX_LENGTH: int = int(os.getenv("COMMENT_MAX_LENGTH", "2000"))
    COMMENT_REPORT_REASON_MAX_LENGTH: int = int(
        os.getenv("COMMENT_REPORT_REASON_MAX_LENGTH", "500")
    )

    # --- Tarea 2.6: moderacion
    MODERATION_HIDE_THRESHOLD: int = int(os.getenv("MODERATION_HIDE_THRESHOLD", "5"))
    LLM_MODERATION_ENABLED: bool = os.getenv("LLM_MODERATION_ENABLED", "false").lower() == "true"
    MODERATION_VERIFIED_EMAIL_DOMAIN: str = os.getenv(
        "MODERATION_VERIFIED_EMAIL_DOMAIN", "unmsm.edu.pe"
    )

    # --- Tarea 2.6: hook resumen IA (Tarea 4.4)
    IA_SUMMARY_HOOK_ENABLED: bool = os.getenv("IA_SUMMARY_HOOK_ENABLED", "false").lower() == "true"
    IA_SUMMARY_THRESHOLD: int = int(os.getenv("IA_SUMMARY_THRESHOLD", "10"))

    # --- Tarea 2.6: cache TTLs
    CACHE_TTL_PROFESSOR_DETAIL_SECONDS: int = int(
        os.getenv("CACHE_TTL_PROFESSOR_DETAIL_SECONDS", "300")
    )
    CACHE_TTL_PROFESSOR_COMMENTS_SECONDS: int = int(
        os.getenv("CACHE_TTL_PROFESSOR_COMMENTS_SECONDS", "120")
    )
    CACHE_TTL_COURSES_SEARCH_SECONDS: int = int(
        os.getenv("CACHE_TTL_COURSES_SEARCH_SECONDS", "60")
    )

    # --- Tarea 2.6: override de semestre (solo tests)
    SEMESTER_OVERRIDE: str | None = os.getenv("SEMESTER_OVERRIDE") or None


settings = Settings()


# Sanity check: aunque los pesos son hardcoded, validamos al import para
# detectar typos si alguien cambia los literales. Suma debe ser 1.0 +- 1e-3.
_weights_sum = (
    settings.SCORE_WEIGHT_CLARITY
    + settings.SCORE_WEIGHT_EASINESS
    + settings.SCORE_WEIGHT_HELPFULNESS
    + settings.SCORE_WEIGHT_PUNCTUALITY
)
if abs(_weights_sum - 1.0) > 1e-3:
    raise ValueError(
        f"Los pesos del puntaje deben sumar 1.0; suman {_weights_sum}. "
        "Revisa SCORE_WEIGHT_* en app/core/config.py."
    )
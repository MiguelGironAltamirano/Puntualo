import ssl
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from dotenv import load_dotenv
import os


load_dotenv()


def _strip_ssl_params(url: str) -> tuple[str, bool]:
    """Elimina ?sslmode= y ?ssl= de la URL y devuelve (url_limpia, necesita_ssl).

    asyncpg y psycopg2 reciben SSL via connect_args, NO via query string de
    SQLAlchemy.  Aiven siempre incluye ?sslmode=require en su connection string;
    esta función lo elimina para evitar el TypeError de asyncpg.
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)

    needs_ssl = False
    for key in ("sslmode", "ssl"):
        val = params.pop(key, None)
        if val and val[0] in ("require", "verify-ca", "verify-full", "true", "1"):
            needs_ssl = True

    clean_query = urlencode({k: v[0] for k, v in params.items()})
    clean_url = urlunparse(parsed._replace(query=clean_query))
    return clean_url, needs_ssl


class Settings:

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        ""
    )

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """URL limpia para asyncpg (postgresql+asyncpg://, sin sslmode/ssl)."""
        raw = self.DATABASE_URL
        # Normalizar esquema
        if raw.startswith("postgresql://"):
            raw = raw.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif raw.startswith("postgresql+psycopg2://"):
            raw = raw.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
        clean_url, _ = _strip_ssl_params(raw)
        return clean_url

    @property
    def ASYNC_SSL_CONTEXT(self) -> "ssl.SSLContext | None":
        """Contexto SSL para asyncpg, o None si la URL no pide SSL.

        Aiven utiliza una CA propia (autofirmada); deshabilitamos la
        verificación de la cadena para evitar SSLCertVerificationError.
        La conexión sigue siendo cifrada (TLS); solo se omite la validación de la CA.
        """
        _, needs_ssl = _strip_ssl_params(self.DATABASE_URL)
        if needs_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            return ctx
        return None

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """URL limpia para psycopg2 (postgresql://, sin sslmode/ssl).

        psycopg2 sí entiende sslmode, pero SQLAlchemy lo pasa como keyword
        arg al driver cuando está en la URL; para evitar colisiones lo
        eliminamos y lo ponemos en connect_args de forma explícita.
        """
        raw = self.DATABASE_URL
        # Normalizar esquema a psycopg2
        if raw.startswith("postgresql+asyncpg://"):
            raw = raw.replace("postgresql+asyncpg://", "postgresql://", 1)
        elif raw.startswith("postgresql+psycopg2://"):
            raw = raw.replace("postgresql+psycopg2://", "postgresql://", 1)
        clean_url, _ = _strip_ssl_params(raw)
        return clean_url

    @property
    def SYNC_SSL_ARGS(self) -> dict:
        """connect_args con sslmode=require para psycopg2, o {} si no aplica."""
        _, needs_ssl = _strip_ssl_params(self.DATABASE_URL)
        if needs_ssl:
            return {"sslmode": "require"}
        return {}

    # --- Pools de conexiones a la BD.
    # Aiven (plan actual) capa en max_connections=20 con 3 reservadas para
    # superuser => 17 usables por el rol de la app, COMPARTIDAS entre el engine
    # async, el sync y los workers de Celery. Por eso los pools van acotados:
    # con QueuePool por defecto (5+10) cada engine consumiría hasta 15 conexiones
    # por proceso y agotaría el tope. Subir estos valores SOLO si se amplía el
    # plan de la BD.
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "2"))
    DB_SYNC_POOL_SIZE: int = int(os.getenv("DB_SYNC_POOL_SIZE", "2"))
    DB_SYNC_MAX_OVERFLOW: int = int(os.getenv("DB_SYNC_MAX_OVERFLOW", "1"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))

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

    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "")
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "true").lower() == "true"
    SMTP_SSL: bool = os.getenv("SMTP_SSL", "false").lower() == "true"

    EMAIL_VERIFICATION_TTL_MINUTES: int = int(
        os.getenv("EMAIL_VERIFICATION_TTL_MINUTES", "10")
    )
    EMAIL_VERIFICATION_MAX_ATTEMPTS: int = int(
        os.getenv("EMAIL_VERIFICATION_MAX_ATTEMPTS", "5")
    )

    PASSWORD_RESET_TTL_MINUTES: int = int(
        os.getenv("PASSWORD_RESET_TTL_MINUTES", "10")
    )
    PASSWORD_RESET_MAX_ATTEMPTS: int = int(
        os.getenv("PASSWORD_RESET_MAX_ATTEMPTS", "5")
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

    # Supabase Storage
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_BUCKET_NAME: str = os.getenv("SUPABASE_BUCKET_NAME", "")

    # Verificacion de carnet (calidad minima)
    VERIFICATION_MAX_FILE_SIZE_BYTES: int = int(
        os.getenv("VERIFICATION_MAX_FILE_SIZE_BYTES", str(5 * 1024 * 1024))
    )
    VERIFICATION_MIN_WIDTH: int = int(
        os.getenv("VERIFICATION_MIN_WIDTH", "800")
    )
    VERIFICATION_MIN_HEIGHT: int = int(
        os.getenv("VERIFICATION_MIN_HEIGHT", "600")
    )
    VERIFICATION_MIN_SHARPNESS: float = float(
        os.getenv("VERIFICATION_MIN_SHARPNESS", "10.0")
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

    # --- Tarea 4.4: Resumen Ejecutivo NLP (Gemini)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    NLP_SUMMARY_MIN_REVIEWS: int = int(os.getenv("NLP_SUMMARY_MIN_REVIEWS", "5"))
    NLP_SUMMARY_MAX_REVIEWS: int = int(os.getenv("NLP_SUMMARY_MAX_REVIEWS", "100"))
    NLP_SUMMARY_SAMPLE_RECENT: int = int(os.getenv("NLP_SUMMARY_SAMPLE_RECENT", "50"))
    NLP_SUMMARY_SAMPLE_RANDOM: int = int(os.getenv("NLP_SUMMARY_SAMPLE_RANDOM", "50"))
    NLP_SUMMARY_MAX_INPUT_TOKENS: int = int(os.getenv("NLP_SUMMARY_MAX_INPUT_TOKENS", "50000"))
    NLP_SUMMARY_BEAT_SECONDS: int = int(os.getenv("NLP_SUMMARY_BEAT_SECONDS", "900"))
    NLP_LLM_MAX_RETRIES: int = int(os.getenv("NLP_LLM_MAX_RETRIES", "2"))

    # --- Tarea 2.6: override de semestre (solo tests)
    SEMESTER_OVERRIDE: str | None = os.getenv("SEMESTER_OVERRIDE") or None

    # --- Heuristic filter thresholds (spam detection)
    HEURISTIC_SPAM_BLOCK_THRESHOLD: float = float(
        os.getenv("HEURISTIC_SPAM_BLOCK_THRESHOLD", "0.7")
    )
    HEURISTIC_SPAM_FLAG_THRESHOLD: float = float(
        os.getenv("HEURISTIC_SPAM_FLAG_THRESHOLD", "0.4")
    )
    HEURISTIC_MAX_UPPERCASE_RATIO: float = float(
        os.getenv("HEURISTIC_MAX_UPPERCASE_RATIO", "0.7")
    )
    HEURISTIC_OBFUSCATION_CHECK: bool = (
        os.getenv("HEURISTIC_OBFUSCATION_CHECK", "true").lower() == "true"
    )

    # --- Report/complaint rate limiting and thresholds
    REPORT_RATE_LIMIT_PER_HOUR: int = int(
        os.getenv("REPORT_RATE_LIMIT_PER_HOUR", "10")
    )
    REPORT_ABUSE_THRESHOLD: int = int(
        os.getenv("REPORT_ABUSE_THRESHOLD", "5")
    )
    REPORT_MODERATION_TRIGGER_THRESHOLD: float = float(
        os.getenv("REPORT_MODERATION_TRIGGER_THRESHOLD", "5.0")
    )


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
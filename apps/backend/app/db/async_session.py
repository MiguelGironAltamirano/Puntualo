import ssl
from collections.abc import AsyncIterator
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


def _build_async_url(url: str) -> tuple[str, dict]:
    """Convierte la URL a asyncpg y extrae el contexto SSL si corresponde.

    asyncpg no acepta el parámetro ``sslmode`` (propio de libpq/psycopg2) ni
    ``ssl`` como query string.  Los eliminamos de la URL y devolvemos el
    contexto SSL listo para pasarlo en ``connect_args``.

    Returns:
        (url_limpia, connect_args)
    """
    # 1. Normalizar esquema a postgresql+asyncpg
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql+psycopg2://"):
        url = url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    # Si ya es postgresql+asyncpg://, se mantiene igual

    # 2. Parsear y eliminar parámetros que asyncpg no entiende
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)

    needs_ssl = False
    for key in ("sslmode", "ssl"):
        value = params.pop(key, None)
        if value and value[0] in ("require", "verify-ca", "verify-full", "true", "1"):
            needs_ssl = True

    # 3. Reconstruir URL sin esos parámetros
    clean_query = urlencode({k: v[0] for k, v in params.items()})
    clean_url = urlunparse(parsed._replace(query=clean_query))

    # 4. Construir connect_args con contexto SSL nativo si hace falta
    connect_args: dict = {}
    if needs_ssl:
        ssl_ctx = ssl.create_default_context()
        # Aiven utiliza una CA propia (autofirmada); deshabilitamos la
        # verificación de la cadena para evitar SSLCertVerificationError.
        # La conexión sigue siendo cifrada; solo se omite la validación de la CA.
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_ctx

    return clean_url, connect_args


_async_url, _connect_args = _build_async_url(settings.DATABASE_URL)

async_engine = create_async_engine(
    _async_url,
    pool_pre_ping=True,
    connect_args=_connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_async_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session

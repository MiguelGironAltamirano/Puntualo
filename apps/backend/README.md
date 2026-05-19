# Puntualo — Backend

FastAPI + Celery + PostgreSQL + Redis. Valida y enriquece perfiles de profesores UNMSM
contra cuatro fuentes externas: directorio UNMSM, OpenAlex, ORCID y Tavily.

---

## Requisitos previos

- Docker + Docker Compose
- Python 3.13 (entorno `puntualo` en mamba/conda)
- Archivo `apps/backend/.env` (ver sección Variables de entorno)

---

## Arranque en desarrollo

### 1. Infraestructura (PostgreSQL + Redis)

Desde la raíz del monorepo:

```bash
docker compose up -d postgres redis
```

Verificar que Redis responde:

```bash
docker exec puntualo_redis redis-cli ping   # → PONG
```

### 2. Migraciones

```bash
cd apps/backend
alembic upgrade head
```

### 3. API (uvicorn)

```bash
cd apps/backend
uvicorn app.main:app --reload --port 8000
```

### 4. Worker Celery

En una terminal separada, **desde el mismo directorio** (`apps/backend`) y con el mismo `.env` que la API:

```bash
cd apps/backend
celery -A app.core.celery_app worker -l info -Q celery
```

El worker carga `.env` automáticamente gracias a `load_dotenv()` en `app/core/config.py`.
No se necesita exportar variables manualmente.

---

## Variables de entorno (`apps/backend/.env`)

| Variable | Descripción | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL (psycopg2 o asyncpg) | — |
| `SECRET_KEY` | Clave firma JWT | — |
| `JWT_SECRET` | Alias de `SECRET_KEY` usado en algunos flows | — |
| `REDIS_URL` | Cache (db 0) | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | Cola de tareas (db 1) | `redis://localhost:6379/1` |
| `CELERY_RESULT_BACKEND` | Resultados Celery (db 2) | `redis://localhost:6379/2` |
| `TAVILY_API_KEY` | API key para búsqueda web (enriquecimiento) | — |
| `TAVILY_BUDGET_HARD_CAP` | Llamadas Tavily máximas por mes | `950` |
| `CIRCUIT_THRESHOLD` | Fallos consecutivos para abrir circuit breaker | `5` |
| `CIRCUIT_RESET_SECONDS` | Segundos hasta que el circuit breaker se cierra | `300` |

---

## Arranque con Docker (worker en contenedor)

El `docker-compose.yml` incluye un servicio `worker` que comparte el mismo `.env`:

```bash
docker compose up -d
```

Esto levanta PostgreSQL, Redis y el worker Celery. La API se corre localmente con uvicorn
(paso 3 de la sección anterior) o se puede agregar un servicio `api` al compose.

---

## Endpoints de validación

### Disparar validación inicial

Al crear un profesor (`POST /professors`), el endpoint encola automáticamente la tarea
de validación. El campo `validation_status` comienza en `pending_validation`.

### Forzar revalidación

```
POST /professors/{professor_id}/revalidate
Authorization: Bearer <token>
```

Respuesta `202 Accepted`:

```json
{ "queued": true, "professor_id": "..." }
```

Lo que hace internamente:
1. Invalida las claves de cache del profesor en Redis (OpenAlex, ORCID, directorio UNMSM).
2. Elimina los registros de evidencia anteriores (`professor_evidence`).
3. Resetea `validation_status` a `pending_validation`.
4. Encola nueva tarea Celery.

---

## Troubleshooting

### El worker dice "Event loop is closed"

Síntoma: segunda tarea en el mismo proceso worker crashea con `RuntimeError: Event loop is closed`.

Causa: singleton de Redis o pool de SQLAlchemy atado al loop anterior.

Solución: el código ya reinicializa `redis_client` al inicio de cada tarea y usa
`NullPool` en el engine de DB. Si el error reaparece, verificar que ningún módulo
haga `from app.utils.cache import redis_client` (importación directa crea binding
estático). Debe ser `import app.utils.cache as _cache_mod` con acceso vía atributo.

### El worker no recibe tareas (broker caído)

Síntomas en logs del worker:

```
[ERROR] consumer: Cannot connect to redis://localhost:6379/1
```

Pasos:
1. Verificar que Redis está corriendo: `docker compose ps redis`
2. Verificar conexión: `redis-cli -p 6379 ping`
3. Reiniciar Redis si es necesario: `docker compose restart redis`
4. Reiniciar el worker después de que Redis esté disponible.

Las tareas encoladas mientras Redis estaba caído **no se pierden** si el worker aún no
las había confirmado (`acks_late=True`). Sí se pierden si fueron encoladas pero Redis
cayó antes de que el worker arrancara.

### Circuit breaker abierto — source saltado

Síntoma: logs con `skipping source X` o evidencia de una fuente ausente en DB.

Un source se desactiva cuando acumula ≥ 5 fallos en 300 segundos. Se restablece solo.

Para forzar reset manual:

```bash
redis-cli del circuit:orcid:failures
redis-cli del circuit:openalex:failures
redis-cli del circuit:unmsm_directory:failures
redis-cli del circuit:tavily:failures
```

### Campos de log estructurado

Cada tarea emite los siguientes campos en sus líneas de log:

| Campo | Aparece en | Significado |
|---|---|---|
| `professor_id` | start / done / crash / persisted | UUID del profesor |
| `name` | start | Nombre completo |
| `status` | persisted | `validated` / `not_found` |
| `evidence_count` | persisted | Número de registros guardados en `professor_evidence` |
| `error` | crash | Excepción que causó el fallo |

Ejemplo de flujo exitoso:

```
validation start | professor_id=... | name=Ciro Rodriguez Rodriguez
validation persisted | professor_id=... | status=validated | evidence_count=6
validation done  | professor_id=...
```

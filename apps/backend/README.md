# Puntualo — Backend

FastAPI + Celery + PostgreSQL + Redis.

Dos pipelines asíncronos sobre el mismo broker:

1. **Validación de profesores** — valida y enriquece perfiles de profesores UNMSM contra cuatro fuentes externas: directorio UNMSM, OpenAlex, ORCID y Tavily.
2. **Resumen ejecutivo IA** — genera un resumen (pros/cons) por profesor con Google Gemini a partir de los comentarios publicados.

---

## TL;DR — arranque rápido

Necesitas **4 terminales** (Docker, API, worker, beat). Desde la raíz del monorepo:

```bash
# 0. (una sola vez) entorno Python + dependencias
mamba activate puntualo            # o: conda activate puntualo
pip install -r apps/backend/requirements.txt

# 0b. (una sola vez) crear el .env del backend
cp apps/backend/.env.example apps/backend/.env
#    y rellena: DATABASE_URL, SECRET_KEY, JWT_SECRET, GEMINI_API_KEY (ver tabla abajo)

# 1. Infra (Postgres + Redis) — déjalo corriendo
docker compose up -d postgres redis

# 2. Migraciones (una vez por cambio de esquema)
cd apps/backend && alembic upgrade head

# 3. API            (terminal A)
cd apps/backend && uvicorn app.main:app --reload --port 8000

# 4. Worker Celery  (terminal B) — procesa validación + resumen IA + score
cd apps/backend && celery -A app.core.celery_app worker -l info

# 5. Beat scheduler (terminal C) — red de respaldo del resumen IA (cada 15 min)
cd apps/backend && celery -A app.core.celery_app beat -l info
```

> Sin el **worker** (paso 4) ninguna tarea asíncrona se ejecuta: quedan encoladas en Redis sin procesarse.
> El **beat** (paso 5) solo hace falta para que el resumen IA se regenere automáticamente; para validación no es necesario.

---

## Requisitos previos

- Docker + Docker Compose
- Python **3.13** en un entorno `puntualo` (mamba/conda)
- Dependencias instaladas: `pip install -r apps/backend/requirements.txt`
- Archivo `apps/backend/.env` (copiado de `.env.example` y completado — ver tabla)

Si el entorno `puntualo` no existe todavía:

```bash
mamba create -n puntualo python=3.13 -y
mamba activate puntualo
pip install -r apps/backend/requirements.txt
```

Todos los comandos de Python/alembic/celery/uvicorn se corren **desde `apps/backend`** y **con el entorno `puntualo` activado**. Tanto la API como el worker leen el mismo `apps/backend/.env` automáticamente (`load_dotenv()` en `app/core/config.py`); no hace falta exportar variables a mano.

---

## Arranque en desarrollo (detallado)

### 1. Infraestructura (PostgreSQL + Redis)

Desde la raíz del monorepo:

```bash
docker compose up -d postgres redis
```

Verificaciones:

```bash
docker compose ps                            # postgres y redis en estado "Up"
docker exec puntualo_redis redis-cli ping    # → PONG
```

Postgres queda en `localhost:5432` (`admin` / `admin123`, db `puntualo_db`); Redis en `localhost:6379`.

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

Docs interactivas en http://localhost:8000/docs.

### 4. Worker Celery

En una terminal aparte, mismo directorio y mismo `.env`:

```bash
cd apps/backend
celery -A app.core.celery_app worker -l info
```

No hay routing de colas configurado: **todas** las tareas (validación, resumen IA, recálculo de score) van a la cola por defecto `celery`, así que un solo worker las procesa todas. Si quieres ser explícito puedes añadir `-Q celery`.

### 5. Beat scheduler (opcional pero recomendado)

Solo necesario para el **resumen IA**. El beat dispara cada `NLP_SUMMARY_BEAT_SECONDS` (default 900 s = 15 min) la tarea `nlp.enqueue_pending_summaries`, que busca profesores que ameritan resumen y los encola para que el worker los procese. Es la red de respaldo del hook inline (ver sección de Resumen IA).

```bash
cd apps/backend
celery -A app.core.celery_app beat -l info
```

---

## Resumen ejecutivo IA (Gemini)

Genera/actualiza una fila en `professor_ai_summaries` (campos `summary`, `pros`, `cons`) por profesor.

### Cuándo se genera (guards)

La generación **solo procede** si el profesor cumple **ambas** condiciones (`app/services/nlp/summary_generator.py`):

1. `validation_status == "validated"`, y
2. tiene **≥ `NLP_SUMMARY_MIN_REVIEWS`** comentarios con `status = 'published'` (default **5**).

### Cómo se dispara

Hay dos caminos, y ambos requieren que **el worker esté corriendo** para ejecutar la tarea `nlp.generate_summary`:

- **Hook inline (post-commit):** al crear una evaluación vía la API (`evaluation_service.create`), un hook encola el resumen. Está detrás del flag **`IA_SUMMARY_HOOK_ENABLED`** (default `false`). Con el flag en `false` el hook es un no-op y **no encola nada**. Ponlo en `true` en tu `.env` para activarlo.
- **Beat scheduler (red de respaldo):** `nlp.enqueue_pending_summaries` corre cada 15 min, detecta profesores validados con ≥5 comentarios sin resumen (o con suficientes evaluaciones nuevas) y los encola. Es el único camino que recoge comentarios insertados **directamente en la BD** (que se saltan el hook inline).

> Nota: el flag se lee al arrancar el proceso. Si cambias `IA_SUMMARY_HOOK_ENABLED`, **reinicia la API y el worker**.

### Forzar un resumen manualmente (debug / pruebas)

Sin esperar al beat, para un `professor_id` concreto:

```bash
cd apps/backend
python -c "import asyncio; from app.tasks.nlp_tasks import _run_summary; \
asyncio.run(_run_summary('<professor_id>', force=False))"
```

Esto replica exactamente lo que hace el worker: crea el `AiJob`, llama a Gemini y hace upsert en `professor_ai_summaries`. Usa `force=True` para regenerar aunque ya exista. Requiere `GEMINI_API_KEY` válido.

---

## Variables de entorno (`apps/backend/.env`)

Copia `apps/backend/.env.example` → `apps/backend/.env`. Los **secrets** (sin default) hay que rellenarlos sí o sí; el resto tiene defaults razonables.

### Imprescindibles

| Variable | Descripción | Ejemplo / Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL (psycopg2; la capa async lo convierte a asyncpg solo) | `postgresql://admin:admin123@localhost:5432/puntualo_db` |
| `SECRET_KEY` | Clave de firma JWT | *(secret)* |
| `JWT_SECRET` | Alias de `SECRET_KEY` usado en algunos flows | *(secret)* |
| `GEMINI_API_KEY` | API key de Google Gemini para el resumen IA | *(secret)* |

### Celery / Redis

| Variable | Descripción | Default |
|---|---|---|
| `REDIS_URL` | Cache de la app (db 0) | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | Cola de tareas (db 1) | `redis://localhost:6379/1` |
| `CELERY_RESULT_BACKEND` | Resultados Celery (db 2) | `redis://localhost:6379/2` |

### Resumen IA / NLP

| Variable | Descripción | Default |
|---|---|---|
| `IA_SUMMARY_HOOK_ENABLED` | Activa el hook inline post-commit que encola el resumen | `false` |
| `GEMINI_MODEL` | Modelo de Gemini | `gemini-2.5-flash` |
| `NLP_SUMMARY_MIN_REVIEWS` | Mínimo de comentarios publicados para generar | `5` |
| `NLP_SUMMARY_MAX_REVIEWS` | A partir de aquí aplica sampling | `100` |
| `NLP_SUMMARY_BEAT_SECONDS` | Período del beat (segundos) | `900` |
| `IA_SUMMARY_THRESHOLD` | Evaluaciones nuevas para considerar un resumen "stale" | `10` |

### Pipeline de validación

| Variable | Descripción | Default |
|---|---|---|
| `TAVILY_API_KEY` | API key para búsqueda web (enriquecimiento) | *(secret)* |
| `TAVILY_BUDGET_HARD_CAP` | Llamadas Tavily máximas por mes | `950` |
| `CIRCUIT_THRESHOLD` | Fallos consecutivos para abrir el circuit breaker | `5` |
| `CIRCUIT_RESET_SECONDS` | Segundos hasta que el circuit breaker se cierra | `300` |

Hay más tuneables (TTLs de cache, timeouts HTTP, moderación de comentarios) documentados en `.env.example`.

---

## Arranque con Docker (worker en contenedor)

El `docker-compose.yml` de la raíz incluye un servicio `worker`:

```bash
docker compose up -d         # postgres + redis + worker
```

> **Importante:** el servicio `worker` usa `env_file: apps/backend/.env`, y ese `.env` apunta a `localhost` para Postgres y Redis. Dentro del contenedor `localhost` es el propio contenedor, **no** los otros servicios, así que con la configuración actual el worker dockerizado no conecta. Para desarrollo, el camino recomendado es levantar **solo `postgres` y `redis`** en Docker y correr API + worker + beat **localmente** (secciones 3–5). Si quieres el worker en Docker, cambia en su entorno los hosts a `postgres` y `redis` (los nombres de servicio del compose) en vez de `localhost`. El compose tampoco define un servicio de `beat`.

---

## Endpoints de validación

### Disparar validación inicial

Al crear un profesor (`POST /professors`), el endpoint encola automáticamente la tarea de validación. El campo `validation_status` comienza en `pending_validation`.

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

### El resumen IA no se genera

Lista de chequeo en orden:

1. **¿Hay worker corriendo?** `celery -A app.core.celery_app worker -l info`. Sin él la tarea queda encolada y nada la ejecuta. Para ver si hay tareas atascadas: `docker exec puntualo_redis redis-cli -n 1 LLEN celery`.
2. **¿El profesor cumple los guards?** `validated` + ≥ `NLP_SUMMARY_MIN_REVIEWS` comentarios `published`. Si no, la tarea corre pero hace skip (`result_payload.reason = guard_not_met`).
3. **¿Cómo creaste los comentarios?**
   - Vía API → necesitas `IA_SUMMARY_HOOK_ENABLED=true` **y** reiniciar API+worker tras cambiar el flag.
   - Directo en la BD → el hook inline no se entera; depende del **beat** (o dispáralo manual, ver arriba).
4. **¿`GEMINI_API_KEY` válido?** Si la key falla, el `AiJob` queda en `status='failed'` con el error en `error_message`.

Inspeccionar el último job:

```bash
cd apps/backend
python -c "from app.db.session import SessionLocal; from sqlalchemy import select; \
from app.models.ai_job import AiJob; db=SessionLocal(); \
j=db.execute(select(AiJob).where(AiJob.job_type=='summary_generation').order_by(AiJob.started_at.desc())).scalars().first(); \
print(j.status, j.result_payload, j.error_message) if j else print('sin jobs')"
```

### El worker dice "Event loop is closed"

Síntoma: la segunda tarea en el mismo proceso worker crashea con `RuntimeError: Event loop is closed`.

Causa: singleton de Redis o pool de SQLAlchemy atado al loop anterior.

Solución: el código ya reinicializa `redis_client` al inicio de cada tarea y usa `NullPool` en el engine de DB. Si el error reaparece, verificar que ningún módulo haga `from app.utils.cache import redis_client` (importación directa crea binding estático). Debe ser `import app.utils.cache as _cache_mod` con acceso vía atributo.

### El worker no recibe tareas (broker caído)

Síntomas en logs del worker:

```
[ERROR] consumer: Cannot connect to redis://localhost:6379/1
```

Pasos:
1. Verificar que Redis está corriendo: `docker compose ps redis`
2. Verificar conexión: `docker exec puntualo_redis redis-cli ping`
3. Reiniciar Redis si es necesario: `docker compose restart redis`
4. Reiniciar el worker después de que Redis esté disponible.

Las tareas encoladas mientras Redis estaba caído **no se pierden** si el worker aún no las había confirmado (`acks_late=True`). Sí se pierden si fueron encoladas pero Redis cayó antes de que el worker arrancara.

### Circuit breaker abierto — source saltado

Síntoma: logs con `skipping source X` o evidencia de una fuente ausente en DB.

Un source se desactiva cuando acumula ≥ 5 fallos en 300 segundos. Se restablece solo.

Para forzar reset manual:

```bash
docker exec puntualo_redis redis-cli del circuit:orcid:failures
docker exec puntualo_redis redis-cli del circuit:openalex:failures
docker exec puntualo_redis redis-cli del circuit:unmsm_directory:failures
docker exec puntualo_redis redis-cli del circuit:tavily:failures
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

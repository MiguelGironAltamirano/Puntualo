# 4. Automatización de pruebas y CI/CD

> **Responsable (WS-C):** Miguel (pipeline CI) · Tarqui/Mathias (implementación de tests) · Sevan (carga/e2e) · **Estado:** 🟡
> Suite automatizada (API, unit/integración, rendimiento) con **evidencia de
> ejecución** e integración a **GitHub Actions**. El inventario está en
> [PRUEBAS.md](PRUEBAS.md).

## 4.1 Estado de la suite

| Tipo | Herramienta | Estado |
|---|---|---|
| Unit / Integración / API | `pytest` | 🟡 auth/humo (Miguel) ✅ verdes; resto de esqueletos por implementar |
| Rendimiento | `Locust` | ✅ implementada con evidencia |
| UI / e2e | Playwright/Cypress | ⬜ sin runner |

> **Avance WS-C (Miguel):** `unit/test_security.py`, `integration/test_auth_api.py` y
> `smoke/test_smoke.py` implementados y **verdes** (22 casos). Pipeline
> `.github/workflows/ci.yml` creado con JUnit + cobertura. Suite completa (excl.
> `test_report_service`): **55 passed, 34 skipped**. `core/security.py` al 100%.

## 4.2 Trabajo de implementación (decidido: implementar y ejecutar)

Orden sugerido (Must primero):
1. [x] `unit/test_security.py` — hashing + JWT ✅ (Miguel)
2. [x] `integration/test_auth_api.py` — login/registro/refresh ✅ (Miguel)
3. [ ] `integration/test_access_control.py` — 401/403 (Sevan)
4. [ ] `integration/test_comments_flow.py` — ciclo de vida (Tarqui)
5. [x] `smoke/test_smoke.py` — arranque + `/health/db` ✅ (Miguel)
6. [ ] Should: profesores, cursos, moderación con DB, scoring (Mathias/Tarqui)

> Requisito técnico ✅ **resuelto**: fixture de cliente HTTP en `conftest.py`.
> Como los endpoints de auth/health usan `Session` **síncrona** (`get_db`), se
> añadió `api_client` (`TestClient` + override de `get_db` a SQLite en memoria) en
> lugar de `httpx.AsyncClient`. También se registró `gen_random_uuid()` para SQLite
> y se corrigieron dos bugs de la fixture `test_db` compartida (ver §4.6).

## 4.3 Evidencia de ejecución (a generar)

Comandos objetivo (recordar `mamba activate puntualo`):

```bash
# Suite con reporte JUnit + cobertura HTML
pytest --junitxml=reports/junit.xml --cov=app --cov-report=html:reports/coverage
```

- [x] `reports/junit.xml` generado
- [x] `reports/coverage/index.html` generado (+ `reports/coverage.xml`)
- [ ] Capturas para la expo
- [x] Prueba de carga ya tiene evidencia: `apps/tests/load-test/results/reporte.html`

## 4.4 Pipeline GitHub Actions (`.github/workflows/ci.yml`)

Jobs propuestos:

| Job | Contenido | Artefactos | Autor |
|---|---|---|---|
| `test-backend` | `pytest` + coverage + JUnit | `junit.xml`, `coverage/` | **Miguel** |
| `gate` | requiere que los checks pasen en PR a `main` | — | **Miguel** |
| `lint` | ruff (backend) + eslint (frontend) | — | Miguel (opcional) |
| `test-frontend` | build + e2e (Playwright) | — | Sevan |
| `security` | `pip-audit`, `pnpm audit`, `gitleaks`, `bandit` | reportes | Mathias (WS-D) |

> El núcleo del pipeline (correr la suite y el gate en cada PR) es `test-backend` +
> `gate`. Los jobs `security` y `test-frontend` se suman después, aportados por sus
> respectivos flujos, reusando la misma estructura del workflow.

- [x] Workflow creado (`test-backend` + `gate`)
- [x] Ejecuta en push/PR a `main` (+ `workflow_dispatch`)
- [x] Sube artefactos (coverage, JUnit) vía `upload-artifact`
- [ ] Badge de estado (opcional)

> Nota: el deploy ya existe (Vercel + VM Oracle). Este pipeline es de **verificación**,
> no de despliegue.

## 4.5 Métricas que produce la automatización

Alimentan el [ítem 7](07_documentacion_y_metricas.md):
- Cobertura de líneas/ramas.
- N.º de pruebas / tasa de éxito.
- Tiempo de ejecución de la suite.
- Métricas de rendimiento (p50/p95, throughput, tasa de error) de Locust.

## 4.6 Correcciones a la infraestructura de pruebas (conftest compartido)

Al implementar los tests de auth se detectaron **bugs preexistentes** en la fixture
`test_db` de `tests/conftest.py` que impedían correr cualquier prueba de integración
sobre SQLite (afectaban a `test_report_service`, ya "verde" en el papel pero en
realidad **6 errores**). Se corrigieron a nivel de infraestructura (no toca la lógica
de ningún test):

1. **`create_all` abortaba** al toparse con tablas de DDL solo-Postgres (JSONB, ARRAY,
   pgvector, server-defaults `'{}'::text[]`). Ahora se crea el esquema *best-effort*,
   omitiendo esas tablas (las pruebas usan un subconjunto compatible).
2. **Sesión mal instanciada**: `AsyncSession(...)()` (una instancia llamada como
   factory) lanzaba `TypeError`. Corregido al patrón estándar.
3. **`gen_random_uuid()`** (server_default de las PK) no existe en SQLite → se registra
   como función del conector.

> **Pendiente para WS-B (Tarqui):** las fixtures compartidas `test_user`/`test_professor`/
> `test_comment` siguen desalineadas con el modelo actual (ids como `str` en vez de
> `UUID`, `role="user"` fuera del check `student/admin`, `hashed_password=None`, y el
> modelo `Comment` ya no tiene `content` sino `text` + `evaluation_id`/`course_id`/
> `modality` obligatorios). Por eso `test_report_service` queda excluido del CI hasta
> que se actualicen. Es trabajo de su módulo, fuera del alcance de auth.

## Entregable (DoD)

- [x] Esqueletos Must (auth/humo de Miguel) implementados y **verdes** (22 casos)
- [x] Coverage + JUnit archivados (`reports/junit.xml`, `reports/coverage/`)
- [x] Workflow GitHub Actions funcionando (`ci.yml`: `test-backend` + `gate`)
- [ ] Evidencia lista para la demo ([06](06_demo_en_vivo.md)) — capturas pendientes

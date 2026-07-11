# Plan de Pruebas — Puntualo

Clasificación de las pruebas del proyecto según tres ejes, priorización MoSCoW,
y ubicación exacta (carpeta/archivo) de cada una.

Estado: ✅ implementada · 🟡 archivo creado (esqueleto, sin desarrollo) · ⬜ no existe.

> Este archivo es el **inventario técnico** (qué pruebas existen y su implementación).
> El **diseño formal de casos** (técnicas, entradas y resultado esperado) vive en
> [03_diseno_de_casos.md](03_diseno_de_casos.md). El índice y la organización del
> equipo están en [README.md](README.md).

## Responsables por grupo de pruebas

| Integrante | Grupo de pruebas a su cargo |
|---|---|
| **Tarqui** | Unitarias (moderación, rate limiter, abuso, scoring, hashtags, paginación util) e integración de evaluaciones (servicio de reportes, flujo de comentarios, moderación con DB) |
| **Mathias** | API (endpoints de profesores/cursos/catálogos, paginación API, score de profesor, cache, pentest) |
| **Sevan** | Sistema y aceptación (control de acceso, carga, e2e frontend, componentes frontend, estrés) |
| **Miguel** | Módulo de autenticación (hashing/JWT, autenticación API), humo y regresión en CI (pipeline GitHub Actions) |
| **Cicilis** | Usabilidad (protocolo manual, documentación de resultados) |

## Ejes de clasificación

- **Nivel:** Unitaria · Integración · Sistema · Aceptación
- **Tipo:**
  - Funcional
  - No Funcional: Regresión · Seguridad · Usabilidad · Rendimiento
  - Asociada al Cambio: Regresión · Humo
- **Técnica:** Caja Negra · Caja Blanca

## Organización de carpetas

```
apps/
├── backend/tests/            # pruebas de código (pytest) — corren contra el fuente
│   ├── conftest.py           # fixtures compartidas (DB SQLite en memoria, usuarios…)
│   ├── unit/                 # Unitarias · Caja Blanca · sin infra real
│   ├── integration/          # Integración · con DB / cliente HTTP / mocks de infra
│   └── smoke/                # Humo · arranque + health
└── tests/                    # pruebas de sistema/aceptación (NO pytest)
    ├── load-test/            # Carga nominal (Locust) — implementada
    ├── stress-test/          # Estrés / punto de quiebre (Locust) — reservado
    ├── security/             # Pentest / seguridad automatizada — reservado
    └── e2e/specs/            # Aceptación end-to-end del frontend (Playwright/Cypress)
```

## ¿Tenemos todos los tipos necesarios? — Verificación de cobertura

| Eje / categoría | ¿Cubierta? | Detalle |
|---|---|---|
| **Nivel** Unitaria | ✅ | `backend/tests/unit/` |
| **Nivel** Integración | ✅ | `backend/tests/integration/` |
| **Nivel** Sistema | ✅ | `tests/load-test/` (carga) + `backend/tests/smoke/` |
| **Nivel** Aceptación | 🟡 | `tests/e2e/` reservado — **falta runner e2e** (Playwright/Cypress no instalado) |
| **Tipo** Funcional | ✅ | mayoría de unit/integration |
| **No Funcional** Rendimiento | ✅ | `tests/load-test/` (implementada) |
| **No Funcional** Seguridad | 🟡 | `integration/test_access_control.py` (esqueleto) + `tests/security/` (reservado) |
| **No Funcional** Usabilidad | ⬜ | sin pruebas — requiere protocolo manual o herramienta específica |
| **No Funcional** Regresión | 🟡 | existe la suite, **falta automatizarla en CI** con reporte archivado |
| **Cambio** Humo | 🟡 | `backend/tests/smoke/test_smoke.py` (esqueleto) |
| **Técnica** Caja Blanca | ✅ | unit/ y varias de integration/ |
| **Técnica** Caja Negra | ✅ | load-test + tests de API |

**Huecos reales que conviene resolver:**
1. **Aceptación (e2e)**: no hay runner de frontend configurado. Carpeta reservada.
2. **Usabilidad**: no hay ninguna prueba; hoy es un vacío total.
3. **Regresión en CI**: la suite existe pero no corre automáticamente ni archiva resultados (JUnit/coverage).
4. **Frontend en general**: cero pruebas de componentes; no hay `vitest`/`jest`.

## Registro de resultados (a hoy)

- Backend (`pytest`): **no hay registro de resultados** archivado.
- Carga (Locust): **sí** — `apps/tests/load-test/ANALISIS.md` (2026-06-27, 0% error, p50 910 ms) y `results/reporte.html`.

---

# Priorización MoSCoW

Formato: **Nivel · Tipo · Técnica** · Estado · 👤 Responsable · `ruta/archivo`.

## Must have

- Filtro heurístico de moderación — Unitaria · Funcional · Caja Blanca · ✅ · 👤 **Tarqui** · `apps/backend/tests/unit/test_moderation.py`
- Rate limiter de reportes — Unitaria · Funcional · Caja Blanca · ✅ · 👤 **Tarqui** · `apps/backend/tests/unit/test_rate_limiter.py`
- Detección de abuso en reportes — Unitaria · Funcional · Caja Blanca · ✅ · 👤 **Tarqui** · `apps/backend/tests/unit/test_rate_limiter.py`
- Servicio de reportes (crear/escalar/score) — Integración · Funcional · Caja Blanca · ✅ · 👤 **Tarqui** · `apps/backend/tests/integration/test_report_service.py`
- Carga backend 50 usuarios — Sistema · No Funcional (Rendimiento) · Caja Negra · ✅ · 👤 **Sevan** · `apps/tests/load-test/locustfile.py`
- Hashing y JWT (core/security) — Unitaria · Funcional · Caja Blanca · 🟡 · 👤 **Miguel** · `apps/backend/tests/unit/test_security.py`
- Autenticación API (login/registro/refresh) — Integración · Funcional · Caja Blanca · 🟡 · 👤 **Miguel** · `apps/backend/tests/integration/test_auth_api.py`
- Control de acceso (401/403) — Integración · No Funcional (Seguridad) · Caja Negra · 🟡 · 👤 **Sevan** · `apps/backend/tests/integration/test_access_control.py`
- Flujo de comentarios (crear→moderar→publicar) — Integración · Funcional · Caja Blanca · 🟡 · 👤 **Tarqui** · `apps/backend/tests/integration/test_comments_flow.py`
- Humo (arranque + `/health/db`) — Sistema · Asociada al Cambio (Humo) · Caja Negra · 🟡 · 👤 **Miguel** · `apps/backend/tests/smoke/test_smoke.py`

## Should have

- Endpoints de profesores (lista/búsqueda/detalle) — Integración · Funcional · Caja Negra · 🟡 · 👤 **Mathias** · `apps/backend/tests/integration/test_professors_api.py`
- Endpoints de cursos y catálogos — Integración · Funcional · Caja Negra · 🟡 · 👤 **Mathias** · `apps/backend/tests/integration/test_catalogs_courses_api.py`
- Paginación de listados — Integración · Funcional · Caja Negra · 🟡 · 👤 **Mathias** · `apps/backend/tests/integration/test_pagination_api.py`
- Score de evaluación — Unitaria · Funcional · Caja Blanca · 🟡 · 👤 **Tarqui** · `apps/backend/tests/unit/test_scoring.py`
- Score de profesor (agregado) — Unitaria · Funcional · Caja Blanca · 🟡 · 👤 **Mathias** · `apps/backend/tests/unit/test_professor_score.py`
- Moderación con DB (términos baneados/l33t) — Integración · Funcional · Caja Blanca · 🟡 · 👤 **Tarqui** · `apps/backend/tests/integration/test_moderation_db.py`
- Suite de regresión en CI (con reporte archivado) — Integración · Asociada al Cambio (Regresión) · Caja Negra · ⬜ · 👤 **Miguel** · (config CI, no un archivo de test)

## Could have

- Cacheo Redis (hit/miss/TTL) — Integración · No Funcional (Rendimiento) · Caja Blanca · 🟡 · 👤 **Mathias** · `apps/backend/tests/integration/test_cache.py`
- Normalizador de hashtags — Unitaria · Funcional · Caja Blanca · 🟡 · 👤 **Tarqui** · `apps/backend/tests/unit/test_hashtag_normalizer.py`
- Helper de paginación — Unitaria · Funcional · Caja Blanca · 🟡 · 👤 **Tarqui** · `apps/backend/tests/unit/test_pagination.py`
- Aceptación e2e frontend — Aceptación · Funcional · Caja Negra · 🟡 · 👤 **Sevan** · `apps/tests/e2e/specs/auth.spec.ts`
- Componentes frontend (render) — Unitaria · Funcional · Caja Blanca · ⬜ · 👤 **Sevan** · (requiere `vitest`/`jest`, sin ubicar aún)
- Usabilidad (recorridos clave) — Aceptación · No Funcional (Usabilidad) · Caja Negra · ⬜ · 👤 **Cicilis** · (protocolo manual, sin archivo)

## Won't have (por ahora)

- Estrés / punto de quiebre — Sistema · No Funcional (Rendimiento) · Caja Negra · 🟡 · 👤 **Sevan** · `apps/tests/stress-test/locustfile.py`
- Penetración / seguridad automatizada — Sistema · No Funcional (Seguridad) · Caja Negra · 🟡 · 👤 **Mathias** · `apps/tests/security/`

---

# Checklist detallado

## MUST HAVE

### ✅ Filtro heurístico de moderación · 👤 Tarqui
`apps/backend/tests/unit/test_moderation.py` — _Unitaria · Funcional · Caja Blanca_
Verifica `app/utils/moderation.py::heuristic_filter` sin base de datos.
- [x] Comentario limpio → `action == "allow"`, `spam_score < 0.4`
- [x] Email y URL suman al `spam_score`
- [x] Caracteres de ancho cero / ofuscación detectados
- [x] Mayúsculas excesivas y caracteres repetidos elevan el score
- [x] Teléfono formato Perú detectado
- [x] Comentarios normales con números/puntuación pasan

### ✅ Rate limiter de reportes · 👤 Tarqui
`apps/backend/tests/unit/test_rate_limiter.py::TestReportRateLimiter` — _Unitaria · Funcional · Caja Blanca_
Verifica `app/utils/rate_limiter.py::ReportRateLimiter` con Redis mockeado.
- [x] Primer reporte permitido; `remaining` correcto
- [x] Dentro del límite permitido
- [x] Límite excedido bloquea
- [x] Registro en Redis (`zadd` + `expire`)
- [x] Timestamps fuera de ventana ignorados

### ✅ Detección de abuso en reportes · 👤 Tarqui
`apps/backend/tests/unit/test_rate_limiter.py::TestReportAbuseDetector` — _Unitaria · Funcional · Caja Blanca_
- [x] Usuario nuevo no es abusador
- [x] Usuario en umbral es marcado
- [x] Incremento y reseteo del contador

### ✅ Servicio de reportes · 👤 Tarqui
`apps/backend/tests/integration/test_report_service.py` — _Integración · Funcional · Caja Blanca_
Verifica `app/modules/evaluations/service/report_service.py` con DB real.
- [x] Creación exitosa
- [x] Rate limit → `ReportRateLimitError`
- [x] Abuso → `ReportAbuseDetectedError`
- [x] Comentario inexistente → `CommentNotFoundError`
- [x] Score alto escala a `HIDDEN_PENDING_REVIEW`
- [x] Score ponderado por razón

### ✅ Carga backend — 50 usuarios concurrentes · 👤 Sevan
`apps/tests/load-test/locustfile.py` — _Sistema · No Funcional (Rendimiento) · Caja Negra_
- [x] Escenario Locust (tareas GET ponderadas) definido
- [x] Corrida ejecutada, resultados en `ANALISIS.md` + `results/reporte.html`

### 🟡 Hashing de contraseñas y JWT · 👤 Miguel
`apps/backend/tests/unit/test_security.py` — _Unitaria · Funcional · Caja Blanca_
Bajo prueba: `app/core/security.py`.
- [ ] Hash y verificación de contraseña correcta
- [ ] Contraseña incorrecta no verifica
- [ ] Crear access token con payload/expiración esperados
- [ ] Decodificar token válido expone claims
- [ ] Token expirado rechazado
- [ ] Token con firma alterada rechazado

### 🟡 Autenticación API · 👤 Miguel
`apps/backend/tests/integration/test_auth_api.py` — _Integración · Funcional · Caja Blanca_
Bajo prueba: `app/modules/auth/`.
- [ ] Registro de usuario nuevo → 201
- [ ] Login válido devuelve token
- [ ] Login inválido → 401
- [ ] Flujo de refresh token

### 🟡 Control de acceso · 👤 Sevan
`apps/backend/tests/integration/test_access_control.py` — _Integración · No Funcional (Seguridad) · Caja Negra_
- [ ] `/professors` sin token → 401
- [ ] Endpoint de escritura sin token → 401
- [ ] Rol insuficiente → 403

### 🟡 Flujo de comentarios · 👤 Tarqui
`apps/backend/tests/integration/test_comments_flow.py` — _Integración · Funcional · Caja Blanca_
- [ ] Comentario limpio → PUBLISHED
- [ ] Comentario que dispara moderación → retenido
- [ ] Transiciones de estado correctas

### 🟡 Humo · 👤 Miguel
`apps/backend/tests/smoke/test_smoke.py` — _Sistema · Asociada al Cambio (Humo) · Caja Negra_
- [ ] La app se levanta sin errores
- [ ] `/health/db` → 200
- [ ] Esquema OpenAPI disponible

---

## SHOULD HAVE

### 🟡 Endpoints de profesores · 👤 Mathias
`apps/backend/tests/integration/test_professors_api.py` — _Integración · Funcional · Caja Negra_
- [ ] Lista paginada
- [ ] Búsqueda por nombre
- [ ] Detalle de profesor
- [ ] Id inexistente → 404

### 🟡 Endpoints de cursos y catálogos · 👤 Mathias
`apps/backend/tests/integration/test_catalogs_courses_api.py` — _Integración · Funcional · Caja Negra_
- [ ] `/courses` paginado
- [ ] `/catalogs/universities` responde
- [ ] Catálogo vacío → lista vacía

### 🟡 Paginación de listados · 👤 Mathias
`apps/backend/tests/integration/test_pagination_api.py` — _Integración · Funcional · Caja Negra_
- [ ] `page_size` respetado
- [ ] Navegación entre páginas
- [ ] Página fuera de rango → vacío

### 🟡 Score de evaluación · 👤 Tarqui
`apps/backend/tests/unit/test_scoring.py` — _Unitaria · Funcional · Caja Blanca_
Bajo prueba: `app/modules/evaluations/scoring.py`.
- [ ] Score dentro de rango válido
- [ ] Pesos aplicados correctamente
- [ ] Valores de borde

### 🟡 Score de profesor (agregado) · 👤 Mathias
`apps/backend/tests/unit/test_professor_score.py` — _Unitaria · Funcional · Caja Blanca_
Bajo prueba: `app/modules/professors/service.py`.
- [ ] Sin evaluaciones → score neutro/None
- [ ] Agrega varias evaluaciones
- [ ] Bordes de thresholds

### 🟡 Moderación con DB · 👤 Tarqui
`apps/backend/tests/integration/test_moderation_db.py` — _Integración · Funcional · Caja Blanca_
Bajo prueba: `app/utils/moderation.py` + `app/models/banned_term.py`.
- [ ] Término baneado eleva score / bloquea
- [ ] L33t de término baneado detectado
- [ ] Comentario limpio pasa con etapa DB activa

### ⬜ Suite de regresión en CI · 👤 Miguel
(config de CI, no un archivo de test) — _Integración · Asociada al Cambio (Regresión) · Caja Negra_
- [ ] Ejecución automatizada de toda la suite en cada push/PR
- [ ] Reporte JUnit/coverage archivado como evidencia

---

## COULD HAVE

### 🟡 Cacheo Redis · 👤 Mathias
`apps/backend/tests/integration/test_cache.py` — _Integración · No Funcional (Rendimiento) · Caja Blanca_
Bajo prueba: `app/utils/cache.py`.
- [ ] Miss y luego hit
- [ ] Expiración por TTL
- [ ] Invalidación

### 🟡 Normalizador de hashtags · 👤 Tarqui
`apps/backend/tests/unit/test_hashtag_normalizer.py` — _Unitaria · Funcional · Caja Blanca_
Bajo prueba: `app/utils/hashtag_normalizer.py`.
- [ ] Minúsculas y trim
- [ ] Acentos normalizados
- [ ] Variantes equivalentes → misma clave

### 🟡 Helper de paginación · 👤 Tarqui
`apps/backend/tests/unit/test_pagination.py` — _Unitaria · Funcional · Caja Blanca_
Bajo prueba: `app/utils/pagination.py`.
- [ ] offset/limit calculados
- [ ] Metadato de total de páginas
- [ ] Valores inválidos → defaults

### 🟡 Aceptación e2e (frontend) · 👤 Sevan
`apps/tests/e2e/specs/auth.spec.ts` — _Aceptación · Funcional · Caja Negra_
Requiere instalar runner (Playwright/Cypress).
- [ ] Login válido → home autenticado
- [ ] Login inválido → mensaje de error
- [ ] Búsqueda de profesor muestra resultados
- [ ] Crear comentario autenticado

### ⬜ Componentes frontend (render) · 👤 Sevan
(sin ubicar — requiere `vitest`/`jest`) — _Unitaria · Funcional · Caja Blanca_
- [ ] Componentes clave renderizan
- [ ] Estados de carga/error

### ⬜ Usabilidad (recorridos clave) · 👤 Cicilis
(protocolo manual, sin archivo) — _Aceptación · No Funcional (Usabilidad) · Caja Negra_
Evidencia previa: `docs/superpowers/ux/resultados_pruebas_usabilidad.md` (SUS 87.5).
- [ ] Recorridos principales sin fricción

---

## WON'T HAVE (por ahora)

### 🟡 Estrés / punto de quiebre · 👤 Sevan
`apps/tests/stress-test/locustfile.py` — _Sistema · No Funcional (Rendimiento) · Caja Negra_
- [ ] Escalar carga por etapas hasta degradación

### 🟡 Penetración / seguridad automatizada · 👤 Mathias
`apps/tests/security/` — _Sistema · No Funcional (Seguridad) · Caja Negra_
- [ ] Definir herramienta y escenarios

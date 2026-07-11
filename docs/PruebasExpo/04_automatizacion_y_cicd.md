# 4. Automatización de pruebas y CI/CD

> **Responsable (WS-C):** Miguel (pipeline CI) · Tarqui/Mathias (implementación de tests) · Sevan (carga/e2e) · **Estado:** 🟡
> Suite automatizada (API, unit/integración, rendimiento) con **evidencia de
> ejecución** e integración a **GitHub Actions**. El inventario está en
> [PRUEBAS.md](PRUEBAS.md).

## 4.1 Estado de la suite

| Tipo | Herramienta | Estado |
|---|---|---|
| Unit / Integración / API | `pytest` | 🟡 5 pruebas reales + ~14 esqueletos en `skip` |
| Rendimiento | `Locust` | ✅ implementada con evidencia |
| UI / e2e | Playwright/Cypress | ⬜ sin runner |

## 4.2 Trabajo de implementación (decidido: implementar y ejecutar)

Orden sugerido (Must primero):
1. [ ] `unit/test_security.py` — hashing + JWT
2. [ ] `integration/test_auth_api.py` — login/registro/refresh
3. [ ] `integration/test_access_control.py` — 401/403
4. [ ] `integration/test_comments_flow.py` — ciclo de vida
5. [ ] `smoke/test_smoke.py` — arranque + `/health/db`
6. [ ] Should: profesores, cursos, moderación con DB, scoring

> Requisito técnico pendiente: **fixture de cliente HTTP** (`httpx.AsyncClient`
> sobre la app FastAPI) en `conftest.py` para todos los tests de API.

## 4.3 Evidencia de ejecución (a generar)

Comandos objetivo (recordar `mamba activate puntualo`):

```bash
# Suite con reporte JUnit + cobertura HTML
pytest --junitxml=reports/junit.xml --cov=app --cov-report=html:reports/coverage
```

- [ ] `reports/junit.xml` generado
- [ ] `reports/coverage/index.html` generado
- [ ] Capturas para la expo
- [ ] Prueba de carga ya tiene evidencia: `apps/tests/load-test/results/reporte.html`

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

- [ ] Workflow creado
- [ ] Ejecuta en push/PR
- [ ] Sube artefactos (coverage, JUnit)
- [ ] Badge de estado (opcional)

> Nota: el deploy ya existe (Vercel + VM Oracle). Este pipeline es de **verificación**,
> no de despliegue.

## 4.5 Métricas que produce la automatización

Alimentan el [ítem 7](07_documentacion_y_metricas.md):
- Cobertura de líneas/ramas.
- N.º de pruebas / tasa de éxito.
- Tiempo de ejecución de la suite.
- Métricas de rendimiento (p50/p95, throughput, tasa de error) de Locust.

## Entregable (DoD)

- [ ] Esqueletos Must implementados y **verdes**
- [ ] Coverage + JUnit archivados
- [ ] Workflow GitHub Actions funcionando
- [ ] Evidencia lista para la demo ([06](06_demo_en_vivo.md))

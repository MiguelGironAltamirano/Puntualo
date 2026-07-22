# 6. Demo en vivo

> **Responsable (WS-E):** Sevan · **Estado:** 🟡
> Ejecución en tiempo real de la suite o de un flujo representativo, mostrando
> **resultados reales** ante el jurado.
>
> **Evidencia disponible (medida 2026-07-15, lista para demo):**
> - Suite backend: **96 passed · 29 skipped · 0 failed** · cobertura **51%** global
>   (`core/security` 100%, `rate_limiter` 94%, `moderation` 70%). Reportes en `reports/`.
> - e2e frontend (Playwright): **3 casos verdes** (`apps/tests/e2e/specs/auth.spec.ts`).
> - Componentes frontend (Vitest): **8 casos verdes** (`Pagination`, `useAuthStore`).
> - Carga (Locust): `apps/tests/load-test/results/reporte.html` (0% error, p95 1.4 s).

## 6.1 Qué demostrar (opciones, elegir 1–2)

| Opción | Muestra | Duración | Impacto |
|---|---|---|---|
| A. Suite pytest en vivo | `pytest` corriendo + verde + coverage | ~2 min | Alto (evidencia directa) |
| B. Pipeline CI/CD | Push → GitHub Actions verde + artefactos | ~3 min | Alto (CI/CD se valora) |
| C. Prueba de carga | Locust en vivo o reporte + gráficas | ~2 min | Medio-Alto (rendimiento) |
| D. Escaneo de seguridad | `pip-audit`/`bandit` en vivo | ~1 min | Medio |

**Recomendado:** A + B (o A + C si el CI no está listo).

## 6.2 Guión paso a paso (opción A + B — ~5 min)

**Bloque 1 — Suite backend en vivo (~2 min)**
1. Abrir terminal y activar el entorno (`mamba activate puntualo`, o el `.venv` del repo).
2. Mostrar la estructura de `apps/backend/tests/` (unit / integración / smoke).
3. Ejecutar (desde `apps/backend/`):
   ```bash
   pytest tests --ignore=tests/integration/test_report_service.py \
     --cov=app --cov-report=term-missing
   ```
4. Señalar en la salida: **96 passed, 29 skipped, 0 failed** y la cobertura (**51%**).
   Destacar los módulos críticos: `core/security` 100%, `rate_limiter` 94%.
5. Abrir `reports/coverage/index.html` para el detalle visual de cobertura.

**Bloque 2 — Aceptación e2e + componentes (~1.5 min)**
6. Correr el e2e del login (Playwright, `apps/tests/e2e/`):
   ```bash
   pnpm test          # 3 casos: render, login inválido→error, login válido→/teachers
   ```
7. Correr los componentes frontend (Vitest, `apps/frontend/`):
   ```bash
   pnpm test          # 8 casos: Pagination, ResultsInfo, useAuthStore
   ```

**Bloque 3 — CI/CD y rendimiento (~1.5 min)**
8. Mostrar en GitHub → pestaña **Actions** el workflow `ci.yml` en **verde**
   (job `test-backend` + `gate`) y los artefactos (`junit.xml`, `coverage/`).
9. Abrir `apps/tests/load-test/results/reporte.html` (Locust): p95 1.4 s, 0% error, 50 usuarios.
10. Cerrar conectando con la tabla de métricas ([07](07_documentacion_y_metricas.md)).

## 6.3 Preparación (checklist previo)

- [x] Entorno con dependencias instaladas (backend `.venv` + `pnpm install` en frontend y e2e)
- [x] Suite backend pasa localmente (96 passed / 0 failed, 2026-07-15)
- [x] e2e Playwright y componentes Vitest pasan localmente (3 y 8 verdes)
- [x] Reportes pre-generados (`reports/coverage/index.html`, `results/reporte.html`)
- [ ] Navegador Chromium de Playwright instalado en la máquina de la demo (`pnpm exec playwright install chromium`)
- [ ] Conexión / proyector probados

## 6.4 Plan B (si algo falla en vivo)

- Tener **capturas y reportes pre-generados** (coverage HTML, `reporte.html` de
  Locust, run verde de GitHub Actions) para mostrar sin ejecutar.
- Un video corto de respaldo de la suite corriendo.

## 6.5 Reparto de la demo

| Momento | Quién | Qué dice |
|---|---|---|
| Intro (30s) | WS-A | Contexto y qué se va a mostrar |
| Ejecución (2–3 min) | WS-C/E | Corre la suite / pipeline |
| Lectura de resultados | WS-E | Interpreta métricas |

## Entregable (DoD)

- [x] Opción de demo elegida (**A + B**: suite pytest en vivo + CI/CD, con e2e/Vitest de refuerzo)
- [ ] Guión ensayado al menos 1 vez completo _(pendiente: ensayo con proyector)_
- [x] Plan B con evidencias pre-generadas listo (coverage HTML + reporte Locust; falta el video de respaldo)
- [ ] Reparto de roles en la demo definido _(ver 6.5; confirmar con el equipo)_

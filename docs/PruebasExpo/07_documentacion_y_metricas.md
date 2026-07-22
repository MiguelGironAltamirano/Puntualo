# 7. Documentación y métricas de calidad

> **Responsable (WS-E):** Sevan · **Estado:** ⬜
> Plan de pruebas, matriz de casos, reportes de defectos y **métricas de calidad
> interpretadas** para la toma de decisiones.

## 7.1 Inventario documental (dónde está cada cosa)

| Documento | Ubicación |
|---|---|
| Plan de pruebas | [02_plan_y_estrategia.md](02_plan_y_estrategia.md) |
| Matriz de casos | [03_diseno_de_casos.md](03_diseno_de_casos.md) |
| Inventario/checklist técnico | [PRUEBAS.md](PRUEBAS.md) |
| Reportes de defectos | [05 §5.2](05_riesgos_defectos_seguridad.md) |
| Evidencia de rendimiento (carga) | `apps/tests/load-test/ANALISIS.md` + `results/reporte.html` |
| Evidencia de rendimiento (estrés) | `apps/tests/stress-test/locustfile.py` (etapas 50→100→200→400, listo para correr) |
| Evidencia de aceptación (e2e) | `apps/tests/e2e/specs/auth.spec.ts` (Playwright, 3 casos verdes) |
| Evidencia de componentes frontend | `apps/frontend/src/**/*.test.tsx` (Vitest, 8 casos verdes) |
| Evidencia de control de acceso | `apps/backend/tests/integration/test_access_control.py` (401/403, 3 casos verdes) |
| Evidencia de usabilidad | `docs/superpowers/ux/resultados_pruebas_usabilidad.md` |
| Coverage / JUnit | `reports/` (generado por la suite — [04](04_automatizacion_y_cicd.md)) |

## 7.2 Métricas de calidad (definir + interpretar)

| Métrica | Fuente | Valor actual | Interpretación / decisión |
|---|---|---|---|
| Cobertura de líneas | pytest-cov | **51% global** (medido 2026-07-15) | Módulos críticos ya sobre umbral: `core/security` 100%, `auth/router` 88%, `auth/schemas` 90%, `utils/rate_limiter` 94%, `utils/moderation` 70%. Por debajo: `auth/service` 47%, `report_service` 31%, `professors/service` 26% → siguientes casos a priorizar |
| N.º de pruebas / tasa de éxito | JUnit | **96 passed · 29 skipped · 0 failed** (2026-07-15) | 100% verde de lo ejecutado; los `skipped` son esqueletos aún sin implementar. Meta: reducir skips e ir a 100% verde en CI |
| Densidad de defectos | Bitácora | 2 (Locust) | Concentrados en acceso a BD → optimizar pool |
| Latencia p95 (carga) | Locust | **1 400 ms** (cache caliente) | Aceptable; degradación en endpoints con BD |
| Throughput | Locust | **14.64 req/s** | Soporta 50 usuarios sin caída |
| Tasa de error bajo carga | Locust | **0%** (cache caliente) / 1% (frío) | Precalentar cache mitiga el riesgo |
| Casos e2e (aceptación) | Playwright | **3 / 3 verdes** | Login (render, inválido→error, válido→/teachers) con red interceptada; deterministas para CI |
| Casos de componente (frontend) | Vitest | **8 / 8 verdes** | `Pagination`, `ResultsInfo`, `useAuthStore` renderizan y responden a interacción |
| Satisfacción (SUS) | Usabilidad | **87.5 / 100** | "Excelente" (>68 = por encima del promedio) |
| Errores de usuario (usabilidad) | Pruebas UX | 1.0 promedio | Bajo; flujos claros |

> ✅ Cobertura y tasa de éxito medidas el 2026-07-15 (`pytest --cov=app`, 125 casos:
> 96 passed / 29 skipped / 0 failed). Reportes en `reports/` (`junit.xml`,
> `coverage.xml`, `coverage/index.html`). Excluido `test_report_service.py` (fixtures
> desalineadas, ver [04 §4.6](04_automatizacion_y_cicd.md)).

## 7.3 Interpretación para toma de decisiones (borrador)

- **Rendimiento:** el cuello de botella es la BD (pool de 14 conexiones).
  Decisión: subir workers Uvicorn y `DB_POOL_SIZE`, cachear listados pesados.
- **Fiabilidad:** los 500s solo aparecen en cache frío → precalentar cache al deploy.
- **Usabilidad:** SUS 87.5 valida los flujos del estudiante; no hay acción urgente.
- **Cobertura:** 51% global (medida). Los módulos de mayor riesgo ya están cubiertos
  (`core/security` 100%, `rate_limiter` 94%, `moderation` 70%, `auth/router` 88%).
  El déficit se concentra en servicios aún sin suite propia (`auth/service` 47%,
  `professors/service` 26%, `report_service` 31%) y en tareas Celery / validación de
  profesores (0–30%), que son trabajo futuro. Decisión: priorizar casos de
  `report_service` y `professors/service` en la próxima iteración.

## 7.4 Formato de reporte de defecto (plantilla)

```
ID: D-<n>
Título:
Severidad: Crítica / Alta / Media / Baja
Riesgo asociado: R#
Entorno:
Pasos para reproducir:
Resultado esperado:
Resultado obtenido:
Evidencia:
Estado: Abierto / En análisis / Corregido / Cerrado
```

### Ejemplo instanciado (hallazgo de la prueba de carga)

```
ID: D-1
Título: 500s intermitentes (~1%) en endpoints de BD con cache frío bajo carga
Severidad: Media
Riesgo asociado: R6 (saturación de BD bajo carga, pool de 14 conexiones)
Entorno: VM Oracle (puntualo.duckdns.org), 2 workers Uvicorn, Supabase pooler :6543
Pasos para reproducir:
  1. Reiniciar el backend (cache Redis vacío).
  2. Lanzar Locust con 50 usuarios / spawn 5 / 3 min sobre endpoints GET públicos.
  3. Observar errores en /courses, /evaluations y /professors/{id}/comments.
Resultado esperado: 100% de respuestas 200 en lecturas públicas.
Resultado obtenido: ~1.07% de HTTP 500 (24 de 2 238) en la 1ª corrida (cache frío);
  0% en la 2ª (cache caliente).
Evidencia: apps/tests/load-test/ANALISIS.md + results/reporte.html
Estado: Observado — mitigación propuesta (precalentar cache + ampliar pool/workers)
```

> Segundo defecto (D-2, degradación de latencia por pool de 14 conexiones) documentado
> en la bitácora de [05 §5.2](05_riesgos_defectos_seguridad.md).

## Entregable (DoD)

- [x] Tabla de métricas completa con valores reales (cobertura, tasa de éxito, e2e, componentes medidos 2026-07-15)
- [x] Interpretación escrita por métrica (no solo el número) — §7.2 y §7.3
- [x] Reportes de defectos en formato plantilla (D-1 instanciado en §7.4; D-2 en [05](05_riesgos_defectos_seguridad.md))
- [ ] 1–2 slides de métricas para la expo _(pendiente: armar las diapositivas)_

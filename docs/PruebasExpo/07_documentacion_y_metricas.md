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
| Evidencia de rendimiento | `apps/tests/load-test/ANALISIS.md` + `results/reporte.html` |
| Evidencia de usabilidad | `docs/superpowers/ux/resultados_pruebas_usabilidad.md` |
| Coverage / JUnit | `reports/` (generado por la suite — [04](04_automatizacion_y_cicd.md)) |

## 7.2 Métricas de calidad (definir + interpretar)

| Métrica | Fuente | Valor actual | Interpretación / decisión |
|---|---|---|---|
| Cobertura de líneas | pytest-cov | ⬜ (medir) | Si < 70% en módulos críticos → priorizar casos |
| N.º de pruebas / tasa de éxito | JUnit | 5 reales + esqueletos | Meta: 100% verde en CI |
| Densidad de defectos | Bitácora | 2 (Locust) | Concentrados en acceso a BD → optimizar pool |
| Latencia p95 (carga) | Locust | **1 400 ms** (cache caliente) | Aceptable; degradación en endpoints con BD |
| Throughput | Locust | **14.64 req/s** | Soporta 50 usuarios sin caída |
| Tasa de error bajo carga | Locust | **0%** (cache caliente) / 1% (frío) | Precalentar cache mitiga el riesgo |
| Satisfacción (SUS) | Usabilidad | **87.5 / 100** | "Excelente" (>68 = por encima del promedio) |
| Errores de usuario (usabilidad) | Pruebas UX | 1.0 promedio | Bajo; flujos claros |

> ⬜ **TODO:** completar cobertura y tasa de éxito tras ejecutar la suite ([04](04_automatizacion_y_cicd.md)).

## 7.3 Interpretación para toma de decisiones (borrador)

- **Rendimiento:** el cuello de botella es la BD (pool de 14 conexiones).
  Decisión: subir workers Uvicorn y `DB_POOL_SIZE`, cachear listados pesados.
- **Fiabilidad:** los 500s solo aparecen en cache frío → precalentar cache al deploy.
- **Usabilidad:** SUS 87.5 valida los flujos del estudiante; no hay acción urgente.
- **Cobertura:** (pendiente medir) guiará dónde invertir más casos.

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

## Entregable (DoD)

- [ ] Tabla de métricas completa con valores reales
- [ ] Interpretación escrita por métrica (no solo el número)
- [ ] Reportes de defectos en formato plantilla
- [ ] 1–2 slides de métricas para la expo

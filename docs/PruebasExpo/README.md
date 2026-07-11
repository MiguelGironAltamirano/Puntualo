# Exposición de Pruebas — Puntualo · Carpeta maestra

Este directorio contiene **toda la documentación de la exposición de pruebas**.
Está dividido en un archivo por cada ítem de la rúbrica para poder **repartir el
trabajo y verificar el avance** de forma independiente.

> Convención de estado en todos los documentos:
> ✅ listo · 🟡 en progreso · ⬜ pendiente · 🔴 bloqueado

---

## Índice de documentos

| Ítem rúbrica | Documento | Responsable | Estado |
|---|---|---|---|
| 1. Sistema y alcance | [01_sistema_y_alcance.md](01_sistema_y_alcance.md) | Cicilis | ⬜ |
| 2. Plan y estrategia | [02_plan_y_estrategia.md](02_plan_y_estrategia.md) | Cicilis | 🟡 |
| 3. Diseño de casos | [03_diseno_de_casos.md](03_diseno_de_casos.md) | Tarqui | ⬜ |
| 4. Automatización y CI/CD | [04_automatizacion_y_cicd.md](04_automatizacion_y_cicd.md) | Miguel (CI) · Sevan (carga/e2e) · Tarqui/Mathias (tests) | 🟡 |
| 5. Riesgos, defectos y seguridad | [05_riesgos_defectos_seguridad.md](05_riesgos_defectos_seguridad.md) | Mathias | 🟡 |
| 6. Demo en vivo | [06_demo_en_vivo.md](06_demo_en_vivo.md) | Sevan | ⬜ |
| 7. Documentación y métricas | [07_documentacion_y_metricas.md](07_documentacion_y_metricas.md) | Sevan | ⬜ |
| 8. Conclusiones y mejoras | [08_conclusiones_y_mejoras.md](08_conclusiones_y_mejoras.md) | Cicilis | ⬜ |
| Soporte técnico | [PRUEBAS.md](PRUEBAS.md) — inventario y checklist de pruebas | Tarqui (unit) · Mathias (API) | 🟡 |

---

## Organización del equipo (work-streams)

El trabajo se agrupa en **5 flujos**. Si el equipo es más chico, se fusionan
(ver nota al final). Cada flujo tiene un responsable único (accountable).

| WS | Flujo | Ítems que cubre | Entregables clave | Responsable |
|---|---|---|---|---|
| **A** | Estrategia y Documentación | 1, 2, 8 | Presentación del sistema, plan ISTQB/29119, conclusiones | **Cicilis** |
| **B** | Diseño de Casos | 3 | Matriz de casos con técnicas y entradas/salidas | **Tarqui** |
| **C** | Automatización y CI/CD | 4 | Suite ejecutable, coverage/JUnit, workflow GitHub Actions | **Miguel** (CI + auth/humo) + Tarqui/Mathias (tests) |
| **D** | Riesgos y Seguridad | 5 | Matriz de riesgos, bitácora de defectos, OWASP/DevSecOps | **Mathias** |
| **E** | Carga, e2e, Demo y Métricas | 4 (carga/e2e), 6, 7 | Prueba de carga, e2e, guión de demo, métricas | **Sevan** |

### RACI resumido

| Actividad | A | B | C | D | E |
|---|---|---|---|---|---|
| Plan y estrategia | **R** | C | C | C | I |
| Diseño de casos | C | **R** | C | C | I |
| Implementar/ejecutar suite | I | C | **R** | C | C |
| Pipeline CI/CD | I | I | **R** | C | I |
| Riesgos y seguridad | C | C | C | **R** | I |
| Demo en vivo | C | I | C | I | **R** |
| Métricas de calidad | C | I | C | C | **R** |
| Conclusiones | **R** | I | I | C | C |

_R = Responsable/hace · C = Consultado · I = Informado_

### Asignación por integrante y cómo verificar su avance

| Integrante | Perfil / base | Entregables concretos | Cómo verificar que está hecho (criterio objetivo) |
|---|---|---|---|
| **Miguel** | Coordinación · módulo de autenticación | `.github/workflows/ci.yml` (pipeline) + tests de auth (`unit/test_security.py`, `integration/test_auth_api.py`) + humo (`smoke/test_smoke.py`) | En GitHub → pestaña **Actions**: workflow **verde**; `pytest apps/backend/tests/unit/test_security.py apps/backend/tests/integration/test_auth_api.py apps/backend/tests/smoke -v` **verde** |
| **Tarqui** | Hizo las pruebas unitarias; backend comparador de profesores | Ítem 3 ([03](03_diseno_de_casos.md)) + mantener sus unitarias + implementar `integration/test_comments_flow.py` | DoD del [03](03_diseno_de_casos.md) marcado; `pytest apps/backend/tests/unit -v` **verde**; `test_comments_flow` **verde** |
| **Mathias** | Chatbot + backend de profesores (filtros) | Ítem 5 ([05](05_riesgos_defectos_seguridad.md)), foco OWASP LLM del chatbot; `integration/test_access_control.py`, `test_professors_api.py` y `test_catalogs_courses_api.py` | DoD del [05](05_riesgos_defectos_seguridad.md) marcado; esos tests **verdes**; escaneos ejecutados con evidencia en `reports/` |
| **Cicilis** | Nuevo (rol documental) | Ítems 1, 2, 8 ([01](01_sistema_y_alcance.md), [02](02_plan_y_estrategia.md), [08](08_conclusiones_y_mejoras.md)) | DoD de esos 3 documentos marcado; **sin `TODO` pendientes** |
| **Sevan** | Nuevo | Prueba de **carga** (re-ejecutar Locust) + **e2e** (Playwright + `auth.spec.ts`) + Ítem 6 ([06](06_demo_en_vivo.md)) + Ítem 7 métricas ([07](07_documentacion_y_metricas.md)) | `results/reporte.html` con fecha nueva; `npx playwright test` con ≥1 caso **verde**; guión del [06](06_demo_en_vivo.md) ensayado; [07](07_documentacion_y_metricas.md) con métricas reales |

> **Regla de verificación general:** cada integrante marca el bloque "Entregable (DoD)"
> al final de su documento. Un ítem se considera cerrado cuando **su DoD está 100%
> marcado** y (si aplica) **su prueba corre verde**. El tablero de arriba refleja el estado.

---

## Tablero de avance (Definition of Done por ítem)

### Ítem 1 — Sistema y alcance
- [ ] Nombre, objetivo, usuarios y funcionalidades descritos
- [ ] Evolución respecto a la actividad integradora (semana 7)
- [ ] Diagrama de contexto/arquitectura

### Ítem 2 — Plan y estrategia
- [ ] Contexto de negocio y objetivos de calidad (ISO 25010)
- [ ] Niveles y tipos priorizados con justificación
- [ ] Mapeo a ISTQB
- [ ] Plan formal ISO/IEC 29119 (alcance, criterios entrada/salida, entorno)

### Ítem 3 — Diseño de casos
- [ ] Casos de caja negra (partición, valores límite, tabla de decisión, estados)
- [ ] Casos de caja blanca (cobertura de sentencias/ramas)
- [ ] Casos basados en riesgo (trazados a la matriz de riesgos)
- [ ] Cada caso con ID, precondición, entradas y resultado esperado

### Ítem 4 — Automatización y CI/CD
- [ ] Suite unit/integración implementada y ejecutada (pytest)
- [ ] Reporte coverage + JUnit archivado
- [ ] Prueba de rendimiento con evidencia (Locust)
- [ ] Workflow GitHub Actions verde (test + security)

### Ítem 5 — Riesgos, defectos y seguridad
- [ ] Matriz de riesgos (probabilidad × impacto)
- [ ] Bitácora de defectos (incluye hallazgos de Locust)
- [ ] Mapeo OWASP Top 10 + LLM Top 10
- [ ] Escaneos ejecutados (pip-audit, pnpm audit, gitleaks, bandit) con evidencia

### Ítem 6 — Demo en vivo
- [ ] Guión paso a paso de la demo
- [ ] Entorno de demo preparado y probado (ensayo)
- [ ] Plan B si algo falla en vivo

### Ítem 7 — Documentación y métricas
- [ ] Plan de pruebas consolidado
- [ ] Matriz de casos (enlace al 03)
- [ ] Reportes de defectos
- [ ] Métricas (cobertura, tasa de éxito, densidad de defectos, p95, SUS) **interpretadas**

### Ítem 8 — Conclusiones y mejoras
- [ ] Cómo la estrategia mejora la calidad
- [ ] Riesgos de negocio reducidos (antes/después)
- [ ] Mejoras propuestas / trabajo futuro

---

## Decisiones de alcance ya tomadas

| Tema | Decisión |
|---|---|
| Nivel de evidencia | **Implementar y ejecutar (máx.)** — suite real + coverage/JUnit + CI |
| Seguridad | **Documentar + herramientas ligeras** (pip-audit, pnpm audit, gitleaks, bandit) |
| CI/CD | **GitHub Actions** |
| Casos formales | En [03_diseno_de_casos.md](03_diseno_de_casos.md) (antes se planeó en PRUEBAS.md) |

## Cronograma sugerido (rellenar fechas)

| Fase | Contenido | Flujos | Fecha límite |
|---|---|---|---|
| F1. Diseño | Ítems 1, 2, 3 + matriz de riesgos | A, B, D | _(fecha)_ |
| F2. Construcción | Implementar suite + CI (ítem 4) | C | _(fecha)_ |
| F3. Seguridad | Escaneos + OWASP (ítem 5) | D | _(fecha)_ |
| F4. Métricas y demo | Ítems 6, 7 | C, E | _(fecha)_ |
| F5. Cierre y ensayo | Ítem 8 + ensayo general | Todos | _(fecha)_ |

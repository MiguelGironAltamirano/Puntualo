# 2. Plan y estrategia de pruebas

> **Responsable (WS-A):** Cicilis · **Estado:** 🟡
> Alineado a **ISTQB** e **ISO/IEC 29119**, con justificación según el contexto de
> negocio de Puntualo. El inventario y priorización detallada vive en
> [PRUEBAS.md](PRUEBAS.md); aquí está el marco estratégico.

## 2.1 Contexto de negocio → estrategia

Puntualo publica **contenido sobre personas reales**. Esto define las prioridades:

| Riesgo de negocio | Consecuencia | Prioridad de prueba derivada |
|---|---|---|
| Comentario difamatorio/falso | Legal, reputacional | **Moderación + reportes** (Must) |
| Spam / abuso de reportes | Pérdida de confianza | Rate limiting + abuso (Must) |
| Cuentas comprometidas | Suplantación | Auth + control de acceso (Must) |
| IA (chatbot) manipulada | Info errónea / costos | Pruebas LLM (Should) |
| Caída bajo carga (matrícula) | Indisponibilidad | Rendimiento (Must) |

## 2.2 Objetivos de calidad (ISO/IEC 25010)

| Característica | Aplicación en Puntualo | Cómo se prueba |
|---|---|---|
| Adecuación funcional | Evaluar, moderar, reportar | Unit + integración |
| Fiabilidad | Escalamiento correcto de reportes | Integración |
| Seguridad | Auth, control de acceso, IA | Seguridad (ítem 5) |
| Eficiencia de desempeño | Latencia bajo carga | Rendimiento (Locust) |
| Usabilidad | Flujos del estudiante | Pruebas de usabilidad (SUS 87.5) |
| Mantenibilidad | Regresión ante cambios | Suite en CI |

> Evidencia de usabilidad existente:
> `docs/superpowers/ux/resultados_pruebas_usabilidad.md` (SUS promedio 87.5).

## 2.3 Alineación ISTQB

### Proceso de prueba (mapeo)
| Fase ISTQB | En este proyecto |
|---|---|
| Planificación | Este documento + [README.md](README.md) |
| Monitoreo y control | Tablero de avance (README) + CI |
| Análisis | Riesgos ([05](05_riesgos_defectos_seguridad.md)) |
| Diseño | Matriz de casos ([03](03_diseno_de_casos.md)) |
| Implementación | Suite pytest/Locust ([04](04_automatizacion_y_cicd.md)) |
| Ejecución | CI + demo ([06](06_demo_en_vivo.md)) |
| Cierre | Conclusiones ([08](08_conclusiones_y_mejoras.md)) |

### Niveles de prueba
Componente (Unitaria) · Integración · Sistema · Aceptación.

### Tipos de prueba
Funcional · No Funcional (Rendimiento, Seguridad, Usabilidad) · Estructural (caja
blanca) · de Cambios (Regresión, Humo).

### Principios ISTQB que citaremos
- "Las pruebas muestran presencia, no ausencia de defectos."
- "Las pruebas exhaustivas son imposibles" → **priorización basada en riesgo**.
- "Agrupamiento de defectos" → foco en moderación/reportes/auth.
- "Paradoja del pesticida" → **regresión** en CI.

## 2.4 Niveles y tipos priorizados (resumen MoSCoW)

El detalle completo y la ubicación de cada archivo está en [PRUEBAS.md](PRUEBAS.md).
Resumen:

- **Must:** moderación, rate limiter, abuso, servicio de reportes, carga 50 usuarios,
  auth+JWT, control de acceso, flujo de comentarios, humo.
- **Should:** endpoints profesores/cursos/catálogos, scoring, moderación con DB, regresión en CI.
- **Could:** cache Redis, hashtags, paginación util, e2e frontend, componentes, usabilidad.
- **Won't (ahora):** estrés, pentest/DAST.

## 2.5 Plan formal (ISO/IEC 29119)

### Alcance
Ver [01 §1.5](01_sistema_y_alcance.md).

### Enfoque por nivel
| Nivel | Herramienta | Entorno |
|---|---|---|
| Unitaria | pytest | Local, sin infra |
| Integración | pytest + SQLite en memoria | Local |
| Sistema (carga) | Locust | VM Oracle (despliegue real) |
| Aceptación (e2e) | Playwright/Cypress _(por instalar)_ | Local/preview |

### Criterios de entrada
- Código compila y la app arranca.
- Fixtures y datos de prueba disponibles.

### Criterios de salida (propuesta — ajustar %)
- Cobertura de líneas **≥ 70%** en módulos críticos (moderación, reportes, auth).
- **0 defectos críticos** abiertos.
- Suite **verde en CI**.
- Escaneos de seguridad sin hallazgos críticos.

### Criterios de suspensión / reanudación
- Suspender si la app no levanta o un fixture base falla.
- Reanudar tras corregir el bloqueante.

### Entregables
Plan (este doc), matriz de casos ([03](03_diseno_de_casos.md)), suite ([04](04_automatizacion_y_cicd.md)),
reportes de defectos y métricas ([07](07_documentacion_y_metricas.md)).

### Entorno de prueba
SQLite en memoria (unit/integración), Redis mockeado o fakeredis, VM Oracle +
Supabase (carga).

## Entregable (DoD)

- [ ] §2.2 objetivos de calidad cerrados
- [ ] §2.3 tablas ISTQB completas
- [ ] §2.5 criterios de salida con % acordados por el equipo
- [ ] 1–2 slides de estrategia

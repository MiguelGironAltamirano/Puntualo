# Diseño — Investigación de fuentes gratuitas para validación de profesores

**Fecha:** 2026-05-11
**Autor:** Mathias Torres (brainstorming con Claude Code)
**Estado:** aprobado para ejecución
**Sustituye / antecede a:** futura redacción de `PLAN_TAREA_2_4_v2.md`

---

## 1. Objetivo y alcance

Este documento es el **meta-diseño** de un informe de investigación. El informe que de aquí se produzca debe responder a:

> ¿Qué fuentes gratuitas existen para validar y enriquecer profesores UNMSM, y cómo combinarlas en un pipeline de validación?

### El informe NO es

- Código de producción.
- Una migración de base de datos.
- Una decisión final sobre reemplazar el `SuneduService` planeado en `PLAN_TAREA_2_4.md`. El informe **propone** ese cambio si la evidencia lo respalda, pero la decisión queda en el equipo.

### El informe SÍ es

- Base para redactar `PLAN_TAREA_2_4_v2.md` reemplazando el plan actual.
- Un smoke test con 3 profesores reales de FISI contra cada fuente, para validar afirmaciones del informe.
- Una guía arquitectónica que aterriza el "Enfoque 2 — Pipeline jerárquico con enriquecimiento" en componentes concretos del repo (`app/services/`, `app/tasks/`, `app/utils/`).

### Audiencia

Equipo Puntualo (Miguel, Ángel, Mathias, Nicolas). Asume conocimiento del stack pero no de las fuentes peruanas de datos académicos.

### Ubicación final

- Este meta-diseño: `docs/superpowers/specs/2026-05-11-professor-validation-research-design.md`.
- El informe producto: `docs/research/2026-05-11-professor-validation-sources.md`.

### Decisiones previas tomadas durante el brainstorming

| # | Pregunta | Decisión |
|---|---|---|
| 1 | Relación con `PLAN_TAREA_2_4.md` | Investigar primero, decidir arquitectura después. |
| 2 | ¿Qué significa "validated"? | Existencia + afiliación UNMSM + enriquecimiento (para futuro resumen IA). |
| 3 | ¿Qué significa "gratuito"? | Cero costo para validación core; free tiers OK siempre que se respete el límite (ej. Tavily 1000/mes nunca rebasado). |
| 4 | ¿Scraping? | Sí, con etiqueta: robots.txt, rate limit, User-Agent identificable, caché agresiva. |
| 5 | ¿Smoke test? | Sí, contra 3 profesores reales (mix high/medium/low profile). |
| 6 | Arquitectura tentativa | Enfoque 2: pipeline jerárquico con enriquecimiento. |
| 7 | Fuente extra a evaluar | Colegio de Profesores del Perú (CPPe) — el informe juzgará si aplica a docentes universitarios. |
| 8 | Facultad prioritaria | FISI. |

---

## 2. Fuentes en alcance

### Validación de afiliación UNMSM (núcleo)

1. **Directorio docente UNMSM** — portales por facultad (`unmsm.edu.pe`, subdominios). Fuente más autoritativa para "enseña en UNMSM hoy". Acceso: scraping HTML.
2. **SUNEDU — Consulta de Docentes Universitarios** — registro oficial del regulador. Cobertura nacional con filtro por universidad. Acceso: scraping.
3. **RENACYT (CONCYTEC)** — investigadores formales en Perú. Cobertura parcial (no todos los docentes son investigadores registrados) con datos estructurados.

### Enriquecimiento

4. **ORCID Public API** — gratuita, sin cuotas duras, opt-in del investigador.
5. **OpenAlex API** — grafo académico abierto, gratuito, incluye affiliations.
6. **Semantic Scholar API** — gratuita con rate limit.
7. **Google Scholar** — solo para evaluar viabilidad; ToS restrictivo, scraping arriesgado.

### Fallback web general

8. **Tavily Search + Extract** — para casos donde ninguna fuente estructurada cubre al profesor. Usado con presupuesto estricto.

### A evaluar con escepticismo

9. **Colegio de Profesores del Perú (CPPe — cppe.org.pe)** — tradicionalmente para docentes de educación básica regular. El informe evaluará si cubre docentes universitarios; si no, se descarta justificadamente.

### Fuera de alcance explícito

- LinkedIn (ToS prohíbe scraping automatizado, no es fuente confiable de afiliación universitaria peruana).
- Wikipedia/Wikidata (cobertura demasiado escasa para profesores UNMSM no famosos).
- DBLP (solo CS).
- APIs de pago (Scopus, Web of Science).

---

## 3. Framework de evaluación por fuente

El informe evaluará cada fuente con esta plantilla idéntica para comparación lado a lado:

| Dimensión | Qué se mide |
|---|---|
| **Cobertura UNMSM** | ¿Lista profesores UNMSM? ¿Aprox cuántos? ¿Cubre FISI? Rating: Alta / Media / Baja / Nula. |
| **Tipo de afiliación** | ¿Marca explícitamente "UNMSM" como empleador actual, o solo se infiere de publicaciones pasadas? |
| **Campos disponibles** | Lista de fields que devuelve: nombre, DNI/ID, facultad, departamento, fecha alta/baja, foto, ORCID, publicaciones, líneas de investigación. |
| **Modo de acceso** | API REST / GraphQL / scraping HTML / dataset descargable. Si scraping: estabilidad estimada del DOM. |
| **Costo y cuota** | Free / free tier (límites) / pago. Para free tier: requests/día/mes y rate limit. |
| **ToS y robots.txt** | ¿Permite acceso automatizado? Citas literales a la cláusula relevante. |
| **Match quality** | ¿Búsqueda por nombre completo? ¿Tolera tildes/abreviaturas? Riesgo de homónimos. |
| **Freshness** | ¿Cuándo se actualiza? ¿Refleja profesores que entraron este semestre? |
| **Rol en el pipeline** | Validación / Enriquecimiento / Ambos / Descartar. |
| **Veredicto smoke test** | Resultado real al consultar los 3 profesores FISI de prueba. |
| **Riesgo principal** | El problema más probable al depender de esta fuente. |

Al final del informe hay una **tabla resumen** con todas las fuentes en filas y estas dimensiones en columnas, más una columna "Recomendación" (tier 1 / tier 2 / descartar).

---

## 4. Metodología del smoke test

### Selección de los 3 profesores FISI

Se cubre el rango de "facilidad de encontrar" para detectar sesgos:

- **1 high-profile** — alguien con publicaciones, posiblemente decano o jefe de departamento. Si una fuente NO lo encuentra, esa fuente tiene un problema serio.
- **1 medio** — docente ordinario con cierta actividad académica.
- **1 low-profile** — docente con poca presencia digital (auxiliar, contratado reciente). Si una fuente lo encuentra, demuestra cobertura amplia real.

### Cómo conseguir los nombres

Extraerlos del **directorio público de FISI** (`https://sistemas.unmsm.edu.pe/`) durante la ejecución del informe, eligiendo a ojo según el perfil arriba. Como toda la info publicada está en webs institucionales públicas, no hay tema de privacidad — son exactamente los datos que Puntualo desplegará.

### Para cada par `(fuente, profesor)` se registra

- ¿Encontrado? (Sí / No / Match dudoso)
- Campos devueltos (lista literal)
- Tiempo de respuesta aproximado
- URL/endpoint usado
- Si hay match dudoso o homónimo: cuántos candidatos devuelve y cómo se discrimina
- Errores (HTTP, parse, ToS warnings)

### Presupuesto de cuotas durante el smoke test

- Tavily: máximo 3 profesores × 3 calls = **9 calls de 1000/mes**. Ínfimo.
- ORCID / OpenAlex / Semantic Scholar: sin cuota dura, rate limit conservador (1 req/s).
- Scraping UNMSM/SUNEDU/CPPe/RENACYT: 1 req/s, User-Agent identificable, respetar robots.txt.

### Criterio para "pasa el smoke test"

Una fuente "pasa" si encuentra al high-profile y al medio sin falsos positivos. Encontrar al low-profile es bonus. No encontrar al high-profile es descarte automático como tier 1.

---

## 5. Arquitectura propuesta (Enfoque 2 — pipeline jerárquico)

### Componentes

```
ProfessorValidationPipeline
├── sources: ordered list of ProfessorSource
└── budget: BudgetTracker (Redis-backed monthly counters)
```

**`ProfessorSource`** — interfaz abstracta que implementa cada fuente:

```python
class ProfessorSource(Protocol):
    name: str                        # "unmsm_directory", "sunedu", ...
    role: Literal["validation", "enrichment", "both"]
    priority: int                    # orden en el pipeline
    cost_per_call: int               # 0 para fuentes libres, 1 para Tavily

    async def validate(full_name: str, university: str) -> ValidationResult
    async def enrich(full_name: str, hints: dict) -> EnrichmentResult
```

**Resultados:**

```python
ValidationResult = { found: bool, affiliation_confirmed: bool, evidence: dict, source: str }
EnrichmentResult = { fields: dict[str, FieldWithProvenance], source: str }
FieldWithProvenance = { value: Any, source: str, fetched_at: datetime, confidence: float }
```

Cada campo enriquecido **mantiene la fuente** (procedencia). Esto es clave para el futuro resumen IA: si OpenAlex y UNMSM discrepan en "departamento", el modelo sabe en cuál confiar más por la procedencia.

### Sources concretos (orden tentativo, ajustable según hallazgos del informe)

1. `UnmsmDirectorySource` — validation + enrichment. Scraping. Más autoritativo.
2. `SuneduSource` — validation. Scraping. Confirma afiliación oficial.
3. `RenacytSource` — validation + enrichment. Estructurado.
4. `OrcidSource` — enrichment. API gratuita.
5. `OpenAlexSource` — enrichment. API gratuita.
6. `SemanticScholarSource` — enrichment. API con rate limit.
7. `TavilySource` — enrichment fallback. Bajo presupuesto.

### Data flow (al crear un profesor)

1. `POST /professors` → `ProfessorService.create()` commitea con `validation_status = "pending_validation"`.
2. Encola `validate_professor.delay(prof_id, full_name)` (no bloqueante).
3. Worker Celery toma la task → `ProfessorValidationPipeline.run(prof)`.
4. **Fase validación:** itera sources con `role ∈ {validation, both}` en orden de prioridad. Para apenas alguno retorne `affiliation_confirmed=True`.
   - Si ninguno confirma: `validation_status = "not_found"`. Pipeline termina.
   - Si alguno confirma: `validation_status = "validated"`, sigue.
5. **Fase enriquecimiento:** itera **todos** los sources restantes con `role ∈ {enrichment, both}`. Cada uno aporta campos. Pipeline merguea con provenance.
6. Persiste `Professor` actualizado + `ProfessorEvidence[]` (nueva tabla, una fila por (professor, source, raw_payload, fetched_at)).

### Mapeo al repo

- `app/services/professor_validation/` (nuevo)
  - `pipeline.py`
  - `sources/base.py`
  - `sources/{unmsm,sunedu,renacyt,orcid,openalex,semantic_scholar,tavily}.py`
  - `budget.py`
- `app/tasks/professor_validation_tasks.py` (reemplaza al planeado `sunedu_tasks.py`)
- `app/models/professor_evidence.py` (nuevo modelo)
- Migración Alembic para `professor_evidence`

---

## 6. Cross-cutting concerns

### Cache (Redis)

- **Clave:** `validation:{source}:{md5(full_name.lower().strip())}`
- **TTL validación:** 24h.
- **TTL enriquecimiento:** 7 días.
- **Invalidación manual:** endpoint admin `POST /professors/{id}/revalidate` que limpia las claves de ese profesor y reencola.

### Circuit breaker (por fuente, no global)

Reutiliza el patrón del `PLAN_TAREA_2_4.md` existente, una instancia por source:

- Clave failures: `circuit:{source}:failures`
- Clave open: `circuit:{source}:open`
- Threshold: 5 fallos consecutivos → abre 5 min.
- Source con circuito abierto se **salta** (no falla el pipeline). El pipeline continúa con la siguiente.

### Presupuesto Tavily (nunca rebasar el límite)

- **Contador mensual:** `tavily:budget:{YYYY-MM}` con TTL hasta fin de mes.
- **Hard cap:** 950 (margen de 50 bajo el límite oficial de 1000 — protege ante race conditions del INCR).
- **Soft warning:** al 80% (760) → log `WARNING`.
- **Al 100% (950):** `TavilySource` lanza `BudgetExhausted`, pipeline lo salta. Como Tavily no es source de validación core, la validación principal no se afecta.
- **Contador separado dev/smoke:** `tavily:budget:dev:{YYYY-MM}` con cap bajo (50). Evita que pruebas locales consuman el budget productivo.
- **Operación atómica:** `INCR` + comparación dentro del cliente Tavily; si supera el cap, decrementa y aborta. Garantiza no gastar 1 call de más.

### Errores y políticas

| Error | Acción |
|---|---|
| HTTP timeout / connection error | Retry con backoff (3 intentos) dentro del source. Si persiste: failure en circuit breaker, retorna `unavailable`. |
| HTTP 4xx (rate limit, auth) | No retry. Log `ERROR`. Registra failure. |
| HTTP 5xx | Retry. Si persiste: registra failure. |
| Parse error (HTML cambió) | Log `ERROR` con snippet HTML, registra failure. **Alerta crítica** — indica deuda de mantenimiento. |
| Ningún source confirma afiliación | `validation_status = "not_found"`. Profesor visible pero marcado "no validado". |
| Pipeline crash entre fases | Celery retry de la task completa (2 retries con countdown 60s). |

### Rate limiting

- Scrapers (UNMSM, SUNEDU, CPPe, RENACYT): **1 req/s por source**, semáforo en Redis.
- APIs (ORCID, OpenAlex, Semantic Scholar): respetar el rate limit propio (10/s típico).
- Tavily: el budget es el cuello de botella, no el rate.

### Logging

Cada llamada a un source emite un log estructurado: `{event, source, professor_id, found, latency_ms, cache_hit, error}`. Sistema listo para observabilidad futura sin acoplarlo a Prometheus ahora.

---

## 7. Testing strategy (recomendación del informe)

- **Unit por source:** mockear `httpx` con `respx`. Casos: encontrado, no-encontrado, timeout, parse error, ToS-deny. ~6-8 tests por source.
- **Pipeline orchestration:** mockear todos los sources. Casos: primer source confirma (corta cadena), ningún source confirma, enrichment con providers caídos parcialmente, todos caídos.
- **BudgetTracker:** INCR atómico, hard cap exacto, no decrementa en fallos legítimos, contador separado dev/prod.
- **Circuit breaker:** abre al threshold, bloquea durante window, resetea, no contamina otros sources.
- **Smoke tests reales:** suite aparte (`tests/smoke/`) con `@pytest.mark.smoke`, no corre en CI por defecto, requiere `RUN_SMOKE=1`. Se corre manualmente al cambiar un scraper o sospechar drift.

---

## 8. Estructura final del informe

`docs/research/2026-05-11-professor-validation-sources.md`:

1. **TL;DR** — 1 párrafo con la recomendación de pipeline ordenado.
2. **Contexto y objetivo** — qué se validó y por qué.
3. **Fuentes investigadas** — una subsección por source con la tabla del framework (sección 3).
4. **Smoke test results** — tabla `3 profesores × N sources` con ✅/❌/⚠️ + hallazgos cualitativos.
5. **Pipeline recomendado** — Enfoque 2 con el orden de sources ajustado a la evidencia del smoke test.
6. **Riesgos y mitigaciones** — drift de HTML, dependencia de portales caídos, homónimos, ToS changes.
7. **Próximos pasos** — handoff a `PLAN_TAREA_2_4_v2.md`.
8. **Apéndice** — payloads crudos del smoke test, queries Tavily usadas, conteo de cuotas consumidas.

---

## 9. Fuera de alcance del informe

- Implementar la pipeline (queda para el plan de implementación posterior).
- UI/UX de cómo se muestra al usuario el `validation_status`.
- Endpoint admin de revalidación (mencionado pero no especificado).
- Extensión a otras universidades — el informe deja la arquitectura preparada (parámetro `university` en sources) pero no investiga fuentes para UNI, PUCP, etc.
- Migración masiva de profesores existentes en DB (todos hoy en `pending_validation`).
- Decisión sobre roles/permisos para `validation_status` (mencionado en plan 2.3 como pendiente).

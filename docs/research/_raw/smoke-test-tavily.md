# Smoke test — Tavily Search + Extract

**Fecha:** 2026-05-11
**Modo de acceso:** API REST (`api.tavily.com/search`, `api.tavily.com/extract`), JSON.
**Auth:** API key (configurada en `apps/backend/.env`).
**Free tier:** 1000 calls/mes.
**Hard cap interno del informe:** 50 calls.
**Consumo a la fecha:** 13/50 (incluyendo el smoke test inicial de Task 2 y las búsquedas para localizar las fuentes de Tasks 7-13).
**ToS:** uso comercial permitido bajo el plan free tier.

## Test 1: Tavily Search por nombre

Query template: `{Nombre completo} UNMSM profesor`, `max_results=5`, `search_depth=basic`.

### Profesor 1 — Ciro Rodriguez Rodriguez

5 hits relevantes con score 1.00:
- `sciprofiles.com/profile/Ciro-Rodriguez` (perfil académico tipo Scopus author page)
- `sistemas.unmsm.edu.pe/posgrado/wp-content/uploads/2022/06/CV-CIRO-RODRIG...` (PDF CV UNMSM 2022 — más reciente que el del directorio principal)
- **`peru.misprofesores.com/profesores/Ciro-Rodriguez-Rodriguez_17290`** ← **MisProfesores Perú, competidor directo de Puntualo**
- `unmsm.academia.edu/CIRORODRIGUEZRODRIGUEZ` (Academia.edu)
- `scholar.google.com/citations?user=mcbgk1wAAAAJ&hl=es` (Google Scholar — Scholar ID visible)

### Profesor 2 — Lenis Wong Portillo

5 hits:
- `peru.misprofesores.com/profesores/Leniss-Wong-Portillo_16948` (con typo "Leniss" en URL pero el contenido apunta a la misma persona; MisProfesores acepta typos)
- `sistemas.unmsm.edu.pe/site/images/archivos/Lenis_Wong.pdf` (CV PDF)
- `sistemas.unmsm.edu.pe/site/home/directivos` — **¡aparece en relación de directivos FISI!** Información que el directorio docente no expone
- Facebook UNMSM (post sobre actividades académicas)
- YouTube (presentación en evento de FISI)

### Profesor 3 — Adegundo Camara Figueroa

5 hits:
- `sgd.unmsm.edu.pe/nosotros.html` (Sistema de Gestión Documental UNMSM, sección administrativa)
- `sistemas.unmsm.edu.pe/site/images/archivos/Mario_Camara.pdf` (CV PDF UNMSM)
- `studocu.com/pe/document/.../ejemplo-de-cv-tech-6-del-especialista...` (ejemplo de CV TECH-6, especialista informático)
- `core.ac.uk/download/pdf/323352429.pdf` (paper PDF en repo CORE)
- `sistemas.unmsm.edu.pe/site/docentes/directorio/directorio-dacc` (directorio)

## Test 2: Tavily Extract

Probadas 2 URLs:
- ❌ `sciprofiles.com/profile/Ciro-Rodriguez` → "Failed to fetch url" (Tavily no pudo acceder por bloqueo del sitio o CORS/rate). El call cuenta contra cuota igual.
- ✅ `peru.misprofesores.com/profesores/Ciro-Rodriguez-Rodriguez_17290` → 4195 chars de markdown estructurado.

### Datos extraídos de MisProfesores (Ciro)

```markdown
## Ciro Rodriguez Rodriguez
Universidad Nacional Mayor de San Marcos
Ciudad: Lima, Lima
Departamento/Facultad: FISI

Calidad General: 4.8
Lo Recomiendan: 33%
Nivel de Dificultad: 6.0

Etiquetas: MUCHAS TAREAS (7), DA BUENA RETROALIMENTACIÓN (2), BRINDA APOYO (1),
TOMARÍA SU CLASE OTRA VEZ (1), CALIFICA DURO (7), LOS EXÁMENES SON DIFÍCILES (4),
MUY CÓMICO (1), RESPETADO POR LOS ESTUDIANTES (2), INSPIRACIONAL (1), ...

12 Calificaciones de Estudiantes (con fecha hasta 06/Mar/2026, comentarios y calificaciones).
```

## Hallazgo colateral: existencia de competidor

`peru.misprofesores.com` es la versión peruana de la red MisProfesores (existe en otros países LATAM con dominios similares). Tiene:
- Reseñas de docentes UNMSM y otras universidades peruanas.
- Sistema de etiquetas similar al planeado para Puntualo.
- Comentarios fechados hasta Marzo 2026 (activo).
- Confirma de manera independiente afiliación FISI para Ciro y Lenis (info que **NO ESTÁ EN EL DIRECTORIO UNMSM**, que solo dice "DAISW/DACC" como departamento).

**Implicación competitiva:** Puntualo no está entrando en mercado vacío. La oportunidad debe diferenciarse vía mejor UX, integración con datos académicos enriquecidos, o resumen IA. La estrategia de "validar profesores con afiliación + enriquecimiento" es defendible si Puntualo lo hace mejor que MisProfesores (que parece tener datos manuales sin enriquecimiento estructurado).

## Análisis de costo Tavily en producción

Si Puntualo usa Tavily como fallback de enrichment (no validation), el costo por profesor varía:

- **Caso típico** (OpenAlex + UNMSM cubren todo): **0 calls Tavily**.
- **Caso fallback parcial** (foto o bio narrativa faltante): 1 search + 1 extract = **2 calls**.
- **Caso fallback completo** (perfil mínimo en otras fuentes): 1-2 search + 2-3 extract = **3-5 calls**.

**Cálculo de capacidad:**
- 1000 calls/mes.
- Asumiendo 30% de profesores requieren fallback Tavily (estimación conservadora), promedio 2 calls cada uno:
  → 0.3 × 2 = **0.6 calls/profesor en promedio**.
- → **~1666 profesores nuevos/mes** dentro del free tier.

UNMSM total ~3000 docentes; FISI ~80. Migración inicial cabe holgadamente. Crecimiento sostenible.

## Conclusión

- **Cobertura UNMSM (Tavily como source):** **Alta para enrichment** — encuentra perfiles, CVs PDFs, menciones en redes sociales, etc.
- **Cobertura para validation:** **No directa** — Tavily devuelve URLs, no afirmaciones estructuradas sobre afiliación. Requiere parsing del contenido.
- **Tipo de afiliación:** **inferida del contenido** de los resultados (cuando MisProfesores dice "UNMSM/FISI", es una pista pero no es una autoridad como SUNEDU sería).
- **Campos disponibles tras extract:** texto markdown semi-estructurado de cualquier URL accesible.
- **Rol en pipeline:** **Enrichment fallback (tier 4)**. Después de OpenAlex (tier 1), Directorio UNMSM (tier 1) y ORCID (tier 1 enrichment), Tavily completa huecos donde fallan los anteriores.
- **Veredicto smoke test:** ✅ ✅ ✅ (todos encontrados, datos enriquecibles disponibles).
- **Riesgo principal:** **costo por cuota**. Hard cap del informe (50) protege esta investigación; el cap real (1000/mes) protege producción si se respeta el promedio 0.6 calls/profesor.
- **Riesgo secundario:** **extract tiene tasa de fallo** (~50% en el test). Sites con CDN agresivo o WAF bloquean Tavily. Mitigación: tener fuentes alternativas; el fallo es no-bloqueante.

## Decisión para pipeline

Tavily ES tier 4 enrichment con presupuesto explícito. Implementación:

1. `TavilySource` SOLO en fase enrichment, NUNCA validation.
2. Trigger condicional: ejecutar solo si los enrichers anteriores (OpenAlex, ORCID, UNMSM CV PDF) dejaron campos clave vacíos (ej. `photo_url`, `bio`).
3. `BudgetTracker` con hard cap 950 (margen 50 bajo el límite oficial 1000).
4. **Smoke test del Tavily extract:** 2 URLs probadas, 1 falló (sciprofiles). Documentar este riesgo en el código.
5. Cache TTL 30 días por (search_query, profesor_id) para evitar gastar cuota en re-fetches.

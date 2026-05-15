# Smoke test — Semantic Scholar API (Academic Graph)

**Fecha:** 2026-05-11
**Modo de acceso:** API REST pública, JSON.
**URL base:** `https://api.semanticscholar.org/graph/v1/`
**Auth:** sin auth para queries básicas; API key gratis incrementa rate limit.
**Rate limit sin auth:** ~100 req / 5 min (≈ 1 req/3s). Con API key gratis: 1 req/s sostenido.
**ToS:** uso libre con atribución; permite uso comercial.

## Endpoints usados

```
GET https://api.semanticscholar.org/graph/v1/author/search?query=NAMES&fields=name,affiliations,paperCount,citationCount,hIndex&limit=5
GET https://api.semanticscholar.org/graph/v1/author/{authorId}?fields=name,affiliations,paperCount,papers.year,papers.venue
```

## Profesor 1 (high-profile): Ciro Rodriguez Rodriguez

- **Search hits:** 61 (problema severo de homónimos — "C. Rodriguez" sin disambiguación).
- **Top hits muestreados (papers, h-index):**
  - `144979365` | C. Rodriguez | papers=10 | h=4
  - `2112359270` | C. Rodriguez | papers=17 | h=6
  - `2147297102` | C. Rodriguez | papers=24 | h=6
  - ...
- **Affiliations:** **vacío** en todos los hits. No hay forma de identificar cuál es el UNMSM sin matching contra otra fuente.
- **Veredicto:** ⚠️ (datos presentes pero inutilizables sin cross-reference).

## Profesor 2 (medio): Lenis Rossi Wong Portillo

- **Search hits:** 0.
- **Veredicto:** ❌ (Semantic Scholar no la indexa, a pesar de tener 23 papers en ORCID + 63 en OpenAlex).
- **Implicación:** la cobertura de SS tiene gaps importantes en publicaciones peruanas.

## Profesor 3 (low-profile): Adegundo Camara Figueroa

- **Search hits:** 1.
- **Match:** `2231808708` | "Adegundo Camara-Figueroa" | papers=6 | h-index=2 | cites=14.
- **Detail endpoint expuso:**
  - Affiliations: `[]` (vacío)
  - Years de publicaciones: 2023, 2025 (confirma actividad reciente)
  - Sample venues: LACCEI conference, Applied Sciences journal, IJEET, Iberian CIST conference, Ingénierie des Systèmes d'Information
- **Veredicto:** ✅ pero limitado (sin affiliation no se puede usar para validation).

## Limitaciones críticas detectadas

1. **Campo `affiliations` consistentemente vacío** para todos los profesores en el smoke test. Semantic Scholar no expone afiliación institucional de forma confiable en el author endpoint.
2. **No hay filtro por institución** en la query de búsqueda. La forma estándar es: search por nombre + traer todos los hits + filtrar manualmente. Pero sin campo affiliation poblado, ese filtro no es viable.
3. **Cobertura inconsistente.** Encontró al low-profile pero no al medio. Esto indica que el corpus indexado tiene huecos no predecibles para autores peruanos.
4. **Homónimo abrumador para nombres comunes.** "Ciro Rodriguez" devuelve 61 hits sin disambiguación.

## Datos útiles que SÍ provee

- **`venue`** por paper: nombres de conferencias y revistas. Útil para enriquecer perfil con "publica en X conference".
- **`year`** por paper: confirma actividad reciente, mismo señal que OpenAlex.
- **`hIndex`, `citationCount`, `paperCount`** agregados: métricas comparables.
- **Papers.title** + cita: si Puntualo quisiera mostrar "publicaciones recientes" sin DOI.

## Conclusión

- **Cobertura UNMSM:** **Baja-Media**. 1/3 con match limpio, 1/3 con match enredado por homónimos, 1/3 sin match.
- **Tipo de afiliación:** **N/A en práctica** — el campo existe en el schema pero está vacío para los casos peruanos del smoke test.
- **Rol en pipeline:** **Enrichment optativo tier 3**. Útil solo como **complemento secundario** después de OpenAlex y ORCID, principalmente para enriquecer con `venue` y `paperCount`.
- **Veredicto smoke test:** ⚠️ ❌ ⚠️ (ningún match limpio).
- **Riesgo principal:** dependencia de un dato que la fuente expone vacío hace que el matching sea poco confiable. Implementación dependiente de SS requeriría cross-reference con OpenAlex/ORCID — momento en el que ya tenemos toda la info de las fuentes mejores.

## Decisión para pipeline

Semantic Scholar **NO ES TIER 1**. Recomendaciones:

1. **No incluir en MVP.** OpenAlex cubre todo lo que Semantic Scholar daría y más, con filtros más confiables.
2. **Considerar en v2** si se quiere enriquecimiento de "venues" no cubiertos por OpenAlex (ej. conferencias regionales LACCEI).
3. Si se incluye eventualmente: usar como `SemanticScholarSource` con `role=enrichment` solamente, y disparar solo si el profesor ya está validado por otra fuente (post-validation enrichment).

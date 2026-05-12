# Smoke test — OpenAlex API

**Fecha:** 2026-05-11
**Modo de acceso:** API REST pública, JSON.
**URL base:** `https://api.openalex.org/`
**Auth requerida:** no. Recomendado pasar email en User-Agent ("polite pool") para mejor servicio.
**Rate limit:** 100 000 req/día — extremadamente generoso.
**ToS:** datos abiertos bajo CC0. Permite uso comercial e integración sin restricciones documentadas.

## Identificador de la institución UNMSM

Búsqueda institucional inicial:
```
GET https://api.openalex.org/institutions?search=Universidad+Nacional+Mayor+de+San+Marcos
```

Resultado: **`https://openalex.org/I192513696`** | "National University of San Marcos" | PE | 43 262 works | type=education.

Este ID se usa en todos los filtros subsiguientes.

## Aprendizaje crítico: filtro correcto

**Mal:** `filter=last_known_institutions.id:I192513696` — excluye a profesores con afiliación dual donde UNMSM NO es la última institución indexada por OpenAlex (caso Lenis Wong, que también enseña en UPC).

**Bien:** `filter=affiliations.institution.id:I192513696` — captura cualquier afiliación histórica con UNMSM, incluyendo profesores duales y emeritos recientes.

## Profesor 1 (high-profile): Ciro Rodriguez Rodriguez

- **Encontrado:** ✅
- **Display name:** "Ciro Rodríguez"
- **ORCID asociado:** `https://orcid.org/0000-0003-2112-1349`
- **Works:** 231
- **Cited by:** 1068
- **Last known institution:** National University of San Marcos
- **Tiempo de respuesta:** ~600 ms
- **Match dudoso:** 4 entries devueltas por la query (OpenAlex no deduplicó completamente sus perfiles; uno principal con 231 works + 3 menores con 2-3 works). Para validar afiliación: el principal alcanza. Para enriquecimiento: usar el principal y descartar duplicados con works_count bajo.
- **Notas:** OpenAlex también devuelve los top "concepts" (áreas de investigación inferidas). Para Ciro presumiblemente abarca ciencias de la computación e ingeniería de sistemas.

## Profesor 2 (medio): Lenis Rossi Wong Portillo

- **Encontrado:** ✅ (con filtro correcto). ❌ inicialmente con `last_known_institutions.id` (falso negativo).
- **Display name:** "Lenis Wong"
- **ORCID asociado:** `https://orcid.org/0000-0002-5032-3233`
- **Works:** 63
- **Last known institution:** Peruvian University of Applied Sciences (UPC) — porque su afiliación más reciente está en UPC
- **Afiliaciones completas:** UPC + National University of San Marcos + "Universidad San Marcos" (duplicado por normalización imperfecta del display_name)
- **Tiempo de respuesta:** ~500 ms
- **Notas:** El comportamiento de `last_known_institutions` es un footgun importante. Confirma que el pipeline DEBE usar el filtro `affiliations.institution.id` o riesga falsos negativos.

## Profesor 3 (low-profile): Adegundo Mario Camara Figueroa

- **Encontrado:** ✅ (sorpresa positiva — refutó la hipótesis del plan original que asumía baja cobertura para auxiliares)
- **Display name:** "Adegundo Cámara-Figueroa" (con tilde y guion — diferente del directorio UNMSM que usa "CAMARA FIGUEROA, Adegundo Mario")
- **ORCID asociado:** `https://orcid.org/0000-0001-5635-7277`
- **Works:** 8
- **Cited by:** 29
- **Affiliations:** National University of San Marcos | years=[2025, 2023] ← **datos 2025 confirman afiliación activa** (más reciente que el directorio UNMSM 2024-I)
- **Top concepts:** Computer science, Data mining, Artificial intelligence, World Wide Web, Archaeology
- **Notas:** **Hallazgo decisivo.** Aun el low-profile tiene publicaciones indexadas y afiliación UNMSM confirmada en 2025. OpenAlex tiene **mejor freshness** que el propio Directorio UNMSM (cuya última tabla es 2024-I). Las "concepts" son input directo para el resumen IA.

## Conclusión

- **Cobertura UNMSM:** **Alta**. 3/3 profesores encontrados con el filtro correcto. La cobertura es excelente porque OpenAlex se basa en publicaciones, y cualquier docente con al menos 1 paper indexado aparece.
- **Tipo de afiliación:** **Explícita** con campo `affiliations[]` que incluye fechas (`years` array).
- **Campos disponibles:** display_name, ORCID, works_count, cited_by_count, afiliaciones con años, top concepts (áreas de investigación), h-index implícito vía counts. Muy rico.
- **Rol en pipeline:** **Validation tier 1 + Enrichment tier 1**. OpenAlex es tan bueno que podría ser el primer source consultado.
- **Veredicto smoke test:** ✅ ✅ ✅ (3/3) — el único source que pasó con todos los perfiles.
- **Riesgo principal:** **dependencia de un servicio externo no estatal** (OpenAlex es operado por OurResearch, una nonprofit). Aunque su sustentabilidad parece sólida (rondas de financiamiento + uso institucional masivo), no es un proveedor del Estado peruano como SUNEDU/CONCYTEC.
- **Riesgo secundario:** OpenAlex normaliza display_names de forma imperfecta (vimos "Universidad San Marcos" duplicado de "National University of San Marcos"). Para el matching contra Puntualo, comparar institution.id, NO display_name.

## Decisión para pipeline

OpenAlex es **tier 1 para validation y enrichment**. Implementación:

1. `OpenAlexSource.validate(full_name, university_id="I192513696")` →
   - Search by name with `affiliations.institution.id:I192513696` filter
   - If 1+ hits → `affiliation_confirmed=True`, `confidence=0.9`
   - If 0 hits → no confirma (pero no descalifica; el profesor puede no haber publicado)

2. `OpenAlexSource.enrich(orcid)` (preferible) o `(full_name)` (fallback) →
   - Get author record
   - Extract: works_count, cited_by_count, top_concepts, affiliations[] con años, ORCID

3. **Rate limit:** 100K/día es enorme — sin necesidad de Redis-backed throttle agresivo. Caché TTL 7 días.

4. **Política ante múltiples hits:** ordenar por `works_count` descendente; el principal es típicamente la deduplicación correcta. Si los top 2 tienen ratio works_count similar, marcar para revisión manual.

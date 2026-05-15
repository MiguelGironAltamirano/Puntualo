# Fuentes gratuitas para validación de profesores UNMSM — Informe

**Fecha:** 2026-05-11
**Autor:** Mathias Torres (asistido por Claude Code)
**Spec base:** `docs/superpowers/specs/2026-05-11-professor-validation-research-design.md`

---

## 1. TL;DR

Para validar y enriquecer profesores UNMSM gratis, **el pipeline MVP debe usar 3 fuentes** (Directorio UNMSM + OpenAlex + ORCID) en lugar de las 7 propuestas en la spec original. **OpenAlex es la fuente más rica y completa** (3/3 hits incluyendo el low-profile, datos de 2025, ORCID asociado, top concepts, citas), pero requiere usar el filtro `affiliations.institution.id:I192513696` (NO `last_known_institutions.id`, que excluye a docentes con afiliación dual). El **Directorio UNMSM/FISI scrapeado** sigue siendo la autoridad oficial primaria a pesar de su freshness limitada (último semestre listado: 2024-I). **ORCID** complementa con datos riquísimos de empleo, educación y cursos dictados. **SUNEDU, CPPe y Google Scholar quedan descartados** por captcha, scope legal y ToS respectivamente. **Semantic Scholar y RENACYT** se difieren post-MVP (cobertura inconsistente / endpoint no documentado). **Tavily** se mantiene como fallback de enrichment con presupuesto duro (hard cap 950/mes; análisis prevé ~0.6 calls/profesor promedio → 1666 prof/mes de capacidad). **Hallazgo competitivo:** `peru.misprofesores.com` ya opera con reseñas UNMSM activas hasta Mar 2026 — Puntualo debe diferenciarse vía UX + enriquecimiento estructurado + resumen IA.

---

## 2. Contexto y objetivo

Puntualo (plataforma de opiniones docentes UNMSM) necesita validar que cada profesor cargado:
1. Existe.
2. Tiene afiliación actual con UNMSM.
3. Tiene datos enriquecibles para un futuro resumen IA.

Este informe evalúa qué fuentes gratuitas (datos abiertos, scraping legal, free tiers) sirven para cumplir esos tres objetivos, y propone un pipeline ordenado.

Decisiones previas tomadas en brainstorming (ver spec):
- Free tier OK, sin rebasar límites.
- Scraping OK con etiqueta (robots.txt, rate limit, UA identificable).
- Foco inicial: FISI / UNMSM. Arquitectura extensible a otras universidades.

---

## 3. Profesores de smoke test

**Directorio fuente:** `https://sistemas.unmsm.edu.pe/site/docentes/directorio` (subdominio FISI), departamentos académicos DACC y DAISW. Scraping del 2026-05-11. Snapshots crudos en `docs/research/_raw/fisi-{dacc,daisw}.html`.

**Caveat de freshness:** el meta-tag de la página referencia "SEMESTRE ACADÉMICO 2019-I/II". La lista visible es de 2019; el portal sigue activo pero la frescura es un riesgo conocido que se documenta en la sección 7.

### Profesores seleccionados

| # | Perfil | Nombre completo | Categoría docente | Departamento | Email institucional |
|---|---|---|---|---|---|
| 1 | High-profile | **Ciro Rodriguez Rodriguez** | Principal T.C. 40 | DAISW | `crodriguezro@unmsm.edu.pe` |
| 2 | Medio | **Lenis Rossi Wong Portillo** | Asociada T.C. 40 | DAISW | `lwongp@unmsm.edu.pe` |
| 3 | Low-profile | **Adegundo Mario Camara Figueroa** | Auxiliar T.P. 20 | DACC | `adegundo.camara@unmsm.edu.pe` |

Detalle de selección (incluida la justificación de cada perfil, los criterios de homónimos y la elección entre departamentos) en `docs/research/_raw/smoke-test-professors.md`.

---

## 4. Fuentes investigadas

### 4.1 Directorio docente UNMSM

| Dimensión | Valor |
|---|---|
| Cobertura UNMSM | **Alta** — los 3 profesores encontrados (incl. el low-profile) |
| Tipo de afiliación | Explícita (la URL implica UNMSM/FISI; la columna `CAT` confirma rol docente) |
| Campos disponibles | nombre, categoría docente, dedicación (T.C./T.P./D.E. + horas), pregrado/posgrado (X), email, link a CV PDF |
| Modo de acceso | Scraping HTML de un archivo por departamento (DACC, DAISW) + lista de posgrado. Sin fichas individuales. |
| Costo y cuota | Gratis. Sin cuota. Rate limit defensivo 1 req/s. |
| ToS y robots.txt | `unmsm.edu.pe/robots.txt`: `User-agent: *` con `Allow: /`. `sistemas.unmsm.edu.pe`: 404 (default permisivo). Scraping permitido. |
| Match quality | Sin buscador embebido; requiere parsear tabla completa. Inconsistencia de tildes y prefijos entre listas pregrado y posgrado — exige normalización NFKD + lowercase. |
| Freshness | **Media-Baja**. Última tabla = 2024-I. Gap notable de ~2 años hasta la fecha del informe. No se actualiza cada semestre. |
| Rol en pipeline | **Validation + Enrichment (parcial)** — tier 1 de validación, tier 2 de enrichment (cubre datos básicos, no foto ni ORCID) |
| Veredicto smoke test | ✅ ✅ ✅ (3/3 encontrados) |
| Riesgo principal | **Freshness** (data 2024-I es lo más nuevo). Mitigación: cross-check con SUNEDU. |

**Detalles del smoke test:** ver `docs/research/_raw/smoke-test-unmsm.md`.

**Hallazgos cualitativos clave:**

1. **El directorio tiene tres URLs separadas** que el scraper debe consultar para cobertura completa: `/directorio-dacc`, `/directorio-daisw` (pregrado por departamento) y `/posgrado/docentes/` (posgrado). El high-profile del smoke test **solo aparece en posgrado** en la última tabla disponible — si el scraper solo lee pregrado, lo perdería.

2. **Inconsistencia de formato entre listas:** pregrado lista nombres en MAYÚSCULAS sin tildes (`RODRIGUEZ RODRIGUEZ CIRO`), mientras posgrado usa tildes y prefijo de grado (`Dr. Ciro Rodríguez Rodríguez`). Cualquier matcher debe normalizar (NFKD + lowercase + strip prefijos honoríficos) antes de comparar.

3. **Cobertura del low-profile fue una sorpresa positiva.** La hipótesis del plan era que un Auxiliar T.P. 20 podría no aparecer; sí aparece y además tiene CV en PDF.

4. **Estructura HTML es razonablemente estable** dentro de una página, pero varía entre semestres (algunos `<td>` tienen atributos, otros no). Scraper debe usar regex tolerante o BeautifulSoup con selectores flexibles.

### 4.2 SUNEDU — Consulta de Docentes Universitarios

| Dimensión | Valor |
|---|---|
| Cobertura UNMSM | **N/A** — la fuente no es accesible programáticamente |
| Tipo de afiliación | La fuente no expone afiliación docente; solo verifica grados/títulos (señal incorrecta para Puntualo) |
| Campos disponibles | DNI, nombres, grado/título, universidad emisora, año (vía consulta manual con captcha) |
| Modo de acceso | Web SPA con **Cloudflare Turnstile captcha** + página HTML manual sin endpoint REST |
| Costo y cuota | Gratis (consumer-facing), pero requiere intervención humana por captcha |
| ToS y robots.txt | Datos públicos del Estado peruano; no hay restricción legal documentada, pero hay restricción técnica que bloquea automatización |
| Match quality | Búsqueda por DNI o nombre vía formulario manual |
| Freshness | Alta (registro oficial actualizado por la SUNEDU directamente) — pero inaccesible |
| Rol en pipeline | **Descartar para automatización**. Posible uso manual por admin en casos dudosos |
| Veredicto smoke test | **NO EJECUTADO** (captcha bloquea acceso automatizado) |
| Riesgo principal | Acoplarse a esta fuente crearía un dead-end técnico. No hay vía pragmática de scraping |

**Detalles del smoke test:** ver `docs/research/_raw/smoke-test-sunedu.md`.

**Hallazgos cualitativos clave:**

1. **Doble bloqueo: técnico + semántico.** El portal `enlinea.sunedu.gob.pe/verificainscripcion` está protegido por Cloudflare Turnstile (descarta scraping automatizado). Aun resolviendo el captcha, la señal devuelta — "esta persona tiene grados inscritos en SUNEDU" — no equivale a la señal que Puntualo necesita — "esta persona enseña actualmente en UNMSM".

2. **Hallazgo colateral: MEF Datos Abiertos `PERSONALSP_2022.csv` (603 MB).** Es el dataset oficial de planilla del sector público, donde UNMSM aparece como pliego, pero los datos están **agregados por grupo ocupacional**, no individualizados. No sirve para validar a una persona específica. Útil solo para estadística.

3. **El `PLAN_TAREA_2_4.md` original anticipaba este escenario** (lo deja como decisión abierta entre mock o scraping frágil). Este informe lo cierra: **eliminar SUNEDU del pipeline automatizado**. La combinación Directorio UNMSM + fuentes académicas (Tasks 8, 10, 11) cubre la necesidad con mejor relación costo/beneficio.

4. **Implicación para el plan de implementación:** el `SuneduService` planeado se reemplaza por un `UnmsmDirectorySource` como tier 1 de validación. Los scaffolds de Celery + Redis + circuit breaker del plan 2.4 actual son **reusables tal cual** — solo cambian las clases concretas de sources.

### 4.3 RENACYT (CONCYTEC)

| Dimensión | Valor |
|---|---|
| Cobertura UNMSM | **Media** — solo investigadores formalmente registrados (alta para Principales con doctorado, media para Asociados, baja para Auxiliares) |
| Tipo de afiliación | **Explícita** — campo "Experiencia laboral" en perfil CTI Vitae confirma afiliación UNMSM con fechas |
| Campos disponibles | nombres, doc redacted, grados académicos, experiencia laboral con fechas, experiencia como asesor de tesis, publicaciones, líneas de investigación, nivel RENACYT (I-V / Carlos Monge / María Rostworowski) |
| Modo de acceso | Frontend Angular SPA (search por nombre requiere endpoint REST aún no descubierto) + perfil individual scrapeable por ID vía `ctivitae.concytec.gob.pe/appDirectorioCTI/VerDatosInvestigador.do?id_investigador=N` |
| Costo y cuota | Gratis. Sin cuota. Rate limit defensivo 1 req/s. |
| ToS y robots.txt | `Disallow:` vacío (permite todo). Datos públicos del Estado peruano. |
| Match quality | Sin homónimos visibles dado que IDs son únicos. Búsqueda por nombre limitada por bloqueo de session en endpoint legacy. |
| Freshness | Alta (datos actualizados por los propios investigadores en CTI Vitae) |
| Rol en pipeline | **Enrichment principal + Validation parcial (tier 2)** — excelente para enriquecimiento; no válido como único validador por cobertura incompleta |
| Veredicto smoke test | ⚠️⚠️⚠️ (datos disponibles pero requiere desbloquear search endpoint primero) |
| Riesgo principal | Dependencia de endpoint no documentado del Angular SPA. Mitigación: alternativa vía dataset RENACYT en gob.pe datos abiertos |

**Detalles del smoke test:** ver `docs/research/_raw/smoke-test-renacyt.md`.

**Hallazgos cualitativos clave:**

1. **Doble entrada de datos.** RENACYT/CTI Vitae expone (a) un buscador público SPA Angular en `renacyt.concytec.gob.pe/buscador-ui/`, y (b) perfiles individuales scrapeables vía URL legacy `appDirectorioCTI/VerDatosInvestigador.do?id_investigador=N`. El path (b) está confirmado accesible (HTTP 200, ~335 KB HTML estructurado) pero requiere conocer el ID del investigador antes.

2. **El verdadero blocker es la API de búsqueda por nombre.** El endpoint legacy de búsqueda devuelve "Su sesión ha caducado". El endpoint nuevo del SPA Angular (`ctivitae.concytec.gob.pe/renacyt-backend-v1/...`) no está documentado públicamente; está en lazy-loaded chunks que requieren reverse engineering (~2 horas de trabajo) para confirmar el path.

3. **Cobertura realista para FISI:** estimo que el high-profile (Ciro Rodriguez, Principal con Dr.) está casi seguro registrado; el medio (Lenis Wong) probablemente sí; el low-profile (Adegundo Camara, Auxiliar T.P.) probablemente NO. RENACYT no cubre auxiliares sin producción investigadora. Esto **descarta RENACYT como source único de validación**.

4. **Datos enriquecidos son la fortaleza real.** Cuando RENACYT cubre a un profesor, el payload incluye: experiencia laboral con fechas (confirma afiliación UNMSM con freshness), nivel RENACYT (badge de prestigio para UI), líneas de investigación (input para resumen IA), publicaciones (idem). Es la fuente más rica para enrichment después del propio CV PDF de UNMSM.

5. **Alternativa de mayor estabilidad:** explorar si el catálogo Datos Abiertos del gobierno peruano (`datosabiertos.gob.pe`) expone un dataset estático RENACYT. Si existe, sería preferible a depender del SPA.

### 4.4 Colegio de Profesores del Perú (CPPe)

| Dimensión | Valor |
|---|---|
| Cobertura UNMSM | **Nula** — fuera del scope legal del colegio |
| Tipo de afiliación | N/A |
| Campos disponibles | N/A |
| Modo de acceso | Portal en mantenimiento al momento del informe |
| Costo y cuota | N/A |
| ToS y robots.txt | N/A |
| Match quality | N/A |
| Freshness | N/A |
| Rol en pipeline | **Descartar** |
| Veredicto smoke test | NO EJECUTADO (fuente fuera de universo) |
| Riesgo principal | Confundirlo con CPPP o variantes podría llevar a integrar la fuente equivocada |

**Detalles del smoke test:** ver `docs/research/_raw/smoke-test-cppe.md`.

**Hallazgos clave (concisos):**

CPPe es el Colegio de Profesores del Perú, regido por la Ley 25231. Su Art. 3 limita el ámbito al "profesorado de educación básica y/o educación superior **no universitaria**" — es decir, docentes de inicial/primaria/secundaria + institutos pedagógicos/técnicos. Los docentes universitarios de UNMSM NO son colegiados en CPPe. Como confirmó la búsqueda de la spec, la fuente queda descartada justificadamente. La validación UNMSM se cubre por el Directorio docente UNMSM + RENACYT.

### 4.5 ORCID Public API

| Dimensión | Valor |
|---|---|
| Cobertura UNMSM | **Media-Alta para investigadores activos** (~70% Principales + Asociados con publicaciones); baja para Auxiliares |
| Tipo de afiliación | **Explícita** con fechas de inicio/fin y rol declarado por el propio investigador |
| Campos disponibles | publications (counts + DOIs), employments (org + fechas + rol + cursos), educations, líneas de investigación, biography, ORCID ID universal |
| Modo de acceso | API REST pública JSON. Search + record endpoints sin auth |
| Costo y cuota | **Gratis. Sin cuota dura.** Rate limit generoso (mucho mayor que 1 req/s) |
| ToS y robots.txt | Datos públicos. ToS liberales para uso no comercial e integración |
| Match quality | **Excelente** con query `family-name + given-names + affiliation-org-name`. Sin homónimos en el smoke test |
| Freshness | Alta (actualizado por los propios investigadores) |
| Rol en pipeline | **Enrichment principal (tier 1)** + **Validation complementaria (tier 2)** — cuando aparece, confirma afiliación con datos sólidos |
| Veredicto smoke test | ✅ ✅ ⚠️ (high y medio encontrados con filtro de afiliación; low-profile sí está en ORCID pero requiere búsqueda sin filtro + post-validación) |
| Riesgo principal | Cobertura desigual: ~30%+ de docentes UNMSM no tienen ORCID. No puede ser único validator |

**Detalles del smoke test:** ver `docs/research/_raw/smoke-test-orcid.md`.

**Hallazgos cualitativos clave:**

1. **Match perfecto con `affiliation-org-name`.** La query `given-names:X+AND+family-name:Y+AND+affiliation-org-name:"Universidad Nacional Mayor de San Marcos"` devuelve exactamente 1 resultado para los profesores con ORCID afiliado a UNMSM. Sin falsos positivos, sin homónimos. Match quality "out-of-the-box".

2. **Datos extraordinariamente ricos para enrichment.** Para Lenis Wong, ORCID expone cosas que NINGUNA otra fuente da: cursos específicos dictados ("Gestión de la Configuración y Mantenimiento de Software, Asesoría de Tesis, Metodología de Investigación, Diseño de Software y Algorítmica I y III"), fechas exactas de afiliación, doble afiliación con UPC. Esto es input directo para el futuro resumen IA.

3. **Limitación del filtro `affiliation-org-name`.** Adegundo Camara (Auxiliar T.P.) no apareció con la query filtrada por UNMSM, pero **sí está en ORCID** (`0000-0001-5635-7277`, encontrado via OpenAlex en Task 11 y verificado en su record completo: 1 employment "Universidad Nacional Mayor de San Marcos | Docente"). Lección: la query ORCID con filtro de afiliación tiene falsos negativos cuando el ORCID record del profesor tiene los campos de organización sutilmente distintos. **Estrategia correcta:** búsqueda sin filtro + post-validar afiliación leyendo `employments[]` del record completo.

4. **Sin cuota dura, sin captcha, sin auth — la fuente más amigable del informe.** Si solo pudiéramos elegir una API para enrichment, sería esta.

### 4.6 OpenAlex API

| Dimensión | Valor |
|---|---|
| Cobertura UNMSM | **Alta** — 3/3 profesores encontrados (incluido el low-profile, contra la hipótesis inicial) |
| Tipo de afiliación | **Explícita con años** — campo `affiliations[]` con `institution.id` + `years[]` |
| Campos disponibles | display_name, ORCID, works_count, cited_by_count, affiliations con años, top concepts, publicaciones con DOIs |
| Modo de acceso | API REST pública JSON. Sin auth (polite pool recomienda email en UA) |
| Costo y cuota | Gratis. **100K req/día** — virtualmente sin cuota |
| ToS y robots.txt | Datos abiertos CC0. ToS liberal. |
| Match quality | Excelente con filtro correcto `affiliations.institution.id` (NO `last_known_institutions.id` — footgun documentado en raw) |
| Freshness | **Mejor que el propio directorio UNMSM** — datos 2025 visibles para Adegundo Camara, vs último semestre 2024-I del directorio |
| Rol en pipeline | **Validation tier 1 + Enrichment tier 1** — la fuente más versátil del informe |
| Veredicto smoke test | ✅ ✅ ✅ (3/3) — único source que pasó con todos los perfiles |
| Riesgo principal | Dependencia de servicio externo no estatal (OurResearch nonprofit); sustentabilidad sólida pero no garantizada como un servicio público peruano |

**Detalles del smoke test:** ver `docs/research/_raw/smoke-test-openalex.md`.

**Hallazgos cualitativos clave:**

1. **3/3 en el smoke test.** OpenAlex es el único source que encontró a los 3 profesores con afiliación UNMSM confirmada — incluyendo al low-profile Adegundo, que NO aparece en ORCID con filtro UNMSM (ahí solo está como "Adegundo Camara" sin filtrar por afiliación). Esto refuta la hipótesis del plan de que un Auxiliar T.P. estaría fuera de las fuentes académicas.

2. **El filtro correcto cambia el resultado.** Usar `filter=last_known_institutions.id:I192513696` excluye a Lenis Wong porque su afiliación más reciente en OpenAlex es UPC. El filtro correcto es `filter=affiliations.institution.id:I192513696`, que captura cualquier afiliación histórica. Este es un footgun crítico que debe documentarse en la implementación.

3. **Mejor freshness que UNMSM directamente.** OpenAlex tiene datos 2025 para Adegundo (year=[2025, 2023] en affiliations). El propio directorio UNMSM solo llega a 2024-I. **OpenAlex es más fresco que la fuente "oficial" UNMSM** porque se actualiza con cada paper publicado, mientras el directorio depende de actualizaciones manuales del vicerrectorado.

4. **Rich data para enrichment:** ORCID linked, works/citations counts, top concepts (Computer science, Data mining, AI, etc. — input directo para tags de la ficha del profesor en Puntualo y para el resumen IA), publicaciones con DOI.

5. **Múltiples hits requieren deduplicación.** Ciro Rodriguez devolvió 4 perfiles (uno principal con 231 works + 3 menores). La estrategia: ordenar por works_count descendente, tomar el principal. Si los top 2 tienen ratio similar, flag para revisión manual.

6. **Sin cuota práctica.** 100K req/día implica que Puntualo puede consultar OpenAlex para cada profesor en cada operación sin acercarse al límite.

### 4.7 Semantic Scholar API

| Dimensión | Valor |
|---|---|
| Cobertura UNMSM | **Baja-Media** — 1/3 con match limpio, 1/3 con homónimos enredados, 1/3 sin match |
| Tipo de afiliación | **N/A** — campo `affiliations` consistentemente vacío en los casos peruanos del smoke test |
| Campos disponibles | nombre, paperCount, citationCount, hIndex, papers con year + venue (este último el único valor diferencial sobre OpenAlex) |
| Modo de acceso | API REST JSON. Sin auth → 100 req/5 min. API key gratis → 1 req/s sostenido |
| Costo y cuota | Gratis (con cuota razonable) |
| ToS y robots.txt | Uso libre con atribución, permite uso comercial |
| Match quality | **Pobre** — 61 hits para "Ciro Rodriguez" sin filtro de afiliación posible |
| Freshness | Aceptable (años 2025 visibles), comparable a OpenAlex |
| Rol en pipeline | **Enrichment opcional tier 3** (solo si v2 quiere datos de `venue`); NO INCLUIR en MVP |
| Veredicto smoke test | ⚠️ ❌ ⚠️ — ningún match limpio |
| Riesgo principal | Campo `affiliations` vacío rompe el matching por institución; dependencia obligada en otra fuente para disambiguación |

**Detalles del smoke test:** ver `docs/research/_raw/smoke-test-semanticscholar.md`.

**Hallazgos cualitativos clave:**

1. **Affiliations consistentemente vacías.** El campo existe en el schema pero retorna `[]` para los 3 profesores. Sin afiliación, la disambiguación de homónimos es imposible y la validación de UNMSM imposible.

2. **Cobertura incompleta y errática.** Encontró al low-profile (Adegundo) pero no al medio (Lenis), a pesar de que Lenis tiene 63 papers en OpenAlex. La cobertura para autores peruanos tiene huecos que no son predecibles por categoría docente.

3. **Único valor diferencial: `venue`.** Semantic Scholar expone el nombre de la conferencia o revista de cada paper (ej. LACCEI, Applied Sciences). OpenAlex también lo expone vía `host_venue`, pero SS tiene mejor cobertura de venues regionales (conferencias latinoamericanas).

4. **Recomendación firme: no incluir en MVP.** Todo lo que SS aporta confiablemente (counts, h-index, años) lo da OpenAlex con mejor matching. Diferir a v2 con `role=enrichment` y trigger post-validation.

### 4.8 Google Scholar (evaluación de viabilidad)

| Dimensión | Valor |
|---|---|
| Cobertura UNMSM | **N/A** — fuente no accesible programáticamente |
| Tipo de afiliación | N/A automated |
| Campos disponibles | N/A para automated |
| Modo de acceso | Sin API pública. robots.txt bloquea `/scholar` y `/search` |
| Costo y cuota | N/A |
| ToS y robots.txt | ToS prohíbe automated access. robots.txt disallow para búsqueda + paginación |
| Match quality | N/A |
| Freshness | N/A |
| Rol en pipeline | **Descartar para automatización**. Permitido únicamente como link manual opt-in del profesor |
| Veredicto smoke test | NO EJECUTADO |
| Riesgo principal | Scrapear violaría ToS, robots.txt y eventualmente activaría captchas/IP bans |

**Detalles del smoke test:** ver `docs/research/_raw/smoke-test-googlescholar.md`.

**Hallazgos cualitativos clave:**

1. **robots.txt bloquea explícitamente la búsqueda.** `Disallow: /scholar`, `Disallow: /search`, `Disallow: /citations?*cstart=` (paginación). Solo `/citations?user={id}` está permitido, pero requiere conocer el ID antes — no hay forma de encontrarlo automáticamente.

2. **No hay API pública.** Google no expone Google Scholar como servicio programático, a diferencia de Search/Books.

3. **No perdemos cobertura significativa.** OpenAlex cubre publicaciones + citas + h-index. ORCID cubre afiliación detallada + educación. Las áreas de investigación están en `x_concepts` de OpenAlex. Lo único que GS aporta uniquely es métricas propietarias (Scholar h-index, i10-index) — nice-to-have, no esencial.

4. **Uso permitido: link manual opt-in.** Si Puntualo permite al profesor (o admin) pegar su Scholar URL, almacenamos el link como `external_links.google_scholar` y lo desplegamos en la UI. NUNCA hacer requests programáticas a `scholar.google.com` desde el backend.

### 4.9 Tavily Search + Extract

| Dimensión | Valor |
|---|---|
| Cobertura UNMSM | **Alta para enrichment** — encuentra perfiles, CVs PDFs, redes sociales, repos académicos |
| Tipo de afiliación | **Inferida** del contenido (no autoritativa) |
| Campos disponibles | URLs de fuentes + texto markdown semi-estructurado vía extract |
| Modo de acceso | API REST con API key. Search + Extract endpoints |
| Costo y cuota | **Free tier 1000/mes** — pero hay que respetarlo. Hard cap interno 950 con margen. |
| ToS y robots.txt | Uso comercial permitido. Tavily respeta robots.txt de los sitios destino |
| Match quality | Buena para search. Extract con ~50% tasa de fallo (algunos sitios bloquean) |
| Freshness | Excelente (Tavily indexa web en tiempo casi-real) |
| Rol en pipeline | **Enrichment fallback tier 4** — NUNCA validation, NUNCA path crítico |
| Veredicto smoke test | ✅ ✅ ✅ (3/3 encontrados con datos enriquecibles) |
| Riesgo principal | Costo por cuota + tasa de fallo de extract |

**Detalles del smoke test:** ver `docs/research/_raw/smoke-test-tavily.md`.

**Hallazgos cualitativos clave:**

1. **Hallazgo competitivo crítico: `peru.misprofesores.com`** es una plataforma activa de reseñas docentes peruanas con cobertura UNMSM (Ciro: calidad 4.8, 12 calificaciones; Lenis: presente; comentarios fechados hasta Mar 2026). Implicación para Puntualo: el mercado existe pero ya hay un jugador. La diferenciación deberá venir de UX + datos enriquecidos + resumen IA.

2. **Cobertura adicional única.** Tavily encontró cosas que ninguna otra fuente reveló: Lenis Wong aparece en `sistemas.unmsm.edu.pe/site/home/directivos` (relación de directivos FISI — info no expuesta en el directorio docente regular). Adegundo aparece como "Especialista TECH-6" en Studocu — confirma rol administrativo además del docente.

3. **Tavily Extract tiene tasa de fallo no trivial.** De 2 URLs probadas, 1 falló (sciprofiles devolvió "Failed to fetch url"). El call fallido sigue contando contra cuota. Implementación debe tener fallback graceful + métricas de éxito por dominio.

4. **Cálculo de capacidad realista:** asumiendo 30% de profesores requieren Tavily como fallback (promedio 2 calls cada uno), free tier soporta **~1666 profesores nuevos/mes**. UNMSM tiene ~3000 docentes totales; FISI ~80. Migración inicial cabe holgadamente.

5. **Sólo enrichment, nunca validation.** Los hits de Tavily son URLs, no aserciones estructuradas. Para validar "profesor X enseña en UNMSM" se necesita parsing del contenido — lo cual es frágil y aporta menos confianza que OpenAlex o el directorio directo.

---

## 5. Smoke test results — matriz consolidada

Leyenda:
- ✅ encontrado con afiliación UNMSM confirmada o confirmable
- ⚠️ encontrado pero ambiguo, requiere desbloqueo técnico, o sin afiliación clara
- ❌ no encontrado / no aplica al perfil
- — fuente no ejecutó smoke test (descartada upstream)

| Fuente | High-profile (Ciro Rodriguez) | Medio (Lenis Wong) | Low-profile (Adegundo Camara) |
|---|---|---|---|
| **Directorio UNMSM** | ✅ (lista posgrado, "Dr. Ciro Rodríguez Rodríguez") | ✅ (DAISW 2024-I, Asociada T.C.) | ✅ (DACC 2024-I, Auxiliar T.P.) |
| **SUNEDU** | — (captcha, fuera de scope semántico) | — | — |
| **RENACYT** | ⚠️ (alta probabilidad pero search endpoint bloqueado) | ⚠️ (media probabilidad) | ⚠️ (baja probabilidad) |
| **CPPe** | — (fuera de scope legal: solo EBR + no-universitario) | — | — |
| **ORCID** | ✅ (`0000-0003-2112-1349`, 229 works, afil UNMSM 2018+) | ✅ (`0000-0002-5032-3233`, 23 works, afil UNMSM 2012+, cursos dictados) | ⚠️ (ORCID `0000-0001-5635-7277` existe pero el filtro `affiliation-org-name` lo excluye; búsqueda por nombre solo lo encuentra) |
| **OpenAlex** | ✅ (231 works, afil UNMSM) | ✅ (63 works, afil UNMSM con filtro correcto) | ✅ (8 works, afil UNMSM years=[2025, 2023]) |
| **Semantic Scholar** | ⚠️ (61 hits, homónimos sin filtro de afiliación) | ❌ (no indexada) | ⚠️ (encontrado pero sin campo affiliation) |
| **Google Scholar** | — (ToS prohíbe automated access) | — | — |
| **Tavily** | ✅ (sciprofiles + CV PDF + MisProfesores + Academia + GS link) | ✅ (CV PDF + directivos UNMSM + MisProfesores) | ✅ (CV PDF + Studocu + CORE + directorio) |

### Lecturas de la matriz

- **Mejor fuente única para validación:** **OpenAlex** — pasó con 3/3 incluyendo el low-profile. Es la única fuente que confirma afiliación UNMSM para los 3 con datos estructurados (filtro `affiliations.institution.id:I192513696`).
- **Mejor combinación tier 1:** **Directorio UNMSM + OpenAlex**. El directorio aporta autoridad oficial UNMSM (fuente primaria), OpenAlex aporta verificación cruzada con freshness 2025. Ambos pasaron con 3/3.
- **Mejor fuente para enrichment narrativo:** **ORCID** — datos extraordinariamente ricos (publicaciones, fechas de empleo, cursos dictados) cuando cubre. Cobertura desigual (2/3) la descalifica como único validator.
- **Sorpresa positiva del smoke test:** el low-profile Adegundo Camara apareció en OpenAlex con datos 2025. La hipótesis del plan ("auxiliares no estarán en fuentes académicas") quedó refutada parcialmente. Confirma que OpenAlex es más inclusivo que ORCID/Semantic Scholar.
- **Confirmaciones esperadas:**
  - SUNEDU no es viable para automatización (captcha + scope semántico equivocado).
  - CPPe no aplica (ley 25231 limita scope a EBR + no-universitario).
  - Google Scholar prohibido por ToS + robots.txt.
  - Semantic Scholar tiene cobertura inconsistente para autores peruanos.
- **Lección de implementación:** filtros importan más que cobertura cruda. OpenAlex `last_known_institutions.id` falla con Lenis; OpenAlex `affiliations.institution.id` pasa. Documentar esto explícitamente en el código.

---

## 6. Pipeline recomendado

Implementación del **Enfoque 2 — Pipeline jerárquico con enriquecimiento** definido en la spec, con el orden de fuentes ajustado a la evidencia del smoke test.

### Fase de validación (corta apenas una confirma afiliación UNMSM)

1. **`UnmsmDirectorySource`** — TIER 1. Scrapea los 3 índices del directorio FISI (`directorio-dacc`, `directorio-daisw`, `posgrado/docentes/`). Justificación: fuente oficial autoritativa de UNMSM, 3/3 hits, datos básicos (categoría, dedicación, CV PDF).
2. **`OpenAlexSource`** — TIER 1 (paralelo, no sequential). Filtro `affiliations.institution.id:I192513696`. Justificación: 3/3 hits con datos hasta 2025 (mejor freshness que el directorio), confirma afiliación con metadatos académicos.
3. **`OrcidSource`** — TIER 2 (cross-check). Query por nombre sin filtro de afiliación, post-validar con check de `employments[].organization`. Justificación: 2/3 hits, datos riquísimos cuando aplica.

**Política de corte:** si UnmsmDirectory **O** OpenAlex confirma → `validation_status = "validated"`. Si **ambos** fallan → `validation_status = "not_found"`. Esta política reduce falsos negativos sin requerir consenso (ORCID/OpenAlex pueden discrepar legítimamente de UNMSM si el directorio está stale).

### Fase de enriquecimiento (en paralelo, dentro de cuota)

Tras `validated`, lanzar todos los enrichers que apliquen:

1. **`UnmsmDirectoryEnricher`** — extrae categoría, dedicación, link al CV PDF, departamento académico (DACC/DAISW), pregrado/posgrado flags.
2. **`OpenAlexEnricher`** — works_count, cited_by_count, top concepts (areas de investigación), publicaciones recientes con DOIs, ORCID link.
3. **`OrcidEnricher`** — biography, employment history con fechas, educación (grados con instituciones), keywords, **cursos dictados** (cuando el profesor lo declara, ej. caso Lenis Wong).
4. **`RenacytEnricher`** (cuando search endpoint se desbloquee) — nivel RENACYT (badge tipo "Carlos Monge" para UI), líneas de investigación, experiencia como asesor de tesis.
5. **`TavilyEnricher`** — SOLO si los enrichers 1-4 dejaron vacíos campos clave (`photo_url`, `bio_narrative`, `external_links`). Sujeto a `BudgetTracker` con hard cap 950/mes.

### Resolución de conflictos en enriquecimiento

Cuando dos enrichers entregan valores distintos para el mismo campo (ej. "departamento académico"):
- **Prioridad de afiliación:** `UnmsmDirectory > OpenAlex > ORCID > Tavily`.
- **Prioridad de datos académicos** (publicaciones, citas, concepts): `OpenAlex > ORCID > Semantic Scholar > Tavily`.
- **Prioridad de identificadores externos** (ORCID, Scholar ID): `ORCID > OpenAlex` (ORCID ID es canónico).
- **Provenance se preserva siempre** en `ProfessorEvidence[]` (tabla nueva por la spec) — el AI summary y la UI tendrán trazabilidad por fuente.

### Mapeo a clases concretas

| Source en pipeline | Clase concreta | Role | Tier validation | Tier enrichment |
|---|---|---|---|---|
| UnmsmDirectory | `UnmsmDirectorySource` | both | 1 | 1 |
| OpenAlex | `OpenAlexSource` | both | 1 | 1 |
| ORCID | `OrcidSource` | both | 2 | 1 |
| RENACYT | `RenacytSource` | enrichment | — | 2 (post-MVP) |
| Tavily | `TavilySource` | enrichment | — | 4 (fallback, budgeted) |
| Semantic Scholar | `SemanticScholarSource` | enrichment | — | 3 (v2, opcional) |
| ~~SUNEDU~~ | ~~descartado~~ | — | — | — |
| ~~CPPe~~ | ~~descartado~~ | — | — | — |
| ~~Google Scholar~~ | ~~descartado para automatización~~ | — | — | — |

### Comparación con la arquitectura propuesta en la spec

La spec proponía 7 sources con orden tentativo `UNMSM > SUNEDU > RENACYT > ORCID > OpenAlex > Semantic Scholar > Tavily`. La evidencia del smoke test obliga a:

- **Promover OpenAlex a tier 1** (estaba en posición 5; debe estar arriba con UNMSM por su cobertura 3/3 y freshness).
- **Eliminar SUNEDU** (la spec lo mantenía como tier 1 esperando ver si era viable; el captcha lo descarta).
- **Bajar RENACYT a tier 2 post-MVP** (la spec lo tenía tier 1; la dependencia de endpoint no documentado lo descalifica de MVP).
- **Mantener Tavily como tier 4 fallback** (correcto en spec).
- **Eliminar Semantic Scholar del MVP** (la spec lo tenía tier 1; el smoke test mostró cobertura inconsistente y campo affiliations vacío).

**El cambio neto:** la spec proponía 7 sources en MVP. La recomendación final es **3 sources en MVP** (UNMSM, OpenAlex, ORCID) + 1 budgeted fallback (Tavily) — un pipeline más simple, más confiable y empíricamente validado.

---

## 7. Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| HTML del directorio UNMSM cambia y rompe scraper | Alta | Medio | Smoke tests `@pytest.mark.smoke` corridos manualmente al sospechar drift; alerta crítica al detectar parse error. Soportar variaciones de `<td>` con/sin atributos |
| Directorio UNMSM no se actualiza más allá de 2024-I | **Confirmado** | Medio | Cross-check con OpenAlex que sí tiene 2025. Si la última tabla del directorio queda más vieja que cierto threshold, marcar dependencia como "stale" en el log |
| OpenAlex cambia política de filtros o discontinúa polite pool | Baja | Medio | Mantener un cliente HTTP con email correcto en UA. Documentar la elección de `affiliations.institution.id` con un test que verifique el shape de respuesta |
| Profesor con nombre extranjero/transliterado (chino, árabe, etc.) | Media | Bajo | OpenAlex maneja Unicode bien (Cámara-Figueroa funcionó con tilde). Normalizar a NFKD pero NO eliminar tildes para queries en ORCID |
| Profesor con homónimos comunes (e.g. "Juan Pérez") | Alta | Medio | Cross-check entre 2+ fuentes con afiliación UNMSM. Si solo Tavily lo confirma (no estructurado) → marcar `validated_with_ambiguity` y requerir review admin |
| Tavily cambia free tier o cierra | Baja | Bajo (no es path crítico) | Pipeline sigue funcionando sin Tavily; perdemos solo enrichment "best effort" |
| Inconsistencia de nombres entre fuentes (e.g. "CAMARA" vs "Cámara-Figueroa") | **Confirmada** | Medio | Normalización NFKD + variantes de family-name al buscar ORCID. Documentado en `smoke-test-orcid.md` y `smoke-test-openalex.md` |
| ORCID search excluye al low-profile cuando se filtra por afil | Confirmado | Medio | Fallback: si query con filtro afil retorna 0, ejecutar query sin filtro y post-validar en el record |
| Free tier Tavily se agota antes de fin de mes (carga inesperada de profesores nuevos) | Media | Bajo | `BudgetTracker` con hard cap 950 + soft warning al 80%. Si se agota: TavilySource lanza `BudgetExhausted` y pipeline lo salta (no falla) |
| Múltiples perfiles OpenAlex para el mismo autor (Ciro tuvo 4) | Confirmada | Bajo | Ordenar por `works_count` desc, tomar el principal. Si top 2 tienen ratio similar (>0.5), flag para revisión manual |
| `peru.misprofesores.com` toma medidas contra Puntualo como competidor | Baja | Bajo | Puntualo no scrapea MisProfesores (no es source en el pipeline). Si en el futuro Puntualo aspirara a importar reseñas, requeriría análisis legal por separado |
| Cambio de Ley peruana sobre datos de docentes universitarios | Baja | Alto | Monitorear publicaciones SUNEDU, CONCYTEC y MINEDU trimestralmente. Toda la data del pipeline es pública por defecto, así que riesgo de privacidad es bajo |

---

## 8. Próximos pasos

1. **Aprobación del informe** por el equipo Puntualo (Miguel, Ángel, Mathias, Nicolas). El informe debería discutirse en una standup o reunión asíncrona; los hallazgos no son obvios y impactan la arquitectura.

2. **Redactar `PLAN_TAREA_2_4_v2.md`** que reemplace al `PLAN_TAREA_2_4.md` actual. Cambios clave:
   - Eliminar `SuneduService` como componente; reemplazar por `ProfessorValidationPipeline` con 3 sources MVP (UNMSM, OpenAlex, ORCID).
   - Conservar el scaffolding Celery + Redis + circuit breaker — es **reusable tal cual**.
   - Agregar `BudgetTracker` para Tavily.
   - Agregar modelo `ProfessorEvidence` (migración Alembic) con campos `(professor_id, source, raw_payload jsonb, fetched_at)`.

3. **Decidir destino del trabajo ya iniciado en plan 2.4 actual:**
   - Conservable: scaffolding Celery + Redis + cliente HTTP `httpx`.
   - Reutilizable con cambios menores: estructura del worker, configuración de retries, circuit breaker pattern.
   - Descartable: `SuneduService` class (si ya se empezó).
   - El cambio neto al PR/branch en curso debería ser ~20% del código planeado, no un rewrite total.

4. **Estimación de esfuerzo para el plan v2:**
   - `UnmsmDirectorySource` (scraping + cache): ~6h.
   - `OpenAlexSource` (cliente + filtro correcto + dedupe): ~4h.
   - `OrcidSource` (cliente + name variants + fallback search): ~4h.
   - `TavilySource` + `BudgetTracker`: ~4h.
   - `ProfessorValidationPipeline` orquestador: ~4h.
   - `ProfessorEvidence` modelo + migración: ~2h.
   - Tests unitarios + smoke tests: ~6h.
   - **Total estimado MVP:** ~30h = ~4 días de un developer (vs. ~3 días que estimaba el plan 2.4 actual; la simplificación a 3 sources reduce el costo neto a pesar de añadir Pipeline + Evidence).

5. **Definir prioridad de RENACYT.** Si el equipo decide ir por la opción "reverse-engineer del Angular bundle de RENACYT" (~2h), se podría sumar `RenacytSource` al MVP. Si no, queda como tarea v2.

6. **Datos de seed para testing.** Recomiendo cargar al menos 10 profesores reales de FISI (no solo los 3 del smoke test) en la DB de dev y correr el pipeline contra ellos al menos una vez antes de desplegar. Sirve como integration test extendido.

7. **Resolver tema admin/revalidate endpoint.** El plan 2.4 actual menciona `POST /professors/{id}/revalidate` como opcional. Para el plan v2 yo lo movería a obligatorio (mínimo viable) porque los falsos negativos serán inevitables y el admin necesita una vía manual para forzar re-validación.

8. **Decidir tema permisos/roles para `validation_status`.** El plan 2.3 dejó esto como TODO. El plan v2 debería resolverlo en simultáneo con la implementación del pipeline.

---

## 9. Apéndice — payloads crudos y queries

Ver `docs/research/_raw/` para los archivos por fuente y `tavily-quota-log.md` para el conteo de cuota consumida.

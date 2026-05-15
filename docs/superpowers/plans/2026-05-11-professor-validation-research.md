# Plan — Investigación de fuentes gratuitas para validación de profesores

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Producir el informe `docs/research/2026-05-11-professor-validation-sources.md` que recomienda qué fuentes gratuitas usar y en qué orden para validar y enriquecer profesores UNMSM en Puntualo, basado en evidencia empírica de un smoke test con 3 profesores reales de FISI.

**Architecture:** No es código de producción. La "arquitectura" es un workflow de investigación: scaffold del documento → seleccionar 3 profesores FISI → investigar cada fuente con desk research + smoke test → sintetizar hallazgos → recomendar pipeline. El informe final implementa el "Enfoque 2 — Pipeline jerárquico" definido en `docs/superpowers/specs/2026-05-11-professor-validation-research-design.md`.

**Tech Stack:** Markdown, `curl`/`httpx` para scraping, skill `tavily-research` para web research, skill `tavily-extract` para extracción estructurada, skill `academic-search` para fuentes académicas.

**Spec base:** `docs/superpowers/specs/2026-05-11-professor-validation-research-design.md`.

**Política de commits:** El usuario indicó "dejala ahi" para la spec. Por consistencia, este plan NO incluye `git commit` automáticos. La Task 19 pregunta al final si commitear todo de una vez.

**Política de cuota Tavily:** Hard cap durante este informe = **50 calls** (de las 1000/mes del free tier). Si una task se acerca al cap, parar y consultar al usuario antes de seguir.

---

## Estructura de archivos del informe

- `docs/research/2026-05-11-professor-validation-sources.md` — informe final.
- `docs/research/_raw/smoke-test-professors.md` — los 3 profesores elegidos con justificación.
- `docs/research/_raw/fisi-directory-snapshot.html` — snapshot del directorio FISI usado para selección (reproducibilidad).
- `docs/research/_raw/smoke-test-{source}.md` — resultados crudos por fuente (uno por fuente).
- `docs/research/_raw/tavily-quota-log.md` — registro vivo del consumo de cuota Tavily (incrementa con cada query).

---

## Task 1: Scaffold del informe y directorio de raws

**Files:**
- Create: `docs/research/2026-05-11-professor-validation-sources.md`
- Create: `docs/research/_raw/.gitkeep`
- Create: `docs/research/_raw/tavily-quota-log.md`

- [ ] **Step 1.1: Crear directorio `docs/research/_raw/`**

```bash
mkdir -p docs/research/_raw
touch docs/research/_raw/.gitkeep
```

- [ ] **Step 1.2: Crear `tavily-quota-log.md` con encabezado**

Contenido literal a escribir en `docs/research/_raw/tavily-quota-log.md`:

```markdown
# Tavily quota log — informe profesores 2026-05-11

Hard cap durante el informe: 50 calls. Free tier mensual: 1000.

| # | Timestamp | Skill usada | Query / URL | Notas |
|---|-----------|-------------|-------------|-------|
```

- [ ] **Step 1.3: Crear `docs/research/2026-05-11-professor-validation-sources.md` con scaffold de secciones vacías**

Contenido literal a escribir:

```markdown
# Fuentes gratuitas para validación de profesores UNMSM — Informe

**Fecha:** 2026-05-11
**Autor:** Mathias Torres (asistido por Claude Code)
**Spec base:** `docs/superpowers/specs/2026-05-11-professor-validation-research-design.md`

---

## 1. TL;DR

_Pendiente — se rellena al final, después de la síntesis._

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

_Pendiente — se rellena en Task 5._

---

## 4. Fuentes investigadas

### 4.1 Directorio docente UNMSM
_Pendiente — Task 6._

### 4.2 SUNEDU — Consulta de Docentes Universitarios
_Pendiente — Task 7._

### 4.3 RENACYT (CONCYTEC)
_Pendiente — Task 8._

### 4.4 Colegio de Profesores del Perú (CPPe)
_Pendiente — Task 9._

### 4.5 ORCID Public API
_Pendiente — Task 10._

### 4.6 OpenAlex API
_Pendiente — Task 11._

### 4.7 Semantic Scholar API
_Pendiente — Task 12._

### 4.8 Google Scholar (evaluación de viabilidad)
_Pendiente — Task 13._

### 4.9 Tavily Search + Extract
_Pendiente — Task 14._

---

## 5. Smoke test results — matriz consolidada

_Pendiente — Task 15._

---

## 6. Pipeline recomendado

_Pendiente — Task 16._

---

## 7. Riesgos y mitigaciones

_Pendiente — Task 17._

---

## 8. Próximos pasos

_Pendiente — Task 17._

---

## 9. Apéndice — payloads crudos y queries

Ver `docs/research/_raw/` para los archivos por fuente y `tavily-quota-log.md` para el conteo de cuota consumida.
```

- [ ] **Step 1.4: Verificar que los archivos existen**

Run: `ls docs/research/ docs/research/_raw/`
Expected: aparecen `2026-05-11-professor-validation-sources.md`, `_raw/`, `_raw/.gitkeep`, `_raw/tavily-quota-log.md`.

---

## Task 2: Confirmar acceso a Tavily

**Files:** ninguno (verificación de entorno).

- [ ] **Step 2.1: Verificar si la variable `TAVILY_API_KEY` está configurada**

Run: `printenv TAVILY_API_KEY | head -c 8 ; echo`
Expected: imprime los primeros 8 caracteres de la API key, o vacío si no está configurada.

- [ ] **Step 2.2: Si no está configurada, BLOQUEAR y pedir al usuario**

Si el comando anterior devolvió vacío, parar la ejecución del plan y mostrar este mensaje al usuario:

> "Necesito una API key de Tavily para continuar. Por favor:
> 1. Crea cuenta gratis en https://app.tavily.com/
> 2. Copia tu API key
> 3. Exportala: `export TAVILY_API_KEY='tvly-...'`
> 4. Confirmame cuando esté lista."

NO continuar con las siguientes tasks hasta que el usuario confirme.

- [ ] **Step 2.3: Smoke test mínimo de Tavily (1 call)**

Invocar la skill `tavily-search` (o equivalente) con la query: `"Universidad Nacional Mayor de San Marcos FISI directorio docentes"` y `max_results=3`.

Registrar el resultado en `docs/research/_raw/tavily-quota-log.md` como el call #1.

Expected: respuesta con al menos 1 URL hacia `unmsm.edu.pe` o `sistemas.unmsm.edu.pe`.

Si falla (timeout, 401, etc.): documentar el error y pedir al usuario que revise la API key.

---

## Task 3: Identificar URL del directorio docente FISI

**Files:**
- Modify: `docs/research/_raw/smoke-test-professors.md` (crear si no existe)

- [ ] **Step 3.1: Crear `smoke-test-professors.md` con encabezado**

Contenido inicial:

```markdown
# Smoke test — profesores FISI seleccionados

**Spec ref:** sección 4 del meta-diseño.
**Criterio:** 1 high-profile, 1 medio, 1 low-profile.

## Directorio fuente usado

_Pendiente._

## Profesores elegidos

_Pendiente._
```

- [ ] **Step 3.2: A partir de los resultados Tavily del Step 2.3, identificar la URL del directorio FISI**

URLs candidatas conocidas (intentar en este orden):
1. `https://sistemas.unmsm.edu.pe/` (FISI tiene este dominio histórico).
2. `https://fisi.unmsm.edu.pe/`
3. Cualquier URL `unmsm.edu.pe` que mencione "docentes" o "personal" en los resultados Tavily.

- [ ] **Step 3.3: Descargar la página del directorio**

Run (sustituyendo `<URL>` por la URL elegida):

```bash
curl -sSL -A "Puntualo-Research/1.0 (mailto:mathias.torres@unmsm.edu.pe)" \
  "<URL>" -o docs/research/_raw/fisi-directory-snapshot.html
```

Expected: archivo creado con tamaño > 1KB.

Si la URL devuelve 404: probar la siguiente candidata.
Si todas fallan: usar Tavily extract (1 call) sobre `unmsm.edu.pe` con prompt "encontrar directorio de docentes de FISI"; registrar el call en `tavily-quota-log.md`.

- [ ] **Step 3.4: Verificar contenido del snapshot**

Run: `grep -i "docent\|profesor\|catedrático" docs/research/_raw/fisi-directory-snapshot.html | head -5`
Expected: aparecen menciones de docentes/profesores. Si no aparece nada, la URL no es la correcta — volver al Step 3.2.

- [ ] **Step 3.5: Anotar la URL definitiva en `smoke-test-professors.md`**

Reemplazar "Directorio fuente usado: _Pendiente_" con la URL final, fecha de scraping y tamaño del HTML.

---

## Task 4: Seleccionar 3 profesores FISI por perfil

**Files:**
- Modify: `docs/research/_raw/smoke-test-professors.md`
- Modify: `docs/research/2026-05-11-professor-validation-sources.md` (sección 3)

- [ ] **Step 4.1: Extraer lista de nombres del snapshot HTML**

Run: `grep -oE '[A-ZÁÉÍÓÚ][a-záéíóúñ]+ [A-ZÁÉÍÓÚ][a-záéíóúñ]+ [A-ZÁÉÍÓÚ][a-záéíóúñ]+' docs/research/_raw/fisi-directory-snapshot.html | sort -u | head -30`
Expected: lista de candidatos a nombres completos.

Si el grep no encuentra nada útil (HTML demasiado dinámico): leer el archivo con la tool Read y extraer nombres a mano.

- [ ] **Step 4.2: Clasificar candidatos por perfil**

Para cada nombre candidato, hacer una mini-búsqueda en Google Scholar (sin Tavily — buscar manualmente o usar la skill `academic-search`) y clasificar:

- **High-profile:** ≥10 publicaciones indexadas o cargo administrativo en la página (decano, director de escuela).
- **Medio:** 1-10 publicaciones o aparece como docente ordinario.
- **Low-profile:** sin publicaciones encontradas, o auxiliar/contratado.

- [ ] **Step 4.3: Elegir 1 por categoría**

Criterio adicional: NO elegir profesores con nombres extremadamente comunes (ej. "Juan Pérez García") en el smoke test — el problema de homónimos es real pero queremos medir la cobertura de las fuentes, no la robustez del matcher.

- [ ] **Step 4.4: Escribir la selección en `smoke-test-professors.md`**

Plantilla:

```markdown
## Profesores elegidos

### 1. High-profile: [Nombre completo]
- Justificación: [N publicaciones / cargo / etc.]
- URL en directorio FISI: [link]
- ORCID conocido: [si aparece en directorio]

### 2. Medio: [Nombre completo]
- Justificación: [...]
- URL en directorio FISI: [...]

### 3. Low-profile: [Nombre completo]
- Justificación: [...]
- URL en directorio FISI: [...]
```

- [ ] **Step 4.5: Espejar la sección 3 del informe principal**

En `docs/research/2026-05-11-professor-validation-sources.md`, reemplazar el "_Pendiente — Task 5._" de la sección 3 con la misma información (los 3 profesores + criterio de selección + URL del directorio fuente).

---

## Task 5: Plantilla reutilizable para evaluación de fuentes

**Files:** ninguno (referencia para Tasks 6-14).

- [ ] **Step 5.1: Memorizar la plantilla de salida por fuente**

Cada fuente (Tasks 6-14) debe producir DOS artefactos:

**Artefacto A** — archivo crudo en `docs/research/_raw/smoke-test-{source-slug}.md`:

```markdown
# Smoke test — {Source name}

**Fecha:** 2026-05-11
**Modo de acceso:** [API REST / GraphQL / scraping HTML / dataset]
**URL/endpoint base:** [...]
**Auth requerida:** [no / API key gratis / API key paga]
**Rate limit observado:** [...]
**ToS / robots.txt relevante:** [cita literal]

## Profesor 1 (high-profile): [Nombre]
- Query/URL usada: [...]
- Resultado: ✅ encontrado / ❌ no / ⚠️ ambiguo
- Tiempo de respuesta: [ms]
- Campos devueltos: [lista literal]
- Match dudoso/homónimos: [si aplica]
- Notas: [...]

## Profesor 2 (medio): [Nombre]
[mismo formato]

## Profesor 3 (low-profile): [Nombre]
[mismo formato]

## Conclusión

- Cobertura UNMSM: Alta / Media / Baja / Nula
- Tipo de afiliación: explícita / inferida / no aplica
- Rol en pipeline: validation / enrichment / ambos / descartar
- Riesgo principal: [...]
```

**Artefacto B** — subsección de la fuente en el informe principal (`4.X` en `docs/research/2026-05-11-professor-validation-sources.md`), que **resume** el artefacto A en formato tabla:

```markdown
### 4.X {Source name}

| Dimensión | Valor |
|---|---|
| Cobertura UNMSM | Alta / Media / Baja / Nula |
| Tipo de afiliación | explícita / inferida / no |
| Campos disponibles | [lista corta] |
| Modo de acceso | [...] |
| Costo y cuota | [...] |
| ToS y robots.txt | [resumen + link] |
| Match quality | [...] |
| Freshness | [...] |
| Rol en pipeline | validation / enrichment / ambos / descartar |
| Veredicto smoke test | ✅✅✅ / ✅✅❌ / etc. |
| Riesgo principal | [...] |

**Detalles del smoke test:** ver `docs/research/_raw/smoke-test-{slug}.md`.

**Notas:** [1-3 párrafos con los hallazgos cualitativos clave].
```

---

## Task 6: Investigar fuente — Directorio docente UNMSM

**Files:**
- Create: `docs/research/_raw/smoke-test-unmsm.md`
- Modify: `docs/research/2026-05-11-professor-validation-sources.md` (sección 4.1)

- [ ] **Step 6.1: Verificar `robots.txt` del dominio UNMSM**

Run:
```bash
curl -sSL "https://unmsm.edu.pe/robots.txt"
curl -sSL "https://sistemas.unmsm.edu.pe/robots.txt"
```
Expected: ambos devuelven algún contenido (puede ser un robots.txt explícito o un 404; documentar lo que aparezca). Citar literalmente las reglas que aplican a `User-agent: *`.

- [ ] **Step 6.2: Identificar la ficha individual de cada profesor del smoke test**

Para cada uno de los 3 profesores elegidos en Task 4, navegar (con curl) desde el directorio principal hasta la ficha individual. URLs típicas: `<dominio>/docente/<id-o-slug>`.

Si no hay ficha individual y los datos están solo en la lista: anotarlo (cobertura limitada).

- [ ] **Step 6.3: Descargar la ficha de cada profesor**

Run para cada uno:
```bash
curl -sSL -A "Puntualo-Research/1.0" "<url-ficha>" -o /tmp/unmsm-prof-N.html
sleep 1   # rate limit
```

- [ ] **Step 6.4: Inventariar campos disponibles**

Para cada ficha, extraer (con `grep`/Read) qué campos aparecen: nombre, DNI, facultad, departamento, categoría, foto URL, email, ORCID, líneas de investigación, cursos dictados, fecha de ingreso.

- [ ] **Step 6.5: Escribir `docs/research/_raw/smoke-test-unmsm.md`**

Usar la plantilla del Step 5.1, artefacto A, con los datos reales.

- [ ] **Step 6.6: Escribir la sección 4.1 del informe**

Usar la plantilla del Step 5.1, artefacto B.

---

## Task 7: Investigar fuente — SUNEDU Consulta de Docentes Universitarios

**Files:**
- Create: `docs/research/_raw/smoke-test-sunedu.md`
- Modify: `docs/research/2026-05-11-professor-validation-sources.md` (sección 4.2)

- [ ] **Step 7.1: Localizar el portal SUNEDU de consulta de docentes**

Invocar skill `tavily-search` con: `"SUNEDU consulta de docentes universitarios Perú portal"` (`max_results=5`). Registrar como call de Tavily en `tavily-quota-log.md`.

URLs probables: `https://www.sunedu.gob.pe/consultas/` o subdominio similar.

- [ ] **Step 7.2: Verificar `robots.txt` de `sunedu.gob.pe`**

Run: `curl -sSL "https://www.sunedu.gob.pe/robots.txt"`
Documentar la respuesta.

- [ ] **Step 7.3: Inspeccionar el portal para entender el flujo de búsqueda**

Si es un formulario HTML simple → identificar el `<form action=...>` y los parámetros.
Si es una SPA con XHR → identificar el endpoint AJAX (DevTools / network panel manual — el plan asume que esto se hace inspeccionando el HTML descargado).

Si requiere reCAPTCHA: marcar la fuente como `descartar para automatización` y documentar.

- [ ] **Step 7.4: Para cada profesor del smoke test, ejecutar la consulta**

Si es formulario GET/POST simple:
```bash
curl -sSL -A "Puntualo-Research/1.0" \
  --data-urlencode "nombre=<Nombre>" \
  "<endpoint>"
sleep 1
```

Si es endpoint JSON XHR: replicar la petición con `curl` adaptado.

- [ ] **Step 7.5: Analizar resultados — cobertura y match quality**

Por cada profesor:
- ¿Aparece?
- ¿Aparece con UNMSM explícito como universidad?
- ¿Cuántos homónimos aparecen?
- ¿Aparece "Activo" / "Cesado"?

- [ ] **Step 7.6: Escribir `_raw/smoke-test-sunedu.md` (plantilla Step 5.1 A)**

- [ ] **Step 7.7: Escribir sección 4.2 del informe (plantilla Step 5.1 B)**

---

## Task 8: Investigar fuente — RENACYT (CONCYTEC)

**Files:**
- Create: `docs/research/_raw/smoke-test-renacyt.md`
- Modify: `docs/research/2026-05-11-professor-validation-sources.md` (sección 4.3)

- [ ] **Step 8.1: Localizar el portal RENACYT**

Invocar `tavily-search`: `"RENACYT CONCYTEC consulta investigadores"`. Registrar en quota log.

URLs probables: `https://renacyt.concytec.gob.pe/` o subruta.

- [ ] **Step 8.2: Verificar `robots.txt` y ToS**

Run: `curl -sSL "https://renacyt.concytec.gob.pe/robots.txt"`

- [ ] **Step 8.3: Identificar formato de búsqueda**

Igual que Task 7 Step 7.3 — formulario, XHR, o SPA con captcha.

- [ ] **Step 8.4: Consultar cada profesor del smoke test**

Esperar: cobertura PARCIAL — solo investigadores formalmente registrados. Profesor low-profile probablemente NO aparece. Eso es información útil.

- [ ] **Step 8.5: Inventariar campos**

RENACYT típicamente devuelve: nombre, nivel (I/II/III/IV/V María Rostworowski/Carlos Monge), institución de afiliación, líneas de investigación, ORCID si vinculado.

- [ ] **Step 8.6: Escribir `_raw/smoke-test-renacyt.md`**

- [ ] **Step 8.7: Escribir sección 4.3 del informe**

---

## Task 9: Investigar fuente — Colegio de Profesores del Perú (CPPe)

**Files:**
- Create: `docs/research/_raw/smoke-test-cppe.md`
- Modify: `docs/research/2026-05-11-professor-validation-sources.md` (sección 4.4)

- [ ] **Step 9.1: Visitar https://cppe.org.pe y entender alcance**

Run: `curl -sSL -A "Puntualo-Research/1.0" "https://cppe.org.pe" -o /tmp/cppe.html`

Leer con la tool Read: identificar **si CPPe afilia docentes universitarios o solo educación básica regular**. Buscar palabras "universitario", "superior", "universidad".

- [ ] **Step 9.2: Si CPPe es solo EBR (Educación Básica Regular), documentar y descartar**

Escribir conclusión literal en `_raw/smoke-test-cppe.md`:

```markdown
# Smoke test — CPPe (Colegio de Profesores del Perú)

**Conclusión rápida:** CPPe agrupa docentes de educación básica regular (inicial/primaria/secundaria), no profesores universitarios. No aplica a Puntualo. Smoke test contra los 3 profesores FISI **no ejecutado** porque la fuente no cubre el universo.

**Evidencia:** [citas del sitio cppe.org.pe que confirman su alcance EBR].

**Rol en pipeline:** descartar.
```

Saltar al Step 9.5.

- [ ] **Step 9.3: Si CPPe SÍ incluye universitarios, intentar buscar los 3 profesores**

Identificar buscador (puede no haber buscador público; en ese caso la fuente es de uso interno y se descarta para automatización).

- [ ] **Step 9.4: Ejecutar smoke test si aplica**

- [ ] **Step 9.5: Escribir sección 4.4 del informe**

Plantilla del Step 5.1 B. Si la fuente se descartó en 9.2, escribir solo un párrafo explicando por qué + la tabla con "Rol en pipeline: descartar".

---

## Task 10: Investigar fuente — ORCID Public API

**Files:**
- Create: `docs/research/_raw/smoke-test-orcid.md`
- Modify: `docs/research/2026-05-11-professor-validation-sources.md` (sección 4.5)

- [ ] **Step 10.1: Revisar docs ORCID Public API**

ORCID Public API: `https://pub.orcid.org/v3.0/`. Sin auth para queries básicas (token público disponible para mayor rate limit). Rate limit: ~24 req/s sin token, mucho más con token.

Registrar en `_raw/smoke-test-orcid.md`: endpoint base, rate limit, ToS link, sin necesidad de Tavily.

- [ ] **Step 10.2: Buscar cada profesor por nombre completo**

Endpoint: `https://pub.orcid.org/v3.0/search?q=given-names:<NOMBRES>+AND+family-name:<APELLIDOS>+AND+affiliation-org-name:"Universidad+Nacional+Mayor+de+San+Marcos"`

Run para cada profesor:
```bash
curl -sSL -H "Accept: application/json" \
  'https://pub.orcid.org/v3.0/search?q=given-names:Juan+AND+family-name:Perez+AND+affiliation-org-name:%22Universidad+Nacional+Mayor+de+San+Marcos%22' \
  -o /tmp/orcid-prof-N.json
sleep 1
```

- [ ] **Step 10.3: Si encuentra hit, descargar el registro completo**

Run: `curl -sSL -H "Accept: application/json" "https://pub.orcid.org/v3.0/<orcid-id>/record" -o /tmp/orcid-record-N.json`

Campos típicamente útiles: `works` (publicaciones), `employments` (afiliaciones con fechas), `educations`, `biography`.

- [ ] **Step 10.4: Inventariar campos disponibles**

- [ ] **Step 10.5: Escribir `_raw/smoke-test-orcid.md`**

- [ ] **Step 10.6: Escribir sección 4.5 del informe**

Esperado: ORCID = enrichment grade A si el profesor tiene ORCID; cobertura baja porque ORCID es opt-in. Rol en pipeline: **enrichment**.

---

## Task 11: Investigar fuente — OpenAlex API

**Files:**
- Create: `docs/research/_raw/smoke-test-openalex.md`
- Modify: `docs/research/2026-05-11-professor-validation-sources.md` (sección 4.6)

- [ ] **Step 11.1: Revisar docs OpenAlex**

OpenAlex: `https://api.openalex.org/`. Sin auth, recomendado pasar email en User-Agent para mejor servicio ("polite pool"). Rate limit: 100 000 req/día (más que suficiente).

- [ ] **Step 11.2: Buscar la institución UNMSM en OpenAlex**

Run:
```bash
curl -sSL "https://api.openalex.org/institutions?search=Universidad+Nacional+Mayor+de+San+Marcos" \
  -H "User-Agent: Puntualo-Research/1.0 (mailto:mathias.torres@unmsm.edu.pe)" \
  | head -200
```

Extraer el `id` de institución (algo como `https://openalex.org/I...`).

- [ ] **Step 11.3: Buscar cada profesor del smoke test**

```bash
curl -sSL "https://api.openalex.org/authors?search=<Nombre+Completo>&filter=last_known_institution.id:I<UNMSM-ID>" \
  -H "User-Agent: Puntualo-Research/1.0 (mailto:mathias.torres@unmsm.edu.pe)"
sleep 1
```

- [ ] **Step 11.4: Para cada hit, registrar campos**

OpenAlex devuelve: `id`, `orcid`, `display_name`, `last_known_institution`, `affiliations[]` (con dates), `works_count`, `cited_by_count`, `concepts[]` (areas de investigación).

- [ ] **Step 11.5: Escribir `_raw/smoke-test-openalex.md`**

- [ ] **Step 11.6: Escribir sección 4.6 del informe**

Esperado: OpenAlex = enrichment grado A (afiliación + métricas) y posible **validation grado B** (si OpenAlex marca UNMSM como `last_known_institution`, eso confirma afiliación con limitaciones de freshness).

---

## Task 12: Investigar fuente — Semantic Scholar API

**Files:**
- Create: `docs/research/_raw/smoke-test-semanticscholar.md`
- Modify: `docs/research/2026-05-11-professor-validation-sources.md` (sección 4.7)

- [ ] **Step 12.1: Revisar docs Semantic Scholar Academic Graph API**

Base: `https://api.semanticscholar.org/graph/v1/`. Sin auth: rate limit 100 req/5 min. Con API key gratis: 1 req/s sostenido.

- [ ] **Step 12.2: Buscar cada profesor**

Run:
```bash
curl -sSL "https://api.semanticscholar.org/graph/v1/author/search?query=<Nombre+Completo>&fields=name,affiliations,papers.year,paperCount,citationCount"
sleep 3   # respetar rate limit
```

- [ ] **Step 12.3: Filtrar manualmente por afiliación UNMSM**

Semantic Scholar no permite filtrar por institución directamente en la query, así que pueden venir homónimos. Documentar la calidad del matching.

- [ ] **Step 12.4: Escribir `_raw/smoke-test-semanticscholar.md`**

- [ ] **Step 12.5: Escribir sección 4.7 del informe**

Esperado: enrichment grado B (similar a OpenAlex pero con peor filtrado por afiliación). Probable rol: **enrichment complementario** (no como source único).

---

## Task 13: Evaluar viabilidad — Google Scholar

**Files:**
- Create: `docs/research/_raw/smoke-test-googlescholar.md`
- Modify: `docs/research/2026-05-11-professor-validation-sources.md` (sección 4.8)

- [ ] **Step 13.1: Revisar ToS de Google Scholar**

Invocar `tavily-search`: `"Google Scholar terms of service automated access"` (max_results=3). Registrar quota.

Citar literalmente la cláusula contra scraping automatizado.

- [ ] **Step 13.2: NO ejecutar scraping. Evaluar como inviable o riesgosa**

Documentar el veredicto en `_raw/smoke-test-googlescholar.md`:

```markdown
# Evaluación de viabilidad — Google Scholar

**Acceso programático:** No hay API pública. ToS prohíbe scraping automatizado ("[cita literal]").

**Alternativas que sí cumplen ToS:**
- Que el profesor opt-in y comparta su Scholar Profile URL → almacenamos solo el URL público, NO scrapeamos.
- Datos académicos similares vía Semantic Scholar / OpenAlex (que sí permiten acceso programático).

**Rol en pipeline:** descartar para acceso automatizado. Permitido únicamente como link manual en la ficha del profesor (opt-in del propio profesor).

**Smoke test:** no ejecutado.
```

- [ ] **Step 13.3: Escribir sección 4.8 del informe**

Solo un párrafo explicando por qué se descarta + tabla con "Rol en pipeline: descartar (acceso manual opt-in OK)".

---

## Task 14: Investigar fuente — Tavily como fuente de enriquecimiento

**Files:**
- Create: `docs/research/_raw/smoke-test-tavily.md`
- Modify: `docs/research/2026-05-11-professor-validation-sources.md` (sección 4.9)

- [ ] **Step 14.1: Verificar cuota disponible**

Leer `_raw/tavily-quota-log.md`, sumar calls usadas hasta ahora. Si > 45 (de 50 hard cap), parar y consultar al usuario.

- [ ] **Step 14.2: Para cada uno de los 3 profesores, una query Tavily search**

Invocar skill `tavily-search` con query: `"<Nombre completo> UNMSM profesor"`, `max_results=5`. Registrar cada call en quota log.

- [ ] **Step 14.3: Para el profesor con mejores hits, un Tavily extract**

Invocar skill `tavily-extract` sobre la URL más prometedora (e.g., su perfil en una página académica). Registrar quota.

- [ ] **Step 14.4: Inventariar campos extraídos**

Tavily extract devuelve markdown estructurado del contenido. Listar qué fields se pueden extraer (foto URL, bio, publicaciones, etc.).

- [ ] **Step 14.5: Calcular costo en pipeline real**

Si en el smoke test se usaron 3 search + 1 extract = 4 calls para 3 profesores ≈ 1.3 calls/profesor. Con 1000 calls/mes → ~750 profesores enriquecibles/mes por Tavily. Documentar este cálculo en el informe.

- [ ] **Step 14.6: Escribir `_raw/smoke-test-tavily.md`**

- [ ] **Step 14.7: Escribir sección 4.9 del informe**

Esperado: Tavily = enrichment fallback grado B (cobertura amplia pero datos no estructurados, requiere parsing). Rol en pipeline: **enrichment de último recurso**, sujeto a budget.

---

## Task 15: Compilar matriz consolidada de smoke test

**Files:**
- Modify: `docs/research/2026-05-11-professor-validation-sources.md` (sección 5)

- [ ] **Step 15.1: Construir tabla `profesor × fuente`**

Reemplazar la sección 5 del informe con esta plantilla (rellenada con datos reales de cada `_raw/smoke-test-*.md`):

```markdown
## 5. Smoke test results — matriz consolidada

Leyenda: ✅ encontrado con afiliación UNMSM confirmada · ⚠️ encontrado pero ambiguo o sin afiliación clara · ❌ no encontrado · — no aplica.

| Fuente | High-profile ({nombre}) | Medio ({nombre}) | Low-profile ({nombre}) |
|---|---|---|---|
| Directorio UNMSM | [✅/⚠️/❌] | [...] | [...] |
| SUNEDU | [...] | [...] | [...] |
| RENACYT | [...] | [...] | [...] |
| CPPe | — | — | — |
| ORCID | [...] | [...] | [...] |
| OpenAlex | [...] | [...] | [...] |
| Semantic Scholar | [...] | [...] | [...] |
| Google Scholar | — | — | — |
| Tavily | [...] | [...] | [...] |

### Lecturas de la matriz

- **Mejor cobertura validación:** [fuente que más ✅ obtuvo en validación].
- **Mejor cobertura enriquecimiento:** [fuente con más campos útiles].
- **Sorpresas:** [...].
- **Confirmaciones:** [...].
```

- [ ] **Step 15.2: Verificar consistencia con `_raw/` files**

Cada celda de la tabla debe poder rastrearse a un `_raw/smoke-test-*.md`. Si una celda dice ✅ pero el raw dice ❌, hay error — arreglar.

---

## Task 16: Decidir pipeline final y escribir recomendación

**Files:**
- Modify: `docs/research/2026-05-11-professor-validation-sources.md` (sección 6)

- [ ] **Step 16.1: Ordenar las fuentes de validación por evidencia**

Criterio: cobertura del smoke test (más ✅ en validación) + estabilidad de acceso (API > scraping estable > scraping frágil). Excluir fuentes descartadas (CPPe, Google Scholar).

- [ ] **Step 16.2: Ordenar las fuentes de enriquecimiento**

Criterio: riqueza de campos + costo (gratis sin cuota > free tier con cuota).

- [ ] **Step 16.3: Escribir sección 6 con pipeline final**

Plantilla:

```markdown
## 6. Pipeline recomendado

Implementación del Enfoque 2 (pipeline jerárquico) definido en la spec. Orden de fuentes basado en evidencia del smoke test:

### Fase de validación (para apenas una confirme afiliación UNMSM)

1. **{Fuente #1}** — [justificación basada en cobertura smoke test + estabilidad].
2. **{Fuente #2}** — [...].
3. **{Fuente #3}** — [...].

### Fase de enriquecimiento (paralelizable, respetando rate limits)

1. **{Fuente A}** — campos: [...].
2. **{Fuente B}** — campos: [...].
3. **{Fuente C}** — campos: [...].
4. **Tavily** — solo si los anteriores no cubrieron campos clave (foto, bio narrativa). Sujeto a presupuesto mensual.

### Resolución de conflictos en enriquecimiento

Cuando dos fuentes discrepan en un mismo campo (ej. "departamento"):
- **Prioridad:** Directorio UNMSM > SUNEDU > otros.
- **Provenance siempre se preserva** en `ProfessorEvidence` (ver spec sección 5).

### Mapeo a la spec

| Source en pipeline | Clase concreta (futura) | Rol |
|---|---|---|
| {Fuente #1} | `UnmsmDirectorySource` | validation + enrichment |
| {Fuente #2} | `SuneduSource` | validation |
| ... | ... | ... |
```

---

## Task 17: Escribir TL;DR, riesgos y próximos pasos

**Files:**
- Modify: `docs/research/2026-05-11-professor-validation-sources.md` (secciones 1, 7, 8)

- [ ] **Step 17.1: Escribir sección 1 (TL;DR)**

Un solo párrafo de 4-6 oraciones que diga:
- Qué fuentes recomendadas como tier 1 para validación (las 2-3 mejores del smoke test).
- Qué fuente recomendada como núcleo de enriquecimiento.
- Si Tavily es necesario o se puede prescindir.
- Cuántas fuentes del scope inicial se descartaron y por qué (CPPe, Google Scholar).
- Si la arquitectura propuesta en la spec sigue válida o si la evidencia obligó a ajustarla.

- [ ] **Step 17.2: Escribir sección 7 (Riesgos y mitigaciones)**

Mínimo cubrir:

```markdown
## 7. Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| HTML del directorio UNMSM cambia y rompe scraper | Alta | Medio | Tests smoke `@pytest.mark.smoke` corridos manualmente al sospechar drift; alerta crítica al detectar parse error |
| SUNEDU agrega captcha al portal | Media | Alto | Fallback a tier 2 (RENACYT + OpenAlex). Plan B: validación manual por admin |
| Profesor con nombre común (homónimos) | Alta | Medio | Cross-check entre 2+ fuentes; si solo 1 confirma, marcar `validated_with_ambiguity` |
| Tavily cambia free tier o cierra | Baja | Bajo (no es validation core) | Pipeline sigue funcionando sin Tavily; perdemos solo enriquecimiento "best effort" |
| ToS de alguna fuente cambia y prohíbe scraping | Media | Alto si es tier 1 | Monitorear ToS trimestralmente; tener fallback documentado |
```

Añadir riesgos específicos descubiertos durante el smoke test.

- [ ] **Step 17.3: Escribir sección 8 (Próximos pasos)**

```markdown
## 8. Próximos pasos

1. **Aprobación del informe** por el equipo Puntualo.
2. **Redactar `PLAN_TAREA_2_4_v2.md`** que reemplace al actual, con la arquitectura del pipeline aterrizada a las fuentes finales que este informe valida.
3. **Decidir migración** del trabajo ya hecho en el plan 2.4 actual: ¿qué partes (Celery scaffolding, Redis cache, circuit breaker pattern) son reusables tal cual? Spoiler: la mayoría sí, solo cambia el conjunto de sources.
4. **Crear modelo `ProfessorEvidence`** (migración Alembic) — pendiente para el plan v2.
5. **Implementar `ProfessorValidationPipeline`** + sources tier 1 primero, luego tier 2.
6. **Implementar `BudgetTracker`** para Tavily con tests específicos del hard cap.
```

---

## Task 18: Self-review del informe

**Files:** ninguno (verificación).

- [ ] **Step 18.1: Buscar placeholders olvidados**

Run: `grep -n "_Pendiente_\|TBD\|TODO\|FIXME" docs/research/2026-05-11-professor-validation-sources.md`
Expected: NO outputs. Si aparece algo, completarlo o explicar por qué quedó así.

- [ ] **Step 18.2: Verificar cobertura de cada fuente del scope**

Run: `grep -E "^### 4\." docs/research/2026-05-11-professor-validation-sources.md`
Expected: 9 subsecciones (4.1 a 4.9). Si falta alguna, completarla.

- [ ] **Step 18.3: Verificar coherencia entre matriz (sección 5) y pipeline (sección 6)**

Las fuentes top del pipeline (sección 6) deben ser exactamente las que más ✅ tienen en la matriz (sección 5). Si no, justificar la divergencia explícitamente en sección 6.

- [ ] **Step 18.4: Verificar quota Tavily final**

Run: `cat docs/research/_raw/tavily-quota-log.md | wc -l`
Expected: número de calls ≤ 50.

Si > 50, NO HEMOS RESPETADO EL HARD CAP. Marcar como incidente y notificar al usuario.

- [ ] **Step 18.5: Lectura final corrida**

Leer el informe de arriba abajo. Verificar que el TL;DR es consistente con las secciones 5-6. Verificar que no hay contradicciones internas.

---

## Task 19: Handoff al usuario

**Files:** ninguno.

- [ ] **Step 19.1: Resumir entregables al usuario**

Mensaje al usuario con esta plantilla:

> "Informe completo en `docs/research/2026-05-11-professor-validation-sources.md`.
>
> Resumen de hallazgos:
> - [TL;DR del informe]
> - Cuota Tavily consumida: X/50 (de los 1000/mes free tier).
>
> Archivos generados:
> - `docs/research/2026-05-11-professor-validation-sources.md` (informe principal)
> - `docs/research/_raw/smoke-test-*.md` (raw por fuente)
> - `docs/research/_raw/fisi-directory-snapshot.html`
> - `docs/research/_raw/tavily-quota-log.md`
>
> Por favor revísalo. Cuando lo apruebes:
> - ¿Commiteo todo a git (informe + raws + spec)?
> - ¿Avanzamos a redactar `PLAN_TAREA_2_4_v2.md`?"

- [ ] **Step 19.2: Esperar respuesta del usuario**

NO hacer commit ni avanzar a siguiente fase sin aprobación explícita.

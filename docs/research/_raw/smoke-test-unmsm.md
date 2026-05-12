# Smoke test — Directorio docente UNMSM/FISI

**Fecha:** 2026-05-11
**Modo de acceso:** scraping HTML (un único HTML por departamento contiene la tabla completa de docentes; no hay fichas individuales en HTML).
**URLs base:**
- `https://sistemas.unmsm.edu.pe/site/docentes/directorio` — índice de departamentos.
- `https://sistemas.unmsm.edu.pe/site/docentes/directorio/directorio-dacc` — DACC (Ciencias de la Computación), 924 KB HTML.
- `https://sistemas.unmsm.edu.pe/site/docentes/directorio/directorio-daisw` — DAISW (Ingeniería de Software), 235 KB HTML.
- `https://sistemas.unmsm.edu.pe/posgrado/docentes/` — docentes de posgrado FISI, 913 KB HTML.
**Auth requerida:** no.
**Rate limit observado:** sin rate limit explícito; usado 1 req/s defensivo.
**robots.txt / ToS:**
- `unmsm.edu.pe/robots.txt`: `User-agent: *` con `Allow: /`. Solo restringe `/nogooglebot/` a Googlebot. Scraping permitido para User-Agents normales.
- `sistemas.unmsm.edu.pe/robots.txt`: 404 (default: permisivo).

## Estructura de los datos

El HTML contiene una sucesión de tablas, **una por semestre académico**. Semestres listados en DACC y DAISW: 2019-I, 2019-II, 2020-I, 2020-II, 2021-I, 2021-II, 2022-I, **2024-I** (último). Faltan 2022-II, 2023-I, 2023-II (gap de ~2 años en la mitad del histórico).

Columnas en cada tabla:
- NRO
- APELLIDOS Y NOMBRES (formato típico: `APELLIDO1 APELLIDO2, Nombres`)
- CAT (Principal / Asociado / Auxiliar / Jefe de Práctica)
- CLASE (T.C. tiempo completo / T.P. tiempo parcial / D.E. dedicación exclusiva + horas: 20/40)
- HOJA DE VIDA (link a PDF si existe; no todos los docentes lo tienen)
- PREGRADO (X si dicta)
- POSGRADO (X si dicta)
- CORREO (email institucional o personal)

**No están en el HTML:** foto, ORCID, líneas de investigación, fecha de ingreso/cese, grado académico (excepto en la lista de posgrado donde aparece como prefijo "Dr./Mg./Mtro.").

## Profesor 1 (high-profile): Ciro Rodriguez Rodriguez

- **Encontrado:** ✅ en lista de posgrado como **"Dr. Ciro Rodríguez Rodríguez"**.
- **NO está** en DACC ni DAISW 2024-I (pregrado). Sí estaba en DAISW 2019-I como Principal T.C. 40.
- **Hoja de Vida PDF:** `/site/images/pdf/Hoja_de_vida_Ciro_Rodriguez.pdf` (link al CV referenciado en 2019-I; sigue disponible).
- **Email:** `crodriguezro@unmsm.edu.pe` (de 2019-I).
- **Match dudoso/homónimos:** ninguno detectado en el directorio FISI.
- **Inconsistencia de formato:** pregrado lo lista sin tildes (`RODRIGUEZ RODRIGUEZ CIRO`), posgrado lo lista con tildes y prefijo (`Dr. Ciro Rodríguez Rodríguez`). Esto importa para normalización de nombres antes de matching.
- **Tiempo de respuesta:** N/A (es una página estática de ~900 KB; descarga total <1s).
- **Notas:** la ausencia en pregrado 2024-I + presencia en posgrado activa sugiere que migró a dedicación exclusiva en posgrado. La fuente NO marca explícitamente "activo en 2026" — la inferencia depende de la presencia en la última tabla disponible.

## Profesor 2 (medio): Lenis Rossi Wong Portillo

- **Encontrado:** ✅ en DAISW 2024-I como **"WONG PORTILLO, Lenis Rossi"**, categoría Asociada T.C. 40.
- **Hoja de Vida PDF:** `/site/images/archivos/Lenis_Wong.pdf` (referenciado en tablas previas; presumiblemente sigue válido).
- **Email:** `lwongp@unmsm.edu.pe`.
- **Match dudoso/homónimos:** ninguno; el apellido "Wong" combinado con "Portillo" es único en el directorio FISI.
- **Notas:** aparece tanto en DAISW (departamento) como dictando posgrado en algunas tablas. Es la docente con más continuidad cross-semester de mi muestra.

## Profesor 3 (low-profile): Adegundo Mario Camara Figueroa

- **Encontrado:** ✅ en DACC 2024-I como **"CAMARA FIGUEROA, Adegundo Mario"**, categoría Auxiliar (sin sufijo de clase visible en la última tabla; en 2019-I era Auxiliar T.P. 20).
- **Hoja de Vida PDF:** `/site/images/archivos/Mario_Camara.pdf` (nombre del archivo usa "Mario_Camara" en lugar del nombre completo, indica que el portal abrevia).
- **Email:** `adegundo.camara@unmsm.edu.pe`.
- **Match dudoso/homónimos:** ninguno; nombre extremadamente inusual.
- **Notas:** sorpresa positiva — la fuente cubre incluso al low-profile. La hipótesis del plan era que un Auxiliar T.P. podría no aparecer, pero sí aparece (con CV inclusive).

## Conclusión

- **Cobertura UNMSM:** **Alta** (los 3 perfiles encontrados — high en posgrado, medio y low en pregrado). Cobertura **completa** para docentes ordinarios FISI.
- **Tipo de afiliación:** **explícita** (la URL del HTML ya implica afiliación a UNMSM/FISI; la categoría confirma rol docente).
- **Rol en pipeline:** **validation + enrichment** (validación = "aparece en el HTML del departamento"; enrichment = categoría, dedicación, email, link a CV).
- **Riesgo principal:** **freshness**. La última tabla es 2024-I (~2 años stale a la fecha del informe 2026-05-11). Profesores que ingresaron o cesaron después de 2024-I no se reflejan. Mitigación: cross-check con SUNEDU (que tiene actualización oficial).
- **Riesgo secundario:** estructura HTML inconsistente entre semestres (algunas tablas tienen `<td style="text-align: left">`, otras `<td>`); el scraper debe ser tolerante a variaciones.
- **Riesgo terciario:** profesores activos en posgrado pueden no aparecer en listas DACC/DAISW pregrado. Hay que scrapear AMBAS URLs (`/site/docentes/directorio/directorio-{dacc,daisw}` Y `/posgrado/docentes/`) para no perder cobertura como en el caso de Ciro Rodriguez.
- **Riesgo cuaternario:** inconsistencia de tildes entre listas (pregrado mayúsculas sin tilde, posgrado con tilde y prefijo de grado). Normalizar a NFKD + lowercase antes de matching.

## Decisión para pipeline

Este source ES el **tier 1 de validación** para profesores UNMSM. El scraper debe:
1. Descargar las 3 URLs principales (DACC, DAISW, posgrado).
2. Parsear la tabla del semestre MÁS RECIENTE de cada una (no todas — sería ruido histórico).
3. Construir un set de nombres normalizados activos.
4. Para validar un profesor candidato: normalizar su nombre → buscar coincidencia en el set.
5. Si encuentra → afiliación UNMSM confirmada + extraer email, categoría, CV link.

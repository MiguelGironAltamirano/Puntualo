# Smoke test — RENACYT (CONCYTEC)

**Fecha:** 2026-05-11
**Modo de acceso:** mixto. Portal de búsqueda Angular SPA + perfiles individuales scrapeables por ID vía CTI Vitae.
**URLs:**
- Frontend búsqueda: `https://renacyt.concytec.gob.pe/buscador-ui/#/registro/investigadores` (Angular SPA, ruta hash).
- Iframe parent: `https://servicio-renacyt.concytec.gob.pe/busqueda-de-investigadores/`.
- Perfil individual scrapeable: `https://ctivitae.concytec.gob.pe/appDirectorioCTI/VerDatosInvestigador.do?id_investigador={N}` (HTML estable de ~335 KB).
- Backend Angular: `https://ctivitae.concytec.gob.pe/renacyt-backend-v1` (Payara/Spring; endpoints internos no documentados públicamente).
- Datos abiertos page: `https://servicio-renacyt.concytec.gob.pe/datosrenacyt/` (informativa, sin descargas directas).

**Auth requerida:** no para el frontend público. El endpoint de búsqueda interno `DirectorioCTI.do?tipo=datosinvestigador` requiere sesión activa (`"Su sesión ha caducado"`).
**robots.txt:** `servicio-renacyt.concytec.gob.pe/robots.txt` retorna `User-agent: * Disallow:` (vacío = permite todo).
**ToS:** datos públicos del Estado peruano; no restringe acceso automatizado documentadamente.

## Estructura de datos disponibles

Al acceder a un perfil individual por ID (ejemplo verificado: ID 50680), CTI Vitae devuelve HTML de ~335 KB con campos:

- Nombres y apellidos
- Tipo y nro. de documento (parcial / redacted en versión pública)
- Sexo, fecha y país de nacimiento
- País de nacionalidad
- Idiomas
- Datos académicos (grados, universidades emisoras)
- **Experiencia laboral** (institución, cargo, fechas) — confirma afiliación UNMSM si aparece
- **Experiencia como asesor de tesis** — muy útil para enriquecimiento académico
- Publicaciones científicas (artículos, libros, capítulos)
- Líneas de investigación
- Categoría RENACYT (Nivel I-V o Carlos Monge / María Rostworowski) — solo investigadores calificados

## Profesor 1 (high-profile): Ciro Rodriguez Rodriguez

- **Smoke test ejecutable:** ⚠️ parcial. No se pudo buscar por nombre programáticamente (requiere sesión web o reverse-engineering del Angular). Si supiéramos su ID, el perfil sería accesible.
- **Probabilidad de estar registrado:** **alta**. Categoría docente Principal T.C. + doctorado (visto como "Dr." en posgrado UNMSM) sugieren que está en RENACYT. La población típica de RENACYT incluye casi todos los Principales con grado de doctor de universidades nacionales.
- **Hallazgo en perfil ejemplo (ID 50680):** se confirma afiliación a UNMSM en el campo "Experiencia laboral" cuando aplica — formato útil para nuestro pipeline.

## Profesor 2 (medio): Lenis Rossi Wong Portillo

- **Smoke test ejecutable:** ⚠️ parcial (mismo blocker).
- **Probabilidad de estar registrado:** **media**. Asociada T.C. con probable producción académica; puede o no haber tramitado calificación RENACYT.

## Profesor 3 (low-profile): Adegundo Mario Camara Figueroa

- **Smoke test ejecutable:** ⚠️ parcial.
- **Probabilidad de estar registrado:** **baja**. RENACYT requiere acreditar producción de investigación; un Auxiliar T.P. típicamente no califica.

## Por qué el smoke test queda como ⚠️ y no ❌

El portal RENACYT **existe**, **es legal de usar**, y **tiene datos estructurados ricos por perfil**. El bloqueo es operativo: la API de búsqueda no está expuesta directamente. Hay tres caminos viables para superarlo en la implementación real:

1. **Reverse-engineer del bundle Angular (chunks lazy-loaded)** para descubrir el endpoint REST exacto. Probablemente algo como `https://ctivitae.concytec.gob.pe/renacyt-backend-v1/investigadores/buscar?nombre=...`. Requiere ~1-2 horas de inspección con DevTools.
2. **Scraping de listados publicados por universidades.** Algunas (e.g. UPAO) publican su listado completo de investigadores RENACYT en una página HTML estática con columnas (ID, nombre, nivel, área). Si UNMSM-VRIP publicara uno similar, sería la solución más simple — un scrape inicial + ID resolution por nombre. UNMSM no publica este listado al día de la investigación.
3. **Vía API gob.pe Datos Abiertos:** existe un dataset de RENACYT en el catálogo Datos Abiertos del gobierno peruano. No verificado en este informe, pero conocido como recurso disponible.

## Conclusión

- **Cobertura UNMSM:** **Media**. Cubre solo investigadores formalmente registrados (estimado: bajo % de la planilla docente total UNMSM, pero >90% de los Principales y >50% de los Asociados con grado de doctor).
- **Tipo de afiliación:** **explícita** (campo "Experiencia laboral" en el perfil CTI Vitae).
- **Rol en pipeline:** **enrichment principal + validation parcial (tier 2)**. Es excelente para enriquecer datos académicos (publicaciones, líneas de investigación, nivel RENACYT) pero NO puede ser el único validator porque no cubre a auxiliares ni a docentes sin producción de investigación.
- **Veredicto smoke test:** ⚠️ ⚠️ ⚠️ (datos potencialmente disponibles para los 3 perfiles pero requiere desbloquear el search endpoint primero).
- **Riesgo principal:** dependencia de un endpoint no oficial-documentado. Cualquier rediseño de la API de CTI Vitae rompería el scraper. Mitigación: usar datos abiertos gob.pe como fuente primaria si está disponible.

## Decisión para pipeline

Tier 2 enrichment confirmado. Pasos para implementación:

1. **Etapa 1 (PoC):** descubrir el endpoint exacto del search del Angular `renacyt-backend-v1` (~2 h).
2. **Etapa 2 (production):** clase `RenacytSource` con caché agresiva (TTL 30 días, los niveles RENACYT cambian raro). Sin retry agresivo si el endpoint falla — log + skip; el pipeline sigue.
3. **Alternativa:** si Datos Abiertos gob.pe expone un dataset RENACYT actualizado, usarlo como source primario y olvidarse del scraping del SPA.

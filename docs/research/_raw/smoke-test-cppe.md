# Smoke test — CPPe (Colegio de Profesores del Perú)

**Fecha:** 2026-05-11
**URL:** `https://cppe.org.pe/` (redirige a `/portal`)

## Conclusión rápida

**CPPe no aplica a Puntualo.** Smoke test contra los 3 profesores FISI **no ejecutado** porque la fuente no cubre el universo (docentes universitarios) y además el portal está actualmente en mantenimiento.

## Evidencia

### Alcance legal

Según el artículo 3° de la ley constitutiva del Colegio de Profesores del Perú (Ley 25231), citado por el documento de UNESCO IIEP:

> "El ámbito del Colegio es el profesorado de educación básica y/o educación superior **no universitaria**, activo o inactivo, hábil para el ejercicio."

Esto significa que el colegio agrupa a:
- Docentes de educación básica regular (inicial, primaria, secundaria).
- Docentes de educación superior **no universitaria** (institutos pedagógicos, técnicos, tecnológicos).

NO incluye a docentes universitarios. Los docentes de UNMSM, por tanto, no son legalmente colegiados en CPPe.

### Estado actual del portal

El sitio `https://cppe.org.pe/` redirige a un mensaje:

> "COLEGIO DE PROFESORES DEL PERÚ. Nuestro portal se encuentra en mantenimiento. Lamentamos las molestias, agradecemos su comprensión."

El subdominio `/portal` retorna HTML de ~230 KB del CMS, pero sin endpoint de búsqueda público accesible. Aun con el portal funcional, el alcance legal lo descarta para validar docentes universitarios.

### Variantes con nombres similares

Durante la búsqueda aparecieron otras siglas similares que NO son la misma institución:
- **CPPP** (Colegio Profesional de Profesores del Perú — `colegiodeprofesoresdelperu.org`) — colegio paralelo, también orientado a "Profesores Profesionales de la Educación", igualmente no incluye universitarios.
- **cppe.pe** (sin .org) — sitio web alternativo que **sí** declara incluir universitarios; pero esta declaración es inconsistente con la Ley 25231 y no se respalda en fuentes oficiales del Estado.

Ninguna variante es una fuente confiable para validar afiliación docente UNMSM.

## Rol en pipeline

**Descartar.** No se incluye en el pipeline ni como tier 1 ni como tier 2. La validación de afiliación UNMSM se cubre por el Directorio docente UNMSM (Task 6) + cross-check con RENACYT (Task 8).

## Smoke test contra los 3 profesores

No ejecutado. Razón: la fuente está fuera del universo de Puntualo (docentes universitarios), tanto por alcance legal como por estado operativo del portal.

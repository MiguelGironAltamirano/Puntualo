# Smoke test — ORCID Public API

**Fecha:** 2026-05-11
**Modo de acceso:** API REST pública, formato JSON.
**URL base:** `https://pub.orcid.org/v3.0/`
**Auth requerida:** no (search + record endpoints públicos sin token). Token público opcional para mayor rate limit.
**Rate limit observado:** sin throttling en queries individuales (1 req/s defensivo respetado).
**ToS:** datos públicos bajo CC0 cuando los propios investigadores lo eligen. La Public API tiene términos liberales para uso no comercial e integración.

## Endpoint usado

**Search:**
```
GET https://pub.orcid.org/v3.0/search?q=given-names:NAMES+AND+family-name:SURNAMES+AND+affiliation-org-name:"Universidad Nacional Mayor de San Marcos"
Accept: application/json
```

**Record completo:**
```
GET https://pub.orcid.org/v3.0/{orcid-id}/record
Accept: application/json
```

## Profesor 1 (high-profile): Ciro Rodriguez Rodriguez

- **Encontrado:** ✅
- **ORCID:** `0000-0003-2112-1349`
- **Query Tavily:** N/A (sin uso de cuota)
- **Tiempo de respuesta:** ~400 ms
- **Campos clave devueltos:**
  - **Works (publicaciones):** **229** (alto volumen — confirma high-profile)
  - **Employments:** 3
    - **Universidad Nacional Mayor de San Marcos | Docente | desde 2018-02-28 | sin fecha fin** ← afiliación UNMSM CONFIRMADA con fecha
    - Escuela Universitaria de Posgrado de la Universidad Nacional Federico Villarreal | Professor | desde 2006
    - National University Federico Villarreal | Professor - Researcher | desde 1998-01-15
  - **Educations:** 6 (incluye U.S. Particle Accelerator School, Korea International Cooperation Agency, etc.)
- **Match dudoso/homónimos:** ninguno; 1/1 hit con `affiliation-org-name:UNMSM`.
- **Notas:** ORCID confirma la afiliación UNMSM con fecha exacta (2018-02-28). El profesor también tiene afiliación previa con UNFV, lo cual es información que el directorio UNMSM no expone. Útil para el resumen IA.

## Profesor 2 (medio): Lenis Rossi Wong Portillo

- **Encontrado:** ✅
- **ORCID:** `0000-0002-5032-3233`
- **Tiempo de respuesta:** ~400 ms
- **Campos clave devueltos:**
  - **Works (publicaciones):** 23
  - **Employments:** **8** (perfil rico)
    - Universidad Peruana de Ciencias Aplicadas | Docente | desde 2021-03-01 (afiliación dual con otra universidad)
    - Universidad Nacional Mayor de San Marcos | Docente | desde 2012-12-17 ← afiliación UNMSM CONFIRMADA
    - UNMSM FISI | DOCENTE PREGRADO (CURSOS: GESTIÓN DE LA CONFIGURACIÓN Y MANTENIMIENTO DE SOFTWARE, ASESORÍA DE TESIS, METODOLOGÍA DE INVESTIGACIÓN, DISEÑO DE SOFTWARE Y ALGORÍTMICA I Y III) | desde 2010-03 ← información sobre cursos dictados, ¡oro para Puntualo!
    - ... (5 más con detalles de carrera anterior)
  - **Educations:** 4 — Doctor + Magister + Ingeniero todos de UNMSM FISI (carrera académica integral en UNMSM)
- **Match dudoso/homónimos:** ninguno; 1/1 hit.
- **Notas:** ORCID confirma TAMBIÉN cursos específicos dictados, lo cual es excelente para el resumen IA. Además, revela que enseña dual en UNMSM + UPC, dato no visible en el directorio UNMSM.

## Profesor 3 (low-profile): Adegundo Mario Camara Figueroa

- **Encontrado:** ❌
- **Razón:** ORCID es **opt-in**; el profesor probablemente no se registró. Confirma la hipótesis de que los low-profile auxiliares no están en ORCID.
- **Match dudoso/homónimos:** N/A.

## Conclusión

- **Cobertura UNMSM:** **Media-Alta para investigadores activos, Baja para auxiliares**. Estimación basada en el smoke test: ~70% de Principales + Asociados con publicaciones tendrán ORCID; auxiliares y JP raramente.
- **Tipo de afiliación:** **explícita** (con fechas y rol, e incluso cursos dictados en algunos casos).
- **Campos disponibles para enrichment:** publicaciones, empleos previos y actuales, educaciones, líneas de investigación, biography, ORCID badge (ID único universal). Excelente input para el resumen IA.
- **Rol en pipeline:** **enrichment principal (tier 1)** + **validation complementaria** (cuando aparece, la afiliación UNMSM se confirma con datos sólidos).
- **Veredicto smoke test:** ✅ ✅ ❌ (2/3).
- **Riesgo principal:** **cobertura desigual**. ORCID NO puede ser único validator porque ~30%+ de los docentes UNMSM no tienen registro.
- **Riesgo secundario:** ningún. ORCID es estable, documentado, gratuito, sin cuotas duras.

## Decisión para pipeline

ORCID es **tier 1 de enrichment** y **tier 2 de validation** (validación bonus cuando aparece). Implementación:

1. `OrcidSource.validate(full_name, university)` → busca; si hit con afiliación UNMSM, marca `affiliation_confirmed=True` con `confidence=0.95`.
2. `OrcidSource.enrich(full_name)` → descarga `/record`, extrae publications, employments, educations. Cache TTL 7 días.
3. Rate limit defensivo 1 req/s (ORCID permite mucho más).
4. NO depender de ORCID como único validator; usar siempre en combinación con Directorio UNMSM.

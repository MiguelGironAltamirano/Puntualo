# Tavily quota log — informe profesores 2026-05-11

Hard cap durante el informe: 50 calls. Free tier mensual: 1000.

| # | Timestamp | Skill usada | Query / URL | Notas |
|---|-----------|-------------|-------------|-------|
| 1 | 2026-05-11 14:07 | search (REST API) | "Universidad Nacional Mayor de San Marcos FISI directorio docentes" | Smoke test Tavily access. Encontró 3 URLs `sistemas.unmsm.edu.pe`. |
| 2 | 2026-05-11 14:18 | search (REST API) | "SUNEDU consulta de docentes universitarios Perú portal oficial" | Búsqueda Task 7. Devolvió `gob.pe/sunedu` y `enlinea.sunedu.gob.pe` (genéricos), no la URL específica del registro docente. |
| 3 | 2026-05-11 14:20 | search advanced (REST API) | "SUNEDU registro nacional de docentes universidades Peru busqueda nombre" | Búsqueda Task 7 v2. Halló: SUNEDU Registro de Grados y Títulos (no docentes), noticia sobre convenio Sunedu-Concytec para "registro de docentes-investigadores". |
| 4 | 2026-05-11 14:25 | search advanced (REST API) | "SUNEDU datos abiertos docentes universitarios CSV dataset Peru" | Búsqueda Task 7 v3. Halló MEF PersonalSP dataset (planilla pública) + repo GitHub `jmcastagnetto/sunedu-licenciamiento`. |
| 5 | 2026-05-11 14:30 | search advanced (REST API) | "RENACYT CONCYTEC consulta investigadores Peru DINA portal" | Búsqueda Task 8. Halló portal oficial `servicio-renacyt.concytec.gob.pe/busqueda-de-investigadores/` + endpoint datos. |
| 6 | 2026-05-11 14:45 | search advanced (REST API) | "UNMSM investigadores RENACYT Rodriguez Wong San Marcos" | Búsqueda Task 8 v2. **Hallazgo crítico:** `ctivitae.concytec.gob.pe/appDirectorioCTI/VerDatosInvestigador.do?id_investigador=N` (CTIVITAE - DINA - URL scrapeable directa por ID de investigador). |
| 7 | 2026-05-11 14:55 | search basic (REST API) | "Colegio de Profesores del Perú alcance docentes universitarios o solo educacion basica regular" | Búsqueda Task 9. Confirmó scope CPPe legalmente limitado a "educación básica y/o educación superior NO universitaria" (Ley 25231, Art. 3). |
| 8 | 2026-05-11 15:25 | search basic (REST API) | "Google Scholar terms of service automated access scraping bots" | Búsqueda Task 13. Confirmó: GS ToS prohíbe automated access; no API pública; robots.txt restringe `/scholar`, `/search` y `/citations?*cstart=`. |
| 9 | 2026-05-11 15:35 | search basic (REST API) | "Ciro Rodriguez Rodriguez UNMSM profesor" | Task 14 smoke test. 5 hits incl. sciprofiles, posgrado CV PDF, **peru.misprofesores.com** (competidor Puntualo), academia.edu, Google Scholar profile. |
| 10 | 2026-05-11 15:36 | search basic (REST API) | "Lenis Wong Portillo UNMSM profesor" | Task 14 smoke test. 5 hits incl. MisProfesores, UNMSM CV PDF, lista de directivos, Facebook, YouTube. |
| 11 | 2026-05-11 15:37 | search basic (REST API) | "Adegundo Camara Figueroa UNMSM profesor" | Task 14 smoke test. 5 hits incl. SGD UNMSM admin, CV UNMSM PDF, ejemplo CV en Studocu, papers en CORE.ac.uk, directorio DACC. |
| 12 | 2026-05-11 15:40 | extract (REST API) | sciprofiles.com Ciro | **Falló** ("Failed to fetch url"). Sigue contando contra cuota. |
| 13 | 2026-05-11 15:41 | extract (REST API) | peru.misprofesores.com/Ciro | OK. 4195 chars markdown. Confirmó: UNMSM/FISI, calidad 4.8, 12 calificaciones, etiquetas estilo Puntualo. |

**Subtotal:** 13 calls de 50 hard cap (1000/mes free tier). Margen restante: 37.

# Smoke test — profesores FISI seleccionados

**Spec ref:** sección 4 del meta-diseño.
**Criterio:** 1 high-profile, 1 medio, 1 low-profile.

## Directorio fuente usado

URL: `https://sistemas.unmsm.edu.pe/site/docentes/directorio`
Subdirectorios usados: `directorio-dacc` y `directorio-daisw` (los dos departamentos académicos de FISI).
Fecha scraping: 2026-05-11.
Snapshot: `fisi-directory-snapshot.html` (53KB, índice), `fisi-dacc.html` (924KB), `fisi-daisw.html` (235KB).

**Nota sobre frescura:** la sección "DOCENTES" en el meta-tag del HTML referencia "SEMESTRE ACADÉMICO 2019-I/II". La fecha de la lista visible es 2019, pero el portal está activo. Es un riesgo conocido (freshness) que el informe documentará.

## Profesores elegidos

### 1. High-profile: Ciro Rodriguez Rodriguez

- **Categoría:** Principal T.C. 40 (la más alta de FISI; única Principal en DAISW).
- **Departamento:** Académico de Ingeniería de Software (DAISW).
- **Email institucional:** `crodriguezro@unmsm.edu.pe`.
- **Justificación:** categoría Principal Tiempo Completo es el rango docente más alto en universidades peruanas; típicamente implica grado de doctor, antigüedad e investigación activa. Si una fuente no lo encuentra, esa fuente tiene un problema serio de cobertura.
- **Riesgo de homónimo:** "Ciro Rodriguez Rodriguez" es un nombre relativamente común en Perú; la coincidencia de apellido paterno y materno (ambos "Rodriguez") es lo que lo hace identificable. Las fuentes deben distinguirlo de otros "Ciro Rodriguez" sin segundo apellido repetido.

### 2. Medio: Lenis Rossi Wong Portillo

- **Categoría:** Asociada T.C. 40.
- **Departamento:** Académico de Ingeniería de Software (DAISW).
- **Email institucional:** `lwongp@unmsm.edu.pe`.
- **Justificación:** categoría Asociado a Tiempo Completo representa el rango docente intermedio típico. Es docente ordinaria con cierta actividad académica esperable. El nombre es poco común (combinación de origen asiático con apellidos peruanos), lo que reduce el riesgo de homónimos.

### 3. Low-profile: Adegundo Mario Camara Figueroa

- **Categoría:** Auxiliar T.P. 20 (rango docente más bajo, dedicación tiempo parcial 20h).
- **Departamento:** Académico de Ciencias de la Computación (DACC).
- **Email institucional:** `adegundo.camara@unmsm.edu.pe`.
- **Justificación:** Auxiliar T.P. es la categoría docente más junior con la menor dedicación horaria. Por la categoría, es esperable poca o ninguna producción académica indexada. El nombre "Adegundo Mario" es extremadamente inusual en Perú, lo que **elimina el riesgo de homónimos** y permite medir cobertura sin ruido.

## Justificación de selección de FISI sobre otras facultades

La spec define FISI como facultad prioritaria. Se eligen profesores de ambos departamentos académicos (DACC y DAISW) para no sesgar por departamento. La presencia de un Principal, un Asociado y un Auxiliar permite medir cobertura por categoría docente.

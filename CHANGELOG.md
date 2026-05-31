# Changelog

Todos los cambios destacados de este proyecto se documentan en este archivo.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto adhiere (de forma laxa por ahora) a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Added
- **Polling condicional del estado de validación** en el listado `/teachers` y la ficha `/teachers/[id]`.
  El frontend re-consulta cada 5s mientras haya profesores en `pending_validation` visibles
  y se detiene automáticamente al resolverse todos (o tras un tope de 24 intentos ≈ 2 min).
  Sin gasto de API cuando no hay nada pendiente. Refetch silencioso (sin spinner) para no parpadear.
- **Asignación de cursos al registrar un profesor**. El modal de alta ahora incluye una sección
  "Cursos que dicta" con búsqueda en vivo (debounced 300 ms) sobre los cursos de la facultad
  elegida, chips removibles para los seleccionados y validación de mínimo 1 / máximo 10.
- **Cap de 10 cursos** en el payload de `POST /professors` (`course_ids: list[int]`, `min_length=1`,
  `max_length=10`). Inserción atómica: el profesor y sus filas en `professor_courses` se crean
  en la misma transacción; cualquier error revierte todo.
- Nuevos códigos de error en `POST /professors`:
  - `404 COURSES_NOT_FOUND` (incluye `ids` con los cursos faltantes en el detail).
  - `422 COURSE_WRONG_FACULTY` cuando algún curso no pertenece a la facultad indicada.
- Soporte para títulos académicos femeninos y otras variantes en el matcher de UNMSM
  (`Dra.`, `Mtra.`, `Mgr.`, `Lica.`, `Profa.`).
- Migration `a1b2c3d4e5f6_seed_fisi_courses` que agrega 15 cursos típicos de la carrera
  a la Facultad de Ingeniería de Sistemas e Informática (idempotente vía `ON CONFLICT DO NOTHING`).

### Changed
- `useProfessors` admite ahora un tercer parámetro opcional `PollOptions<T>` para polling
  condicional opt-in. Comportamiento default sin cambios — los consumidores existentes
  (`compare/page.tsx`) no se ven afectados.
- Ordenamiento real en el catálogo de profesores: el `<select>` "Ordenar por" del
  catálogo está cableado al backend (`sort_by`, `sort_order`) en lugar de ser cosmético.

### Fixed
- **TLS de `sistemas.unmsm.edu.pe`**: el servidor sirve una cadena de intermedios incompleta
  desde la renovación del 2026-02-06 (cert firmado por `Sectigo Public Server Authentication
  CA OV R36`, cadena vieja). Se introdujo `truststore` para que el cliente `httpx` del source
  UNMSM use el almacén del SO con AIA fetching; las demás fuentes (OpenAlex, ORCID, Tavily)
  siguen con verificación por defecto.
- `GET /courses` devolvía **500 Internal Server Error** cuando `sort_by != 'evaluation_count'`
  (el caso por defecto). Se desempaquetaba mal el `Row` de SQLAlchemy en
  `evaluations/routers/courses.py:102`. Bug pre-existente que bloqueaba todo el catálogo de cursos.
- `TeacherCatalog.tsx` rompía con `ReferenceError: sortBy is not defined`. Faltaba declarar
  el estado y eliminar un bloque duplicado de controles que quedó tras una refactorización a medias.
- El badge **VERIFICADO** nunca aparecía en el catálogo ni en la página de comparación porque
  comparaban `validation_status === 'verified'`. El backend emite `'validated'` — se corrigió
  en `TeacherCatalog.tsx` y `compare/page.tsx`.
- El modal de alta llamaba a `/universities` y `/universities/{id}/faculties` sin el prefijo
  `/catalogs/` que el backend espera desde el commit `2157fe2` → 404 → "No se pudieron cargar
  las universidades".
- Reemplazado el kwarg deprecado `regex=` por `pattern=` en `evaluations/routers/courses.py`
  y `evaluations/routers/evaluations.py` (FastAPI / Pydantic v2).
- El worker Celery fallaba con `ModuleNotFoundError: truststore` por desfase entre el `pip`
  del env mamba `puntualo` y el `pip` por defecto del shell. `truststore==0.10.4` quedó
  declarado explícitamente en `requirements.txt`.

### Documentation
- Se crea este `CHANGELOG.md` para registrar cambios destacados desde ahora.

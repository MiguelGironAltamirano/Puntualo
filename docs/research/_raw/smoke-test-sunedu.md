# Smoke test — SUNEDU (Superintendencia Nacional de Educación Superior Universitaria)

**Fecha:** 2026-05-11
**Modo de acceso:** scraping HTML / consulta web manual.
**Auth requerida:** no, pero los portales web requieren **resolver captcha**.
**Rate limit observado:** N/A (no se pudo ejecutar smoke test automatizado).
**ToS / robots.txt:** los portales SUNEDU son del Estado peruano, datos públicos. No hay restricción legal documentada contra el uso de datos, pero hay restricción técnica (captcha) que en la práctica prohíbe acceso automatizado.

## Portales SUNEDU evaluados

### 1. `https://enlinea.sunedu.gob.pe/verificainscripcion/`

- **Propósito:** Registro Nacional de Grados y Títulos. Permite verificar si una persona tiene un grado/título universitario inscrito en SUNEDU.
- **Limitación 1 (técnica):** la página carga un **Cloudflare Turnstile captcha** (`<script src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit">`). No hay endpoint REST público accesible sin resolver el captcha.
- **Limitación 2 (semántica):** valida **grados/títulos** (¿esta persona tiene un grado de Doctor?), **no afiliación docente actual** (¿esta persona enseña en UNMSM?). Una persona puede tener grado de SUNEDU sin enseñar en ninguna universidad, y una persona puede enseñar en UNMSM sin tener su título registrado todavía. Es la señal incorrecta para el caso de uso de Puntualo.

### 2. `https://talento.sunedu.gob.pe/`

- **Propósito:** ORH (Oficina de Recursos Humanos) — sistema interno de gestión de talento de SUNEDU. NO es un buscador público de docentes universitarios.
- **Limitación:** también incluye referencias a captcha. Acceso no automatizable.

### 3. `https://www.sunedu.gob.pe/registro-nacional-de-grados-y-titulos/`

- Página estática WordPress que linkea a `enlinea.sunedu.gob.pe/verificainscripcion`. No es un endpoint de consulta propio.

### 4. MEF Datos Abiertos — Personal del Sector Público (descubrimiento colateral)

- URL: `https://fs.datosabiertos.mef.gob.pe/datastorefiles/PERSONALSP_2022.csv`
- Tamaño: **603 MB**.
- **Limitación crítica:** el dataset está **agregado por grupo ocupacional/condición laboral**, NO individualizado. Cada fila representa un grupo (`CANTIDAD: 59`, `CANTIDAD: 6`...) con sus características de cargo y régimen. No hay nombres ni DNI. No sirve para validar a una persona específica, solo para estadísticas.
- Verificado leyendo cabecera + primeras 2 filas:
  ```
  "PERIODO","EJERCICIO","MES","NIVEL","CODIGO_SECTOR","SECTOR","CODIGO_PLIEGO","PLIEGO","UNIDAD_EJECUTORA",...,"DESC_CARGO_ESTRUCUTURAL","DESC_CONDICION_LABORAL",...,"CANTIDAD","ING_IMPONIBLE_PERM_MENSUAL",...
  "20220131","2022","01","GOBIERNO NACIONAL","26","DEFENSA","026","M. DE DEFENSA",...,"Tecnico de Segunda","Nombrado",...,"59",...
  ```

## Profesores del smoke test

**Smoke test NO ejecutado** contra los 3 profesores FISI. Razón:

- `verificainscripcion` requiere captcha resuelto manualmente — incompatible con un pipeline automatizado.
- Aunque se resolviera, la señal devuelta (grados y títulos) no es la que necesita Puntualo (afiliación docente actual).

Se podría ejecutar manualmente desde un navegador para los 3 profesores como verificación una sola vez, pero eso no aporta a la viabilidad de la fuente como source automatizado, que es lo que el informe necesita evaluar.

## Conclusión

- **Cobertura UNMSM:** **N/A** — la fuente cubre potencialmente a todos los graduados peruanos, pero no es accesible programáticamente.
- **Tipo de afiliación:** la fuente no expone afiliación docente; expone grados/títulos. Señal incorrecta para Puntualo.
- **Rol en pipeline:** **descartar para automatización**.
- **Posible uso manual:** un admin podría, ante un caso dudoso, consultar manualmente el portal y registrar el resultado como evidencia complementaria. Pero no es escalable.
- **Riesgo principal:** depender de SUNEDU para validación automatizada sería un dead-end técnico. Mejor enfocar la validación de afiliación UNMSM en el directorio UNMSM (Task 6) + cross-check con RENACYT u OpenAlex (Tasks 8, 11).

## Nota sobre el plan original (PLAN_TAREA_2_4.md)

El plan original `PLAN_TAREA_2_4.md` ya anticipaba esta situación:

> "SUNEDU no tiene API pública estable documentada al día de hoy. Confirmar con el equipo si:
> - se mockea con un endpoint HTTP local (`httpbin`/FastAPI dummy) para esta sprint, o
> - se scrapea con `BeautifulSoup` contra el portal público (más frágil)."

Este informe **descarta** ambas opciones: el captcha bloquea el scraping HTML, y mockear no entrega valor real. La recomendación final es **eliminar SUNEDU del pipeline** y reemplazarlo con la combinación Directorio UNMSM + RENACYT + OpenAlex.

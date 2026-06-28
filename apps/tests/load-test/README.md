# Prueba de carga — Puntualo (50 usuarios concurrentes)

Simula 50 usuarios anónimos navegando el contenido público del backend
desplegado en la VM de Oracle. **Solo lecturas (GET)**: no escribe en la BD
ni necesita credenciales.

Ubicación: `apps/tests/load-test/`

## Estructura

```
apps/tests/load-test/
├── locustfile.py        # definición de los usuarios virtuales y sus tareas
├── requirements.txt     # dependencia (locust) — NO borrar
├── README.md            # esta guía
├── ANALISIS.md          # informe de la última corrida (para presentar)
├── .gitignore           # versiona solo el reporte; ignora la data cruda
└── results/             # salidas de cada corrida
    ├── reporte.html         # ✅ se versiona (el reporte)
    ├── resultados_*.csv     # 🚫 ignorados por git (data cruda)
    └── .gitkeep
```

## 1. Instalar (usando el .venv del root, NO crear otro)

Este proyecto ya tiene un `.venv` en el root. Reutilízalo:

```bash
# desde el root del repo
source .venv/Scripts/activate          # Windows (bash)
pip install -r apps/tests/load-test/requirements.txt
```

## 2. Ejecutar

Siempre **desde la carpeta `apps/tests/load-test/`** para que las salidas
caigan en `results/`:

```bash
cd apps/tests/load-test
```

### Opción A — interfaz web (explorar en vivo)

```bash
locust -f locustfile.py --host https://puntualo.duckdns.org
```

Abre http://localhost:8089 y configura: **Users = 50**, **Ramp up = 5**.

### Opción B — headless + reporte (reproducible, para presentar)

```bash
locust -f locustfile.py \
  --host https://puntualo.duckdns.org \
  --users 50 --spawn-rate 5 --run-time 3m \
  --headless --html results/reporte.html --csv results/resultados
```

## 3. Cómo se guardan los registros

Locust escribe los resultados al terminar la corrida. Hay dos tipos:

| Archivo | Contenido | ¿Git? |
|---|---|---|
| `results/reporte.html` | Reporte visual autocontenido (gráficas + tablas). Es el entregable. | ✅ versionado |
| `results/resultados_stats.csv` | Métricas agregadas por endpoint (1 fila por ruta + total). | 🚫 ignorado |
| `results/resultados_stats_history.csv` | Serie temporal: una fila cada ~2 s con RPS/latencia/usuarios. Sirve para graficar la evolución. | 🚫 ignorado |
| `results/resultados_failures.csv` | Detalle de cada tipo de fallo y su frecuencia. | 🚫 ignorado |
| `results/resultados_exceptions.csv` | Excepciones de Python dentro del propio test (no del servidor). | 🚫 ignorado |

El prefijo lo decides tú con `--csv <prefijo>`; Locust le añade los sufijos
`_stats`, `_stats_history`, `_failures`, `_exceptions`.

**Por qué solo se versiona el HTML:** el `.gitignore` de esta carpeta hace
`results/*` (ignora todo) y luego `!results/reporte.html` (excepción). Así el
repo guarda el reporte presentable y no se llena de CSV crudos que cambian en
cada corrida. La data cruda queda local para análisis pero fuera de git.

## 4. Qué significa el reporte HTML

El `reporte.html` tiene estas secciones:

### Cabecera
- **Target host** — la URL probada (la VM).
- **Script** / **Start/End time** — qué corrió y cuándo.

### Request Statistics (tabla principal)
Una fila por endpoint + una fila **Aggregated** (todo junto):
- **Method / Name** — verbo HTTP y nombre lógico de la petición.
- **# Requests** — total de peticiones enviadas a esa ruta.
- **# Fails** — cuántas fallaron (status >= 400 o timeout).
- **Median (ms)** — latencia mediana (p50): la mitad fue más rápida que esto.
- **90%ile / 95%ile / 99%ile** — percentiles: el 90/95/99 % fue más rápido que
  ese valor. El **p95** es el indicador clave de "experiencia bajo carga".
- **Average / Min / Max (ms)** — promedio y extremos.
- **Average size (bytes)** — tamaño medio de la respuesta.
- **RPS (current)** — peticiones por segundo que sostuvo esa ruta.
- **Failures/s** — errores por segundo.

### Response Time Statistics
Misma idea pero enfocada solo en percentiles de latencia (p50…p100),
para ver la cola de respuestas lentas.

### Gráficas (charts)
- **Total Requests per Second** — línea verde = RPS exitosos; roja = fallos/s.
  Si el verde se aplana mientras suben usuarios → llegaste al techo.
- **Response Times (ms)** — curvas de p50 y p95 en el tiempo. Si suben y no
  bajan → saturación (peticiones encolándose).
- **Number of Users** — cuántos usuarios virtuales activos había (la rampa).
  Te permite correlacionar "a los N usuarios, la latencia se disparó".

### Failures / Exceptions
- **Failures** — tabla con cada error del servidor (p.ej. `500 ... /courses`)
  y cuántas veces ocurrió.
- **Exceptions** — errores en el propio script de Locust (idealmente vacío).

## Cómo leer si "aguanta"

| Métrica | Bien | Alerta |
|---|---|---|
| **Failures %** | < 1 % | > 1 % sostenido |
| **p95 latency** | estable | crece sin estabilizarse |
| **RPS** | sube con los usuarios | se aplana antes de los 50 |

## Notas

- El backend está detrás de Caddy con HTTPS; `http://` redirige (308) a
  `https://`. Usa siempre `--host https://puntualo.duckdns.org`.
- Si ves muchos 500/timeouts, el cuello suele ser el nº de workers de Uvicorn
  o el pool de conexiones a la BD, no Locust. Ver `ANALISIS.md`.

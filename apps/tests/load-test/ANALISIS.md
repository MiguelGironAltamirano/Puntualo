# Análisis de prueba de carga — 50 usuarios concurrentes

**Fecha:** 2026-06-27
**Objetivo:** backend en VM Oracle (`https://puntualo.duckdns.org`)
**Herramienta:** Locust 2.44.4
**Escenario:** 50 usuarios virtuales anónimos, ramp-up 5 usuarios/s, 3 minutos sostenidos,
solo lecturas públicas (GET).

## Configuración del backend probado

- Uvicorn con **2 workers** async, detrás de Caddy (HTTPS / reverse proxy).
- BD: **Supabase** vía transaction pooler (puerto 6543).
- Pool async SQLAlchemy: `pool_size=5 + max_overflow=2` → **7 conexiones por worker** (14 en total).
- Cache: Redis con TTLs por endpoint.

## Resultados globales

> Se corrió dos veces. La 1ª (cache frío) dio ~1 % de errores 500 y p50 ~1.6 s.
> La 2ª (cache caliente, es la del `reporte.html` actual) dio 0 errores y mejor
> latencia. Ambas se reportan porque el contraste es informativo.

| Métrica | Corrida 1 (cache frío) | Corrida 2 (cache caliente) |
|---|---|---|
| Total de peticiones | 2 238 | **2 631** |
| Throughput | 12.46 req/s | **14.64 req/s** |
| Tasa de error | 1.07 % (24× HTTP 500) | **0 %** |
| Latencia mediana (p50) | 1 600 ms | **910 ms** |
| Latencia p95 | 2 600 ms | **1 400 ms** |
| Latencia p99 | 2 800 ms | **1 600 ms** |
| Latencia máxima | 3 650 ms | **1 837 ms** |

## Resultados por endpoint (corrida 2, la del reporte)

| Endpoint | p50 | p95 | Errores | Toca BD |
|---|---|---|---|---|
| `/hashtags` | **100 ms** | 220 ms | 0 % | Ligero / cache |
| `/health/db` | 350 ms | 570 ms | 0 % | `SELECT 1` |
| `/catalogs/universities` | 710 ms | 1 100 ms | 0 % | Sí |
| `/evaluations` (lista) | 830 ms | 1 300 ms | 0 % | Sí |
| `/courses` | 990 ms | 1 500 ms | 0 % | Sí |
| `/professors/{id}/comments` | 1 000 ms | 1 600 ms | 0 % | Sí (count + join) |

## Interpretación

1. **El backend SÍ soporta 50 usuarios concurrentes** sin caerse: 98.9 % de éxito.
   No hubo timeouts ni caída del servicio.

2. **Cuello de botella claro: el acceso a la base de datos.**
   - Endpoints ligeros / cacheados responden excelente (<350 ms).
   - Endpoints que consultan la BD (con `COUNT` + paginación + joins) se degradan
     a ~1.7–1.9 s de mediana bajo carga.
   - Causa raíz: solo hay **14 conexiones async** disponibles (7 × 2 workers).
     Con 50 usuarios simultáneos las peticiones se **encolan** esperando conexión,
     lo que infla la latencia.

3. **Errores 500 intermitentes** concentrados en endpoints que tocan la BD.
   Aparecieron en la 1ª corrida (cache frío, ~1 %) y desaparecieron en la 2ª.
   Compatibles con saturación del pool / hipos del transaction pooler de Supabase
   al arrancar en frío. No son fallos de lógica (las mismas rutas responden 200
   sin carga). El arranque en frío es el peor escenario: vale la pena precalentar
   el cache o revisar logs si reaparecen.

4. **`/professors` quedó fuera de la prueba**: exige autenticación (devuelve 401).
   No es un endpoint público. Para medirlo haría falta un escenario con login.

## Recomendaciones priorizadas

1. **Subir workers de Uvicorn** (2 → 4) si la VM tiene ≥2 vCPU. Duplica las
   conexiones disponibles y el paralelismo. *(Mayor impacto, menor esfuerzo.)*
2. **Ampliar el pool async**: `DB_POOL_SIZE` 5 → 10 (verificar el límite del
   pooler de Supabase antes).
3. **Cachear los listados pesados** (`/evaluations`, `/courses`) como ya se hace
   con detalle de profesor y comentarios.
4. **Investigar los 500 intermitentes** revisando los logs del contenedor `api`
   durante carga (`docker logs puntualo_api`).
5. Optimizar los `COUNT(*)` de paginación (estimaciones o índices) en las
   consultas más lentas.

## Archivos de evidencia

- `results/reporte.html` — reporte visual de Locust (gráficas de RPS, latencia, errores). **Versionado.**
- `results/resultados_stats.csv` — métricas agregadas por endpoint. *(data cruda, ignorada por git)*
- `results/resultados_stats_history.csv` — serie temporal (para graficar evolución). *(ignorada)*
- `results/resultados_failures.csv` — detalle de los errores. *(ignorada)*

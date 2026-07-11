# 6. Demo en vivo

> **Responsable (WS-E):** Sevan · **Estado:** ⬜
> Ejecución en tiempo real de la suite o de un flujo representativo, mostrando
> **resultados reales** ante el jurado.

## 6.1 Qué demostrar (opciones, elegir 1–2)

| Opción | Muestra | Duración | Impacto |
|---|---|---|---|
| A. Suite pytest en vivo | `pytest` corriendo + verde + coverage | ~2 min | Alto (evidencia directa) |
| B. Pipeline CI/CD | Push → GitHub Actions verde + artefactos | ~3 min | Alto (CI/CD se valora) |
| C. Prueba de carga | Locust en vivo o reporte + gráficas | ~2 min | Medio-Alto (rendimiento) |
| D. Escaneo de seguridad | `pip-audit`/`bandit` en vivo | ~1 min | Medio |

**Recomendado:** A + B (o A + C si el CI no está listo).

## 6.2 Guión paso a paso (borrador — opción A)

1. Abrir terminal, `mamba activate puntualo`.
2. Mostrar estructura de `apps/backend/tests/` (unit/integración/smoke).
3. Ejecutar:
   ```bash
   pytest apps/backend/tests -v --cov=app --cov-report=term-missing
   ```
4. Señalar: n.º de pruebas, verde, % de cobertura.
5. Abrir `reports/coverage/index.html` (o el reporte de Locust).
6. Cerrar conectando con las métricas ([07](07_documentacion_y_metricas.md)).

## 6.3 Preparación (checklist previo)

- [ ] Entorno `puntualo` activo y dependencias instaladas
- [ ] Suite pasa localmente (ensayo completo hecho)
- [ ] Datos/fixtures listos
- [ ] Reportes pre-generados por si falla la ejecución en vivo
- [ ] Conexión / proyector probados

## 6.4 Plan B (si algo falla en vivo)

- Tener **capturas y reportes pre-generados** (coverage HTML, `reporte.html` de
  Locust, run verde de GitHub Actions) para mostrar sin ejecutar.
- Un video corto de respaldo de la suite corriendo.

## 6.5 Reparto de la demo

| Momento | Quién | Qué dice |
|---|---|---|
| Intro (30s) | WS-A | Contexto y qué se va a mostrar |
| Ejecución (2–3 min) | WS-C/E | Corre la suite / pipeline |
| Lectura de resultados | WS-E | Interpreta métricas |

## Entregable (DoD)

- [ ] Opción de demo elegida
- [ ] Guión ensayado al menos 1 vez completo
- [ ] Plan B con evidencias pre-generadas listo
- [ ] Reparto de roles en la demo definido

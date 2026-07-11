# 8. Conclusiones y mejoras

> **Responsable (WS-A):** Cicilis · **Estado:** ⬜
> Cómo la estrategia de pruebas **mejora la calidad** del sistema y **reduce los
> riesgos del negocio**.

## 8.1 Cómo la estrategia mejora la calidad (borrador)

- Se pasó de pruebas dispersas a una **estrategia por niveles y tipos priorizada
  por riesgo** (ISTQB / ISO 29119).
- Se cubren los **flujos críticos de negocio** (moderación, reportes, auth) con
  pruebas automatizadas.
- La **automatización + CI/CD** crea una red de regresión que protege ante cambios
  (paradoja del pesticida).
- La **seguridad** se incorpora al ciclo (OWASP + escaneos en pipeline = DevSecOps).

## 8.2 Riesgos de negocio reducidos (antes / después)

| Riesgo | Antes | Después de la estrategia |
|---|---|---|
| R1 Difamación | Moderación sin pruebas de regresión | Cubierta por unit+integración, regresión en CI |
| R3 IDOR / acceso | Sin verificación sistemática | Pruebas 401/403 + casos basados en riesgo |
| R6 Saturación BD | Desconocido | Medido (Locust) y con recomendaciones concretas |
| R7 Deps vulnerables | Sin control | Escaneo automático en cada PR |

## 8.3 Métricas que respaldan la conclusión

Referencia a [07](07_documentacion_y_metricas.md): SUS 87.5, 0% error bajo carga
(cache caliente), throughput 14.64 req/s, cobertura ⬜(medir).

## 8.4 Mejoras propuestas / trabajo futuro

1. Completar cobertura de módulos críticos al objetivo acordado.
2. Instalar runner e2e (Playwright) y cubrir flujos del estudiante.
3. Añadir pruebas de estrés (punto de quiebre) y DAST (OWASP ZAP).
4. Optimizar el pool de BD y precalentar cache (mitiga D1/D2).
5. Pruebas específicas de prompt injection para el chatbot.
6. Monitoreo/alertas de eventos de seguridad (OWASP A09).

## Entregable (DoD)

- [ ] §8.1 y §8.2 redactadas con datos reales
- [ ] Tabla antes/después cerrada
- [ ] Lista de mejoras priorizada
- [ ] 1 slide de cierre

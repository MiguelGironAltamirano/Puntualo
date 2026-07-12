# 3. Diseño de casos de prueba

> **Responsable (WS-B):** Tarqui · **Estado:** ⬜
> Casos formales con **técnicas de caja negra, caja blanca y basadas en riesgo**,
> con **entradas y resultado esperado**. Se apoya en el inventario de
> [PRUEBAS.md](PRUEBAS.md) y la matriz de riesgos de
> [05_riesgos_defectos_seguridad.md](05_riesgos_defectos_seguridad.md).

## 3.1 Formato de caso

`ID · Nivel · Técnica · Riesgo asociado · Precondición · Entrada · Pasos · Resultado esperado`

Los ID siguen: `CP-<módulo>-<n>` (ej. `CP-MOD-01`).

## 3.2 Casos de CAJA NEGRA

### Técnica: Partición de equivalencias — filtro de moderación
| ID | Entrada (comentario) | Clase | Resultado esperado |
|---|---|---|---|
| CP-MOD-01 | "Excelente profesor, explica muy bien" | Válido/limpio | `action = allow`, `spam_score < 0.4` |
| CP-MOD-02 | "Contáctame a hacker@evil.com" | Contiene email | `spam_score ≥ 0.1`, patrón `email` |
| CP-MOD-03 | "Visita https://scam.com" | Contiene URL | `spam_score ≥ 0.1`, patrón `url` |
| CP-MOD-04 | "GRAN PROFESOR!!!!!" | Mayúsculas/repetición | `action = allow`, `spam_score ≥ 0.25` |

### Técnica: Valores límite — rate limiter de reportes (máx = 3/h)
| ID | Reportes previos en ventana | Resultado esperado |
|---|---|---|
| CP-RL-01 | 0 | Permitido, `remaining = 2` |
| CP-RL-02 | 2 (límite − 1) | Permitido, `remaining = 0` |
| CP-RL-03 | 3 (límite) | **Bloqueado**, `allowed = false` |

### Técnica: Tabla de decisión — creación de reporte
| Regla | Rate OK | No abusador | Comentario existe | Resultado |
|---|---|---|---|---|
| R1 | Sí | Sí | Sí | Reporte creado |
| R2 | No | — | — | `ReportRateLimitError` |
| R3 | Sí | No | — | `ReportAbuseDetectedError` |
| R4 | Sí | Sí | No | `CommentNotFoundError` |

### Técnica: Transición de estados — ciclo de vida del comentario
| ID | Estado inicial | Evento | Estado esperado |
|---|---|---|---|
| CP-CMT-01 | (nuevo) | Pasa moderación | `PUBLISHED` |
| CP-CMT-02 | `PUBLISHED` | Score de reportes ≥ umbral | `HIDDEN_PENDING_REVIEW` |
| CP-CMT-03 | `HIDDEN_PENDING_REVIEW` | Admin aprueba/elimina | `PUBLISHED` / `REMOVED` |

### Técnica: Casos de API (caja negra)
| ID | Petición | Entrada | Resultado esperado |
|---|---|---|---|
| CP-API-01 | `GET /professors` sin token | — | `401` |
| CP-API-02 | `POST /login` credenciales válidas | email+pass ok | `200` + token |
| CP-API-03 | `POST /login` credenciales inválidas | pass incorrecto | `401` |
| CP-API-04 | `GET /evaluations?page=1&page_size=20` | paginación válida | `200` + ≤20 items |
| CP-API-05 | `GET /professors/{id}` inexistente | uuid random | `404` |

## 3.3 Casos de CAJA BLANCA

### Técnica: Cobertura de sentencias/ramas — `_calculate_weighted_score`
| ID | Estado interno | Camino ejercitado | Resultado esperado |
|---|---|---|---|
| CP-WB-01 | 1 reporte `hate_speech` (peso 2.0) | rama peso alto | score = 2.0 |
| CP-WB-02 | `hate_speech` + `spam` (2.0+0.5) | acumulación | score = 2.5 |
| CP-WB-03 | 0 reportes | rama vacía | score = 0 |

### Técnica: Cobertura de decisiones — `heuristic_filter` (etapas)
| ID | Rama forzada | Entrada | Resultado esperado |
|---|---|---|---|
| CP-WB-04 | rama zero-width | texto con `​` | reason contiene "obfuscation"/"zero" |
| CP-WB-05 | rama sin DB (banned terms saltada) | término baneado | no bloquea (DB ausente) |
| CP-WB-06 | rama con DB (banned terms activa) | término baneado sembrado | eleva score / bloquea |

### Técnica: JWT (caja blanca de `core/security`)
| ID | Camino | Entrada | Resultado esperado |
|---|---|---|---|
| CP-SEC-01 | crear+verificar | payload válido | claims correctos |
| CP-SEC-02 | rama expiración | token vencido | error de credenciales |
| CP-SEC-03 | rama firma inválida | token alterado | rechazado |

## 3.4 Casos BASADOS EN RIESGO

Trazados a la matriz de riesgos ([05](05_riesgos_defectos_seguridad.md)).

| ID | Riesgo | Caso | Resultado esperado |
|---|---|---|---|
| CP-RB-01 | R1 difamación | Comentario tóxico dispara escalamiento | Comentario oculto para revisión |
| CP-RB-02 | R3 IDOR | Usuario A intenta operar recurso de B | `403`/`404`, sin fuga |
| CP-RB-03 | R5 prompt injection | Prompt "ignora instrucciones…" al chatbot | No ejecuta acción no autorizada |
| CP-RB-04 | R6 saturación BD | 50 usuarios concurrentes | Sin caída; p95 dentro de umbral |

## 3.5 Trazabilidad casos ↔ implementación

| Grupo de casos | Archivo de prueba |
|---|---|
| CP-MOD-* | `apps/backend/tests/unit/test_moderation.py` (+ `integration/test_moderation_db.py`) |
| CP-RL-* | `apps/backend/tests/unit/test_rate_limiter.py` |
| CP-CMT-*, tabla decisión | `apps/backend/tests/integration/test_report_service.py`, `test_comments_flow.py` |
| CP-API-* | `apps/backend/tests/integration/test_*_api.py` |
| CP-WB-*, CP-SEC-* | `unit/test_security.py`, `integration/test_report_service.py` |
| CP-RB-04 | `apps/tests/load-test/locustfile.py` |

## Entregable (DoD)

- [ ] Cada técnica de caja negra con ≥1 tabla de casos
- [ ] Caja blanca con casos trazados a caminos de código
- [ ] Casos basados en riesgo trazados a la matriz de riesgos
- [ ] Todos los casos con entrada y resultado esperado explícitos
- [ ] Trazabilidad caso ↔ archivo de prueba completa

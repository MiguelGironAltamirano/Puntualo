# 5. Análisis de riesgos, defectos y seguridad

> **Responsable (WS-D):** Mathias · **Estado:** 🟡
> Riesgos y defectos críticos + criterios de seguridad **OWASP / DevSecOps**
> pertinentes a Puntualo.

## 5.1 Matriz de riesgos

Escala: Probabilidad (B/M/A) × Impacto (B/M/A) → Prioridad.

| ID | Riesgo | Prob. | Impacto | Prioridad | Mitigación / prueba asociada |
|---|---|---|---|---|---|
| R1 | Comentario difamatorio sobre profesor real | M | A | **Alta** | Moderación + reportes + escalamiento (CP-MOD-*, CP-RB-01) |
| R2 | Abuso del sistema de reportes (brigading) | M | M | Media | Rate limiter + abuse detector (CP-RL-*) |
| R3 | Acceso no autorizado / IDOR | M | A | **Alta** | Control de acceso (CP-API-01, CP-RB-02) |
| R4 | Compromiso de credenciales / JWT | B | A | Media-Alta | `test_security`, `test_auth_api` (CP-SEC-*) |
| R5 | Prompt injection en el chatbot LLM | M | M | Media | Pruebas del orquestador/tools (CP-RB-03) |
| R6 | Saturación de BD bajo carga (pool 14 conns) | A | M | **Alta** | Prueba de carga (CP-RB-04) — hallazgo observado |
| R7 | Dependencias vulnerables | M | M | Media | `pip-audit` / `pnpm audit` en CI |
| R8 | Fuga de secretos en el repo | B | A | Media | Regla `.env.example` + `gitleaks` |
| R9 | Subida de archivos maliciosos | M | M | Media | Validación de uploads (por diseñar) |

## 5.2 Bitácora de defectos

Formato: `ID · Descripción · Origen · Severidad · Pasos · Esperado/Obtenido · Estado`.

| ID | Defecto | Origen | Severidad | Estado |
|---|---|---|---|---|
| D1 | 500s intermitentes (~1%) en endpoints de BD con cache frío | Locust corrida 1 (`ANALISIS.md`) | Media | Observado, causa raíz no cerrada |
| D2 | Degradación de latencia (p50 ~1.7s) por pool de 14 conexiones bajo 50 usuarios | Locust `ANALISIS.md` | Media | Documentado, recomendación pendiente |

> ⬜ **TODO:** conforme se ejecute la suite y los escaneos, registrar aquí los
> nuevos defectos con pasos reproducibles y trazarlos a un riesgo (R#).

## 5.3 OWASP Top 10 (2021) mapeado a Puntualo

| OWASP | Aplicación | Cómo lo cubrimos |
|---|---|---|
| A01 Broken Access Control | IDOR en comentarios/reportes, rutas admin | `test_access_control` (401/403) |
| A02 Cryptographic Failures | Hash de contraseña, secreto JWT | `test_security` |
| A03 Injection (SQL/LLM) | Consultas + **prompt injection** | ORM parametrizado; pruebas LLM |
| A04 Insecure Design | Moderación y rate limiting | Ya diseñados y probados |
| A05 Security Misconfiguration | CORS, headers, debug, `.env` | Revisión + `gitleaks` |
| A06 Vulnerable Components | deps Python/JS | `pip-audit`, `pnpm audit` |
| A07 Auth Failures | Fuerza bruta, expiración token | `test_auth_api` (+ verificar rate limit en login) |
| A08 Integrity Failures | Cadena de suministro CI | Pin de deps, escaneos |
| A09 Logging & Monitoring | Eventos de seguridad | ⬜ revisar qué se registra |
| A10 SSRF | Validación de profesores (fuentes externas) | ⬜ revisar `services/professor_validation/sources` |

## 5.4 OWASP LLM Top 10 (por el chatbot IA)

| LLM | Punto del sistema | Acción |
|---|---|---|
| LLM01 Prompt Injection | `services/chatbot/orchestrator.py`, `tools/` | Caso CP-RB-03 |
| LLM04 Model DoS / costos | `services/chatbot/rate_limit.py` | Verificar límites |
| LLM06 Divulgación de info sensible | salidas del chatbot | Revisión |
| LLM08 Agencia excesiva | herramientas invocables por el modelo | Revisión de permisos |

## 5.5 DevSecOps — herramientas ligeras (decidido)

| Herramienta | Objetivo | Comando | Evidencia |
|---|---|---|---|
| `pip-audit` | Vulns deps Python | `pip-audit -r apps/backend/requirements.txt` | ⬜ |
| `pnpm audit` | Vulns deps frontend | `pnpm audit` (en `apps/frontend`) | ⬜ |
| `gitleaks` | Escaneo de secretos | `gitleaks detect` | ⬜ |
| `bandit` | SAST básico Python | `bandit -r apps/backend/app` | ⬜ |

Todas se integran al job `security` del pipeline ([04 §4.4](04_automatizacion_y_cicd.md)).

> DAST (OWASP ZAP) queda como **trabajo futuro** (fuera del alcance elegido).

## Entregable (DoD)

- [ ] Matriz de riesgos revisada y priorizada por el equipo
- [ ] Bitácora de defectos con hallazgos reales (Locust + suite)
- [ ] Mapeo OWASP Top 10 + LLM Top 10 completo
- [ ] Escaneos ejecutados con evidencia archivada
- [ ] Puntos A09/A10 revisados en el código

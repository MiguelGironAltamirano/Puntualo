# 1. Presentación del sistema y alcance del proyecto

> **Responsable (WS-A):** Cicilis · **Estado:** ⬜
> **Objetivo del documento:** dar el contexto mínimo para que el jurado entienda
> qué es Puntualo antes de hablar de pruebas.

## 1.1 Ficha del sistema

| Campo | Valor |
|---|---|
| Nombre | **Puntualo** |
| Tipo | Plataforma web de evaluación de docentes universitarios |
| Backend | FastAPI (Python), SQLAlchemy async, Supabase (Postgres), Redis, Celery |
| Frontend | Next.js (React) |
| IA | Chatbot (Gemini/Cohere), moderación automática, validación de profesores, generación de resúmenes |
| Despliegue | Frontend en Vercel · Backend en VM Oracle (Caddy + Uvicorn) |

## 1.2 Objetivo del sistema

Permitir que estudiantes universitarios **consulten, evalúen y comenten** sobre
profesores reales (identificados por nombre), de forma **moderada y confiable**,
para apoyar la toma de decisiones al matricularse.

## 1.3 Usuarios (roles)

- **Estudiante** (rol principal): busca profesores, publica calificaciones y
  comentarios, compara docentes, reporta contenido, usa el chatbot.
- **Administrador / Moderador:** revisa reportes, gestiona contenido escalado,
  administra catálogos y términos baneados.
- **Sistema (agentes IA):** moderación automática, validación de profesores,
  generación de resúmenes.

## 1.4 Funcionalidades principales

1. **Evaluación de profesores** (calificación + comentario).
2. **Moderación automática** de comentarios (filtro heurístico + pipeline).
3. **Reportes de contenido** con rate limiting, detección de abuso y escalamiento.
4. **Búsqueda y comparador** de profesores.
5. **Chatbot con IA** para consultas sobre docentes.
6. **Validación automática de profesores** (fuentes externas).
7. **Catálogos** (universidades, facultades, cursos, hashtags).
8. **Autenticación** con correo universitario.

## 1.5 Alcance de las pruebas (qué SÍ / qué NO)

**Dentro del alcance:**
- Lógica de moderación, reportes y scoring (unit/integración).
- API pública y protegida (integración).
- Autenticación y control de acceso.
- Rendimiento de lectura bajo carga.
- Seguridad: OWASP Top 10 + LLM Top 10 (nivel documentado + escaneos ligeros).

**Fuera del alcance (por ahora):**
- Pruebas de estrés hasta punto de quiebre.
- DAST completo (OWASP ZAP).
- Cobertura exhaustiva del frontend (solo e2e de flujos clave si da tiempo).

## 1.6 Evolución respecto a la actividad integradora (semana 7)

> ⬜ **TODO (equipo):** completar. Puntos a cubrir:
> - Qué se propuso en la semana 7 y qué se implementó desde entonces.
> - Nuevas funcionalidades / módulos añadidos.
> - Qué madurez de calidad se agregó (esta estrategia de pruebas).

## 1.7 Diagrama de contexto

> ⬜ **TODO (equipo):** insertar diagrama (arquitectura o C4 nivel 1):
> Estudiante → Frontend (Next.js) → API (FastAPI) → {Postgres, Redis, LLMs}.

## Entregable (DoD)

- [ ] Ficha, objetivo, usuarios y funcionalidades revisados por el equipo
- [ ] Sección 1.6 (evolución semana 7) redactada
- [ ] Diagrama de contexto insertado
- [ ] 1 slide resumen para la expo

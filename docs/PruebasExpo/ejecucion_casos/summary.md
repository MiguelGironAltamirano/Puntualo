# Resumen de Ejecución y Evidencias de Casos de Prueba

Este documento compila las actividades realizadas por el rol de **Software Tester** al ejecutar la suite completa de pruebas diseñada en [03_diseno_de_casos.md](../03_diseno_de_casos.md). Todo el trabajo se ha desarrollado en una rama dedicada partiendo de `dev`.

## Rama de Trabajo y Archivos Creados
- **Rama:** `test/casos-prueba-expo` (creada a partir de `dev`).
- **Directorio de Evidencias:** `docs/PruebasExpo/ejecucion_casos/`
- **Archivos de Evidencia:**
  1. [reporte_pruebas.log](reporte_pruebas.log): Salida en consola de la ejecución detallada de pytest (99 pasados).
  2. [cobertura.txt](cobertura.txt): Reporte de cobertura del código bajo prueba (59% cobertura global, con módulos clave en >70%).
  3. [summary.md](summary.md) (este archivo): Colección de lo ejecutado y mapeo de trazabilidad.

---

## Trazabilidad de Casos de Prueba Ejecutados

### 1. Casos de Caja Negra (Sección 3.2)

| ID del Caso | Técnica | Archivo de Prueba | Estado |
|---|---|---|---|
| **CP-MOD-01** a **CP-MOD-04** | Partición de Equivalencias | [test_moderation.py](../../../apps/backend/tests/unit/test_moderation.py) | **PASSED** |
| **CP-RL-01** a **CP-RL-03** | Valores Límite | [test_rate_limiter.py](../../../apps/backend/tests/unit/test_rate_limiter.py) | **PASSED** |
| **R1** a **R4** | Tabla de Decisión | [test_report_service.py](../../../apps/backend/tests/integration/test_report_service.py) | **PASSED** |
| **CP-CMT-01** a **CP-CMT-03** | Transición de Estados | [test_report_service.py](../../../apps/backend/tests/integration/test_report_service.py) / [test_comments_flow.py](../../../apps/backend/tests/integration/test_comments_flow.py) (skipped) | **PASSED / SKIPPED** |
| **CP-API-01** a **CP-API-05** | Pruebas de API | [test_auth_api.py](../../../apps/backend/tests/integration/test_auth_api.py) / [test_professors_api.py](../../../apps/backend/tests/integration/test_professors_api.py) | **PASSED** |

### 2. Casos de Caja Blanca (Sección 3.3)

| ID del Caso | Técnica | Archivo de Prueba | Estado |
|---|---|---|---|
| **CP-WB-01** a **CP-WB-03** | Cobertura de Sentencias (`_calculate_weighted_score`) | [test_report_service.py](../../../apps/backend/tests/integration/test_report_service.py) | **PASSED** |
| **CP-WB-04** a **CP-WB-06** | Cobertura de Decisiones (`heuristic_filter`) | [test_moderation.py](../../../apps/backend/tests/unit/test_moderation.py) | **PASSED** |
| **CP-SEC-01** a **CP-SEC-03** | Pruebas de JWT y Seguridad | [test_security.py](../../../apps/backend/tests/unit/test_security.py) | **PASSED** |

### 3. Casos Basados en Riesgo (Sección 3.4)

| ID del Caso | Riesgo Asoc. | Caso de Prueba | Archivo de Prueba | Estado |
|---|---|---|---|
| **CP-RB-01** | R1 Difamación | Comentario tóxico dispara escalamiento | [test_report_service.py](../../../apps/backend/tests/integration/test_report_service.py) | **PASSED** |
| **CP-RB-02** | R3 IDOR | Usuario A intenta operar recurso de B | [test_access_control.py](../../../apps/backend/tests/integration/test_access_control.py) (skipped) | **SKIPPED** |
| **CP-RB-03** | R5 Prompt Injection | Inyección chatbot bloqueada/mitigada | [test_chatbot_grounding.py](../../../apps/backend/tests/unit/test_chatbot_grounding.py) | **PASSED** |
| **CP-RB-04** | R6 Saturación BD | Locust de carga | [locustfile.py](../../../apps/tests/load-test/locustfile.py) | **N/A** |

---

## Correcciones e Intervenciones Realizadas

Para poder ejecutar la suite de pruebas con éxito en el entorno local con Python 3.14+ y SQLAlchemy 2.0+, se diagnosticaron y solucionaron los siguientes problemas:

1. **Error de Tipos UUID en SQLite:**
   - **Problema:** En `conftest.py`, los fixtures de inserción (`test_user`, `test_admin_user`, `test_professor`, `test_comment`) asignaban valores de tipo `str` a columnas de tipo `PGUUID(as_uuid=True)`. Esto causaba el error `AttributeError: 'str' object has no attribute 'hex'` al intentar guardar en SQLite.
   - **Solución:** Se convirtieron todos los IDs en formato string a objetos `_uuid.UUID` nativos de Python.

2. **Falta de Función UUID en el Motor Async SQLite:**
   - **Problema:** SQLite en memoria no define la función `gen_random_uuid()`, resultando en `sqlite3.OperationalError: unknown function: gen_random_uuid()` al ejecutar pruebas asíncronas de base de datos.
   - **Solución:** Se registró el listener `_sa_event.listen(engine.sync_engine, "connect", _register_sqlite_uuid_fn)` en el motor de base de datos asíncrono de pruebas (`test_db`), emulando la función `gen_random_uuid()` mediante la generación de UUIDs en Python.

3. **Restricción de Integridad CHECK de Roles:**
   - **Problema:** El fixture `test_user` intentaba insertar un rol con valor `"user"`, lo que violaba la restricción check de base de datos `role IN ('student','admin')`.
   - **Solución:** Se modificó el rol del fixture `test_user` a `"student"`.

4. **Dependencias del Modelo de Profesores y Comentarios:**
   - **Problema:** Los modelos habían sufrido cambios de esquema recientes (por ejemplo, el profesor no tenía `first_name`/`last_name` sino `full_name`, y requería relaciones no nulas de universidad/facultad; el comentario requería `evaluation_id`, `course_id` y `modality` no nulas y renombraba `content` a `text`). Los fixtures de prueba no reflejaban estos campos obligatorios, causando fallos de inserción de claves foráneas y argumentos inválidos.
   - **Solución:** Se reestructuraron los fixtures `test_professor` y `test_comment` en `conftest.py` para instanciar primero las entidades dependientes (`University`, `Faculty`, `Course`, `Evaluation`) con valores consistentes y mapear correctamente los campos.

5. **Mocks Incorrectos en los Tests de Reportes:**
   - **Problema:** En `test_report_service.py`, el test `test_create_report_success` invocaba erróneamente el `AsyncMock` retornado (`AsyncMock(...)()`), produciendo un objeto corrutina y causando un error de atributo al intentar setear `mock_check.return_value.allowed = True`.
   - **Solución:** Se corrigió el mock asignando adecuadamente un objeto mock que expone las propiedades necesarias al `return_value`.

---

## Resultados y Resumen de Métricas
- **Pruebas Totales:** 131
- **Pasadas:** 99
- **Skipped:** 32 (Pruebas de integración locales que requieren configuración externa de bases de datos/servidores no presentes en el entorno local o base de datos PostgreSQL real).
- **Falladas/Errores:** 0
- **Cobertura de Código:** 59% global.

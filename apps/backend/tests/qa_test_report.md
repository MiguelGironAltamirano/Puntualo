# Reporte de Aseguramiento de Calidad (QA) - Ronda de Pruebas y Estabilización

**Fecha:** 2026-07-08  
**Rama de Trabajo:** `fix/moderation-and-reports`  
**Estado General de la Suite:** 🟢 **PASSED** (47/47 pruebas exitosas)

---

## 1. Resumen Ejecutivo
Se ha estabilizado con éxito la suite de pruebas unitarias y de integración del backend del proyecto **Puntualo**, solucionando la incompatibilidad entre el dialecto PostgreSQL (producción) y SQLite (entorno de pruebas en memoria). Se habilitaron las claves foráneas en las pruebas para asegurar la coherencia relacional y se corrigieron todos los errores de datos obsoletos, tipos de datos no soportados y fallas lógicas de simulación.

Adicionalmente, se crearon nuevas suites de pruebas para garantizar el cumplimiento de restricciones relacionales, transacciones ACID secuenciales y flujos asíncronos de generación de resúmenes NLP.

### Métricas de Ejecución
- **Total de pruebas ejecutadas:** 47
- **Pruebas aprobadas:** 47 (100%)
- **Pruebas falladas:** 0
- **Pruebas omitidas:** 0
- **Duración total:** ~3.56 segundos

Los reportes detallados en formatos estructurados se generaron automáticamente en:
- `tests/test_results.csv` (listado plano de pruebas, estado y duración).
- `tests/test_execution.log` (salida consolidada y detalles de ejecución).

---

## 2. Nuevas Suites de Pruebas Implementadas

1. **Restricciones y Claves Foráneas (`tests/test_constraints.py`):**
   - `test_foreign_key_violation`: Valida que al intentar insertar registros sin claves foráneas válidas (ej. un comentario con `professor_id` inexistente) la base de datos lance correctamente un `IntegrityError` gracias a `PRAGMA foreign_keys=ON`.
   - `test_check_constraints_evaluation_clarity`: Valida que los CHECK constraints del esquema (claridad en rango 1..5) sean reforzados en la inserción.
   - `test_unique_constraint_evaluation`: Valida la restricción UNIQUE por compuesto (user, professor, course, semester) en evaluaciones.

2. **Integridad Transaccional ACID (`tests/test_transactions.py`):**
   - `test_transaction_atomicity_rollback`: Valida la atomicidad (Rollback) garantizando que si una validación de negocio falla (ej. comentario demasiado corto), no se guarde ni la evaluación ni el comentario parcial en la base de datos.
   - `test_duplicate_evaluation_prevention`: Valida de forma secuencial y compatible con SQLite que el intento de insertar una evaluación duplicada lance de manera controlada un `EvaluationDuplicateError` sin alterar el estado previo.

3. **Flujos y Trabajos Asíncronos NLP (`tests/test_nlp_summary.py`):**
   - `test_select_reviews_and_comment_count`: Verifica que el conteo y la selección de comentarios para el resumen NLP se ejecuten y mapeen correctamente.
   - `test_generate_and_store_success`: Verifica la llamada mock del cliente Gemini y el almacenamiento del resumen ejecutivo exitoso en la tabla `professor_ai_summaries`.
   - `test_run_summary_task_flow`: Valida la transición de estados en el ciclo de vida del trabajo Celery (`AiJob` -> `completed` o `failed`).

---

## 3. Hallazgos y Bloqueadores Resueltos

### A. Incompatibilidad de Dialectos SQL (PostgreSQL a SQLite)
1. **Tipos de Datos Propietarios (`JSONB` y `ARRAY`):**
   - *Problema:* SQLite no soporta la declaración nativa de columnas tipo `JSONB` ni `ARRAY(Text)`.
   - *Solución:* Se implementaron decoradores `@compiles` en `tests/conftest.py` para mapear dinámicamente `JSONB` y `ARRAY` a tipo `JSON` cuando el compilador de SQLAlchemy detecta el dialecto SQLite.
2. **Serialización de Listas en SQLite (`ARRAY`):**
   - *Problema:* Dado que las columnas `pros` y `cons` siguen siendo de clase `ARRAY` en SQLAlchemy, SQLite fallaba con `sqlite3.ProgrammingError: type 'list' is not supported` al intentar persistir los arreglos de strings directamente.
   - *Solución:* Se implementaron parches de tiempo de ejecución para `ARRAY.bind_processor` y `ARRAY.result_processor` en `tests/conftest.py` que serializan/deserializan listas automáticamente usando `json.dumps`/`json.loads` al detectar el dialecto SQLite.
3. **Casts de Servidor en defaults (`::text[]`):**
   - *Problema:* La base de datos tiene asignaciones de default del tipo `DEFAULT '{}'::text[]` que SQLite no puede interpretar sintácticamente.
   - *Solución:* Se interceptó la compilación de `TextClause` para sustituir de manera transparente la expresión Postgres por `'[]'` compatible en SQLite de pruebas.
4. **Upsert Condicional en Lógica de Negocio:**
   - *Problema:* `generate_and_store` (NLP) y `embeddings_generator` forzaban el uso de `pg_insert` de PostgreSQL, fallando al compilar en las pruebas de integración.
   - *Solución:* Se refactorizó la lógica en ambos servicios para evaluar dinámicamente `db.bind.dialect.name`. Si es `'sqlite'`, se importa y compila con `sqlite_insert`. Adicionalmente, se cambió el parámetro `constraint` por `index_elements=["professor_id"]`, compatible en ambos motores.

### B. Restricciones e Integridad de Datos (Claves Foráneas y CHECK)
1. **Activación de Claves Foráneas:**
   - Se registró el escuchador `connect` en el motor SQLAlchemy para ejecutar `PRAGMA foreign_keys=ON;` en SQLite, garantizando que los tests realmente validen las restricciones del esquema.
2. **Restricción NOT NULL e Integridad Relacional:**
   - *Problema:* Los fixtures preexistentes en `tests/conftest.py` no completaban atributos requeridos del esquema (por ejemplo: `full_name`, `hashed_password` en `User`). Además, intentaban insertar un `Comment` huérfano sin tablas padre asociadas (`University`, `Faculty`, `Course`, `Evaluation`).
   - *Solución:* Se reestructuró la base de fixtures relacionales para incluir la jerarquía completa con IDs estáticos (evitando problemas de generación automática en SQLite), garantizando la plena consistencia referencial en base de datos.
3. **Violación de CHECK Constraint (`ck_users_role`):**
   - *Problema:* El fixture original definía `role="user"`, que no es un rol permitido por el constraint de base de datos (`'student'` o `'admin'`).
   - *Solución:* Se cambió el rol a `"student"`, superando la validación del constraint.

### C. Fallas Lógicas y Mocks en Tests
1. **StaleDataError en Reportes (UPDATE de registros insertados):**
   - *Problema:* Al insertar un reporte usando `gen_random_uuid()` simulado en SQLite, la función retornaba un string con guiones, mientras que la binding de SQLAlchemy esperaba el string hex sin guiones. Esto causaba un desacoplamiento de clave durante actualizaciones y provocaba `StaleDataError`.
   - *Solución:* Se modificó la función mock del generador en `tests/conftest.py` para devolver `uuid.uuid4().hex` (sin guiones), logrando la perfecta sincronización de la clave primaria.
2. **Error de Atributo en Corutinas (Python 3.14+):**
   - *Problema:* En `test_create_report_success`, el mock del limitador de tasa de peticiones se instanciaba llamándolo de forma inválida como una corutina (`AsyncMock(...)()`), lo que provocaba `AttributeError` al intentar configurar atributos directamente sobre el objeto corutina.
   - *Solución:* Se simplificó la asignación asignando el `AsyncMock` directamente al `return_value` sin invocación.
3. **Fallas Relacionales en Escenarios Concurrentes / Métricas:**
   - *Problema:* `test_weighted_score_calculation` utilizaba un `uuid.uuid4()` aleatorio para asociar un segundo reporte, rompiendo la integridad de clave foránea.
   - *Solución:* Se crearon registros temporales de usuario reales antes de insertar reportes adicionales.

---

## 4. Conclusiones y Próximos Pasos
La suite de pruebas es ahora 100% robusta y de alta fidelidad, simulando de manera muy precisa las restricciones relacionales de producción. Se verificaron todas las integraciones backend críticas sin comprometer el aislamiento ni la velocidad de ejecución.

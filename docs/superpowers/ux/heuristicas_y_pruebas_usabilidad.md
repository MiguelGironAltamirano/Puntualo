# Heurísticas de Nielsen y Pruebas de Usabilidad - Puntualo

**Método:** Evaluación Heurística basada en los 10 principios de usabilidad de Jakob Nielsen y Planificación de Pruebas de Usabilidad Empíricas.  
**Alcance:** Exclusivo para el rol de Estudiante.

---

## 1. Heurísticas de Nielsen

### 1.1. Visibilidad del estado del sistema
* **Estados de carga interactivos:** Al realizar búsquedas o aplicar filtros en el buscador de profesores, la interfaz muestra un esqueleto de carga (*skeleton screen*) y un indicador visual en movimiento para indicar que el sistema está procesando la consulta activa.
* **Confirmación de acciones:** Al enviar una calificación y reseña sobre un docente, se despliega una alerta verde confirmando que la reseña fue recibida y se encuentra en proceso de validación.
* **Indicadores en tiempo real:** Cuando el estudiante compara dos docentes en el comparador, las tarjetas de perfil muestran estados de carga individuales en paralelo hasta que se cargan todos los datos comparativos.

### 1.2. Relación entre el sistema y el mundo real
* **Lenguaje estudiantil natural:** La plataforma utiliza términos familiares del entorno universitario tales como "Profesor", "Curso", "Calificación", "Dificultad" y "Puntualidad" en lugar de identificadores técnicos o jerga interna del sistema.
* **Metáforas visuales claras:** Para calificar aspectos específicos del docente, se utiliza la escala de estrellas (1 a 5) y colores intuitivos (rojo para baja puntualidad, verde para alta puntualidad), facilitando la asociación con calificaciones reales.
* **Clasificación por dependencias:** La organización de las materias y docentes sigue la estructura organizativa típica de la universidad del estudiante (por ejemplo: Facultad de Ingeniería, Departamento de Ciencias Computacionales).

### 1.3. Control y libertad del usuario
* **Cancelación de procesos:** Durante el flujo de redacción de una calificación, se provee un botón visible de "Cancelar" que cierra el formulario modal y retorna al estudiante al perfil del profesor sin alterar su estado previo.
* **Edición ágil de entradas:** En el módulo de comparación de profesores, el estudiante puede remover fácilmente a cualquiera de los docentes seleccionados mediante un botón "Quitar" (icono de X) en la esquina superior de la columna de comparación.
* **Limpieza de filtros rápida:** En la pantalla de resultados de búsqueda, se incluye un botón "Limpiar todos los filtros" para que el usuario pueda reiniciar su búsqueda a su estado original con un solo clic.

### 1.4. Consistencia y estándares
* **Uniformidad de elementos:** Todos los botones de acción principal (como "Buscar" y "Enviar Calificación") y las escalas de puntuación mantienen los mismos colores, tipografías y bordes redondeados a lo largo de toda la interfaz.
* **Comportamiento estándar de componentes:** Los modales de la aplicación se pueden cerrar haciendo clic fuera del cuadro del diálogo o presionando la tecla *Escape*, cumpliendo con las convenciones estándar de aplicaciones web modernas.
* **Navegación predecible:** La barra de navegación superior mantiene exactamente el mismo orden de opciones ("Inicio", "Buscador", "Comparador") sin importar en qué pantalla o perfil de profesor se encuentre el estudiante.

### 1.5. Prevención de errores
* **Restricción de envíos vacíos:** El botón de "Publicar calificación" permanece deshabilitado hasta que el estudiante asigne puntuaciones obligatorias en cada métrica y complete el número mínimo de caracteres requerido para el comentario.
* **Sugerencias de búsqueda inteligente:** A medida que el estudiante escribe en el buscador de profesores, se despliega una lista de coincidencias exactas para evitar fallos por errores de ortografía.
* **Advertencias antes de abandonar:** Si el estudiante ha comenzado a escribir una reseña e intenta cerrar el modal o navegar a otra sección, el sistema muestra un cuadro de diálogo de confirmación advirtiendo que los datos no guardados se perderán.

### 1.6. Reconocimiento antes que recuerdo
* **Búsquedas recientes sugeridas:** Al hacer clic en la barra de búsqueda, se despliega una lista corta con los últimos nombres de profesores que el estudiante ha buscado recientemente.
* **Contexto de evaluación visible:** En la parte superior del formulario de calificación, se muestra de manera fija el nombre del profesor, su foto y su departamento, de modo que el estudiante no deba recordar a quién está calificando.
* **Fichas comparativas explícitas:** El comparador muestra de manera simultánea y lado a lado las tarjetas completas de los profesores seleccionados, con sus métricas etiquetadas directamente para evitar que el estudiante deba recordar los valores del perfil anterior.

### 1.7. Flexibilidad y eficiencia de uso
* **Búsqueda y filtrado avanzados:** Permite a los estudiantes filtrar directamente por facultad, calificación promedio mínima o nivel de dificultad técnica, acelerando el proceso de encontrar un docente idóneo.
* **Accesos rápidos a comparación:** El estudiante puede agregar a un docente a la herramienta de comparación directamente desde la lista de resultados de búsqueda sin necesidad de acceder a la página de perfil detallada del profesor.
* **Teclas de navegación rápida:** El cursor se enfoca de manera automática en la barra de búsqueda principal en cuanto el estudiante ingresa al sitio web, permitiéndole empezar a escribir de inmediato sin usar el ratón.

### 1.8. Estética y diseño minimalista
* **Tarjetas de información condensada:** Las fichas de los profesores contienen únicamente la información relevante para el alumno (promedio, puntualidad, dificultad y últimas reseñas), evitando sobrecargar la pantalla con datos secundarios.
* **Jerarquía visual espaciada:** Se utiliza espacio negativo (en blanco) para separar de manera clara los diferentes comentarios de alumnos, facilitando la lectura individual y evitando la fatiga visual.
* **Simplicidad en el formulario:** El formulario de calificación se divide en secciones limpias y directas, eliminando cualquier distracción que no guarde relación directa con la evaluación del docente.

### 1.9. Ayudar a los usuarios a reconocer, diagnosticar y recuperarse de los errores
* **Mensajes de error detallados y constructivos:** Si falla la carga del formulario por longitud de caracteres, el mensaje de error indica: "Tu reseña debe tener al menos 30 caracteres. Faltan [X] caracteres" en lugar de un genérico "Entrada inválida".
* **Enfoque visual del fallo:** El campo de entrada de texto que genera el error se resalta en rojo de forma automática para guiar directamente la atención del estudiante al punto conflictivo.
* **Sugerencias ante búsquedas vacías:** Cuando la búsqueda de un docente no arroja resultados, la interfaz muestra un mensaje indicando sugerencias prácticas: "Verifica que el nombre esté bien escrito o intenta buscar únicamente por el apellido".

### 1.10. Ayuda y documentación
* **Consejos y guías rápidas:** Al iniciar el proceso de calificación, se visualiza una pequeña guía desplegable con consejos sobre cómo escribir una reseña constructiva y objetiva.
* **Glosario de métricas:** Cada indicador técnico de calificación (como el nivel de "Dificultad" o la tasa de "Puntualidad") tiene un icono interactivo de información (?) que, al pasar el cursor, explica en una burbuja de texto cómo se calcula dicha métrica.
* **Preguntas Frecuentes específicas:** Se proporciona una sección de ayuda dedicada a los estudiantes con respuestas a dudas frecuentes sobre el anonimato de las reseñas y los criterios de publicación.

---

## 2. Pruebas de usabilidad

### 2.1. Objetivo de las pruebas de usabilidad
El objetivo central de estas pruebas de usabilidad es evaluar la fluidez y autonomía del estudiante al interactuar con las funcionalidades principales de Puntualo. Específicamente, se busca determinar si el alumno puede buscar y encontrar perfiles de profesores sin desorientarse, calificar a un docente a través de un formulario guiado de manera exitosa y realizar comparativas en paralelo de forma intuitiva, minimizando la carga cognitiva y optimizando la tasa de éxito de cada flujo.

### 2.2. Perfil de usuarios evaluados

| Característica | Descripción |
| :--- | :--- |
| **Edad** | Estudiantes universitarios activos entre 18 y 26 años. |
| **Dispositivo principal** | Teléfono inteligente (Smartphone) y computadora portátil (Laptop) con conexión a internet. |
| **Nivel tecnológico** | Medio a alto; usuarios habituales de redes sociales, portales universitarios y herramientas colaborativas digitales. |

Durante las sesiones de prueba se aplicará de manera estricta el método de indagación **'think-aloud' (pensar en voz alta)**. Este enfoque nos permitirá recopilar información cualitativa directa sobre el razonamiento, las dudas y las emociones del estudiante al interactuar con el sistema, complementando de esta manera las métricas de rendimiento cuantitativas (como los tiempos de resolución y el recuento de errores).

### 2.3. Escenarios evaluados

| Escenario | Objetivo | Flujo evaluado | Resultado esperado |
| :--- | :--- | :--- | :--- |
| **1. Buscar y encontrar a un docente específico** | Medir la rapidez y precisión con la que un estudiante localiza el perfil de un profesor concreto dentro de la base de datos de la plataforma. | Inicio -> Clic en el buscador -> Escribir nombre del docente -> Seleccionar filtros por facultad -> Seleccionar tarjeta del docente en los resultados. | El estudiante encuentra la ficha del profesor solicitado y entra a su perfil detallado en menos de 15 segundos y sin realizar clics innecesarios. |
| **2. Publicar una calificación y reseña** | Evaluar la claridad de las métricas de evaluación y comprobar si el estudiante puede completar satisfactoriamente el proceso de calificación de un docente. | Perfil del docente -> Clic en botón "Calificar" -> Asignación de estrellas en las métricas -> Redacción del comentario -> Clic en "Publicar" -> Confirmación. | El estudiante completa todas las métricas obligatorias, escribe el comentario mínimo solicitado y envía el formulario de calificación sin experimentar bloqueos visuales ni errores de validación. |
| **3. Utilizar el comparador para evaluar a dos profesores simultáneamente** | Validar la intuición y facilidad de uso del sistema de comparación de perfiles académicos en paralelo para la toma de decisiones. | Inicio -> Agregar profesor "A" al comparador -> Buscar y agregar profesor "B" al comparador -> Entrar a la vista del comparador -> Analizar datos en paralelo. | El estudiante logra contrastar las métricas de ambos docentes una al lado de la otra y determina verbalmente cuál tiene mejores valoraciones en un lapso menor a 25 segundos. |

### 2.4. Aspectos evaluados

| Aspecto | Descripción | ¿Cómo se mide? | Tipo |
| :--- | :--- | :--- | :--- |
| **Navegación** | Facilidad del estudiante para desplazarse entre páginas y funciones de la plataforma sin confundirse. | Tasa de finalización del flujo, uso de los botones "Volver" o de navegación principal, y registro de desvíos de ruta. | Cualitativo y Cuantitativo |
| **Claridad visual** | Facilidad para identificar botones, elementos de formulario y textos relevantes sin esfuerzo cognitivo. | Detección visual de elementos, comentarios del usuario durante el protocolo 'think-aloud' y número de clics erróneos en zonas no interactivas. | Cualitativo |
| **Tiempo de uso** | Rapidez con la que un estudiante realiza una acción desde que se le plantea el escenario hasta su término. | Registro en segundos del tiempo transcurrido para la resolución de cada uno de los 3 escenarios descritos. | Cuantitativo |
| **Terminología** | Comprensión del vocabulario, títulos y descripciones de métricas usadas en la interfaz. | Preguntas abiertas post-tarea al estudiante sobre el significado de métricas como "Dificultad" o "Puntualidad". | Cualitativo |
| **Cantidad de errores** | Frecuencia de incidentes que obstaculizan la navegación o la compleción de tareas por parte del estudiante. | Conteo de errores cometidos por escenario, agrupados en leves (errores tipográficos, clics accidentales) y críticos (bloqueo total). | Cuantitativo |
| **Satisfacción del usuario** | Percepción general del estudiante acerca de la utilidad, velocidad y agrado visual de la plataforma. | Aplicación del cuestionario estandarizado SUS (System Usability Scale) y escala de satisfacción de 1 a 5 al finalizar la prueba. | Cuantitativo y Cualitativo |

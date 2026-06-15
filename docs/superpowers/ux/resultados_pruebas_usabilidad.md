# Resultados de las Pruebas de Usabilidad - Puntualo (Ficticios)

Este documento detalla los resultados obtenidos en la simulación de pruebas de usabilidad con 5 estudiantes universitarios activos, aplicando los escenarios y métricas establecidos en el plan de pruebas.

---

## 1. Perfil de los Estudiantes Evaluados

* **Estudiante 1 (E1):** 20 años. Escuela de Ingeniería de Software. Dispositivo: Laptop (Windows). Nivel tecnológico: Medio-Alto.
* **Estudiante 2 (E2):** 22 años. Escuela de Ingeniería de Software. Dispositivo: Smartphone (Android). Nivel tecnológico: Medio-Alto.
* **Estudiante 3 (E3):** 19 años. Escuela de Ingeniería de Software. Dispositivo: Laptop (macOS). Nivel tecnológico: Medio-Alto.
* **Estudiante 4 (E4):** 24 años. Escuela de Ingeniería de Software. Dispositivo: Smartphone (iOS). Nivel tecnológico: Medio-Alto.
* **Estudiante 5 (E5):** 21 años. Escuela de Ingeniería de Software. Dispositivo: Laptop (Windows). Nivel tecnológico: Medio-Alto.

---

## 2. Tiempos de Uso y Registro de Errores por Escenario

A continuación, se tabulan los tiempos de resolución (en segundos) y la cantidad de errores cometidos por cada estudiante durante las pruebas.

### Tabla de Rendimiento por Escenario

| Estudiante | Escenario 1 (Buscar Docente) | Escenario 2 (Publicar Calificación) | Escenario 3 (Comparar Profesores) | Errores Totales | Satisfacción (SUS / 100) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Estudiante 1 (E1)** | 11 s (0 err) | 45 s (0 err) | 22 s (0 err) | 0 | 92.5 |
| **Estudiante 2 (E2)** | 14 s (1 err) | 58 s (1 err) | 30 s (1 err) | 3 | 80.0 |
| **Estudiante 3 (E3)** | 9 s (0 err) | 40 s (0 err) | 18 s (0 err) | 0 | 95.0 |
| **Estudiante 4 (E4)** | 17 s (1 err) | 52 s (0 err) | 25 s (0 err) | 1 | 82.5 |
| **Estudiante 5 (E5)** | 12 s (0 err) | 65 s (1 err) | 20 s (0 err) | 1 | 87.5 |
| **Promedios** | **12.6 s** | **52.0 s** | **23.0 s** | **1.0** | **87.5** |

---

## 3. Transcripciones Destacadas (Método Think-Aloud)

Se obtuvieron las siguientes verbalizaciones clave que exponen el modelo mental del estudiante al interactuar con la interfaz:

### Sobre la Búsqueda y Filtros (Escenario 1)
* **Estudiante 4 (E4):** *"Voy a buscar al profesor Arredondo para ver sus calificaciones... A ver, escribo 'Arredondo' en la barra principal... Uy, me aparecen bastantes profesores con ese apellido. Déjame ver si puedo filtrar por mi facultad... Ah, sí, aquí a la izquierda dice 'Ingeniería'. Al seleccionarlo se actualizó al instante y solo quedaron dos perfiles. Es el profesor Arredondo, lo identifiqué rápido porque abajo de su nombre dice 'Estructuras de Datos'. Listo, le doy clic y ya estoy en su ficha."*

### Sobre la Calificación y Validación de Errores (Escenario 2)
* **Estudiante 2 (E2):** *"Le doy al botón verde de 'Calificar Profesor'. Me abre un modal limpio. Le pongo 4 estrellas en claridad y 2 en puntualidad porque suele llegar tarde. En la caja de comentarios voy a poner: 'Buen docente.'... A ver, el botón de publicar sigue apagado. ¿Qué pasó? Ah, un aviso en rojo debajo de la caja de texto dice: 'Tu reseña debe tener al menos 30 caracteres. Faltan 18 caracteres'. Menos mal me lo indica exactamente ahí. Voy a complementarlo escribiendo más sobre el tipo de exámenes que toma... Listo, ya se activó el botón de publicar, le doy clic y me sale el mensaje verde confirmando que mi evaluación fue enviada exitosamente."*
* **Estudiante 5 (E5):** *"Entro a evaluar a mi profesora de Programación Orientada a Objetos... Me pide calificar la 'Dificultad'. ¿Dificultad de qué? ¿De pasar su materia o de su carácter?... Déjame ver este icono de pregunta al lado del título. Ah, perfecto, el tooltip dice: 'Mide la complejidad promedio de las evaluaciones y el nivel de exigencia en las tareas'. Ahora sí entiendo qué evaluar. Le pongo un 4 de dificultad porque sus exámenes son bastante largos y detallados."*

### Sobre la Herramienta de Comparación (Escenario 3)
* **Estudiante 2 (E2):** *"Quiero comparar a dos profesores para matricular mi clase de Bases de Datos el próximo semestre. En la tarjeta del primer profesor veo un botón con el icono de una balanza que dice 'Comparar'. Le doy clic y aparece una burbuja flotante abajo que dice '1 profesor seleccionado'. Excelente, ahora busco al segundo profesor... aquí está. Le doy también a 'Comparar'. La burbuja cambia a '2 profesores seleccionados' y me da el botón 'Ir al comparador'. Al entrar, me muestra ambos perfiles en columnas paralelas. Es genial ver las barras de dificultad y puntualidad una al lado de la otra. Me ayuda mucho a decidir sin tener que ir abriendo pestañas diferentes del navegador."*

---

## 4. Análisis Consolidado de Aspectos Evaluados

* **Navegación (Cualitativo y Cuantitativo):** La tasa de finalización del flujo fue del 100%. Los estudiantes transitaron sin problemas entre el buscador, los perfiles individuales y la sección de comparación. Se observó un leve retraso en E2 en el comparador, quien intentó inicialmente arrastrar las tarjetas de los docentes antes de pulsar el botón dedicado a la acción.
* **Claridad visual (Cualitativo):** La jerarquía visual fue calificada positivamente. Los tooltip de información y las etiquetas de error en rojo al lado de las cajas de texto ayudaron a corregir problemas de forma instantánea sin generar frustración.
* **Tiempo de uso (Cuantitativo):** El promedio general de los escenarios se mantiene dentro de los límites ideales de usabilidad web: 12.6 segundos para búsqueda, 52.0 segundos para el llenado y redacción del formulario, y 23.0 segundos para realizar la comparación de profesores.
* **Terminología (Cualitativo):** El vocabulario es altamente familiar para el rol de Estudiante. La única duda inicial surgió con la métrica de 'Dificultad', la cual fue resuelta eficientemente a través de la lectura del tooltip explicativo.
* **Cantidad de errores (Cuantitativo):** Se registró un promedio de 1.0 errores por sesión de prueba. El error más común fue intentar enviar comentarios de texto por debajo del límite de longitud (Escenario 2), lo cual fue corregido por los estudiantes de inmediato gracias a los mensajes de validación dinámicos.
* **Satisfacción del usuario (Cuantitativo y Cualitativo):** La puntuación SUS promedio fue de **87.5 / 100**, lo que clasifica a la interfaz como "Excelente" en términos de experiencia de usuario y facilidad de uso para el estudiante universitario.

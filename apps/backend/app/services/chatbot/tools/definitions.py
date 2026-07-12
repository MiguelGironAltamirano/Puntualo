"""JSON schemas de las tools para function calling (Gemini)."""

TOOL_DECLARATIONS = [
    {
        "name": "get_course_professors",
        "description": (
            "Devuelve los profesores que dictan un curso, buscando el curso por "
            "su nombre (parcial) en una sola llamada. Es LA herramienta para "
            "responder '¿qué profesor me recomiendas para <curso>?'. Úsala "
            "SIEMPRE que el usuario mencione un curso por nombre; no necesitas "
            "resolver el course_id por separado."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "course_name": {
                    "type": "string",
                    "description": "Nombre (parcial) del curso mencionado por el usuario.",
                },
            },
            "required": ["course_name"],
        },
    },
    {
        "name": "search_courses",
        "description": (
            "Busca cursos activos por nombre para resolver su course_id. "
            "Úsala SIEMPRE que el usuario mencione un curso por nombre, antes "
            "de llamar a search_professors con ese course_id — el filtro "
            "por curso solo funciona con el ID exacto, no con el nombre."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Nombre (parcial) del curso a buscar.",
                },
                "university_id": {
                    "type": "integer",
                    "description": "Filtra por ID de universidad.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_professors",
        "description": (
            "Busca profesores validados por nombre/tema, con filtros opcionales "
            "de curso (usa course_id obtenido de search_courses), facultad o "
            "hashtags. Con solo course_id (sin query) lista todos los profesores "
            "que dictan ese curso. Devuelve una lista breve."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Texto de búsqueda (tema o nombre del profesor). "
                        "Omítelo para listar todos los del course_id/faculty_id."
                    ),
                },
                "course_id": {
                    "type": "integer",
                    "description": "Filtra por ID de curso.",
                },
                "faculty_id": {
                    "type": "integer",
                    "description": "Filtra por ID de facultad.",
                },
            },
        },
    },
    {
        "name": "search_professors_by_topic",
        "description": (
            "Búsqueda semántica de profesores por tema, estilo de enseñanza o "
            "reputación (sobre sus reseñas y resúmenes). Úsala cuando el usuario "
            "pregunte por características ('paciente', 'bueno explicando', 'sobre "
            "machine learning') SIN pedir un curso puntual. IMPORTANTE: sus "
            "resultados NO confirman qué curso dicta cada profesor; para "
            "recomendar por curso usa search_courses + search_professors."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Tema, estilo o característica buscada.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_professor_details",
        "description": (
            "Obtiene el detalle completo de un profesor (resumen IA, cursos que "
            "dicta, puntajes) por su UUID o directamente por su nombre — no "
            "necesitas buscar el UUID primero."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "professor_id": {
                    "type": "string",
                    "description": "UUID del profesor (si lo tienes de una búsqueda).",
                },
                "professor_name": {
                    "type": "string",
                    "description": "Nombre del profesor tal como apareció en la conversación.",
                },
            },
        },
    },
    {
        "name": "compare_professors_by_name",
        "description": (
            "Compara 2 o más profesores POR NOMBRE en una sola llamada (puntajes "
            "y métricas detalladas de sus evaluaciones). Es LA herramienta para "
            "'¿cuál de estos profesores es mejor / ayuda más / exige menos?': "
            "pásale los nombres tal como aparecieron en la conversación, sin "
            "resolver UUIDs por separado."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Nombres de los profesores a comparar.",
                },
            },
            "required": ["names"],
        },
    },
    {
        "name": "compare_professors",
        "description": "Compara 2 o más profesores por UUID (puntajes y métricas detalladas).",
        "parameters": {
            "type": "object",
            "properties": {
                "professor_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de UUIDs de los profesores a comparar.",
                },
            },
            "required": ["professor_ids"],
        },
    },
]

"""JSON schemas de las tools para function calling (Gemini)."""

TOOL_DECLARATIONS = [
    {
        "name": "search_professors",
        "description": (
            "Busca profesores validados por nombre/tema, con filtros opcionales "
            "de curso, facultad o hashtags. Devuelve una lista breve."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Texto de búsqueda (tema o nombre del profesor).",
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
            "required": ["query"],
        },
    },
    {
        "name": "get_professor_details",
        "description": (
            "Obtiene el detalle completo de un profesor por su ID, "
            "incluyendo resumen IA, cursos que dicta y puntajes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "professor_id": {
                    "type": "string",
                    "description": "UUID del profesor.",
                },
            },
            "required": ["professor_id"],
        },
    },
    {
        "name": "compare_professors",
        "description": "Compara 2 o más profesores por ID (puntajes y métricas detalladas).",
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

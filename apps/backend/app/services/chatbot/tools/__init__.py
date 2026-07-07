"""Dispatcher de function-calling tools del chatbot."""
# Importamos con alias privados para que los nombres de función no sombreen
# los submódulos homónimos (Python usa atributo del paquete en 'import a.b as x').
from app.services.chatbot.tools.compare_professors import compare_professors as _compare
from app.services.chatbot.tools.definitions import TOOL_DECLARATIONS
from app.services.chatbot.tools.get_professor_details import (
    get_professor_details as _get_detail,
)
from app.services.chatbot.tools.search_courses import search_courses as _search_courses
from app.services.chatbot.tools.search_professors import search_professors as _search

TOOL_EXECUTORS: dict = {
    "search_courses": _search_courses,
    "search_professors": _search,
    "get_professor_details": _get_detail,
    "compare_professors": _compare,
}

__all__ = ["TOOL_DECLARATIONS", "TOOL_EXECUTORS"]

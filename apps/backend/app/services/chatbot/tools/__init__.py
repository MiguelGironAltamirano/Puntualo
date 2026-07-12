"""Dispatcher de function-calling tools del chatbot."""
# Importamos con alias privados para que los nombres de función no sombreen
# los submódulos homónimos (Python usa atributo del paquete en 'import a.b as x').
from app.services.chatbot.tools.compare_professors import compare_professors as _compare
from app.services.chatbot.tools.compare_professors_by_name import (
    compare_professors_by_name as _compare_by_name,
)
from app.services.chatbot.tools.definitions import TOOL_DECLARATIONS
from app.services.chatbot.tools.get_course_professors import (
    get_course_professors as _get_course_profs,
)
from app.services.chatbot.tools.get_professor_details import (
    get_professor_details as _get_detail,
)
from app.services.chatbot.tools.search_courses import search_courses as _search_courses
from app.services.chatbot.tools.search_professors import search_professors as _search
from app.services.chatbot.tools.search_professors_by_topic import (
    search_professors_by_topic as _search_by_topic,
)

TOOL_EXECUTORS: dict = {
    "get_course_professors": _get_course_profs,
    "search_courses": _search_courses,
    "search_professors": _search,
    "search_professors_by_topic": _search_by_topic,
    "get_professor_details": _get_detail,
    "compare_professors": _compare,
    "compare_professors_by_name": _compare_by_name,
}

__all__ = ["TOOL_DECLARATIONS", "TOOL_EXECUTORS"]

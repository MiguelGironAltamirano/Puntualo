"""app/utils/db.py

Utilidades de bajo nivel para consultas con SQLAlchemy.
"""


def escape_like(term: str, escape_char: str = "\\") -> str:
    """Escapa los caracteres comodín de SQL LIKE/ILIKE en *term*.

    Los caracteres ``%``, ``_`` y el propio caracter de escape (``\\`` por
    defecto) son interpretados por el motor de base de datos como comodines
    dentro de un patrón LIKE.  Si el usuario los incluye en una búsqueda de
    texto libre éstos pueden generar full-table scans arbitrarios (LIKE
    Injection / DoS).

    Uso::

        from app.utils.db import escape_like

        safe = f"%{escape_like(user_input)}%"
        stmt = stmt.where(Column.ilike(safe, escape="\\\\"))

    Args:
        term: Cadena de búsqueda ingresada por el usuario.
        escape_char: Caracter usado como prefijo de escape. Debe coincidir
            con el valor pasado a ``ilike(..., escape=...)``.

    Returns:
        Cadena con ``escape_char``, ``%`` y ``_`` escapados.
    """
    # El caracter de escape se escapa primero para no duplicar las sustituciones.
    term = term.replace(escape_char, escape_char * 2)
    term = term.replace("%", escape_char + "%")
    term = term.replace("_", escape_char + "_")
    return term

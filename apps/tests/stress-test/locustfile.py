"""
Prueba de estrés — punto de quiebre del backend (más allá de 50 usuarios).

Nivel:   Sistema
Tipo:    No Funcional (Rendimiento)
Técnica: Caja Negra
Objetivo: subir la carga hasta encontrar el punto donde se degrada/cae el servicio.

Complementa a apps/tests/load-test/ (carga nominal, 50 usuarios).
Prioridad MoSCoW: Won't have (por ahora).

TODO: implementar. Reutilizar tareas de load-test/locustfile.py escalando
      --users y --spawn-rate por etapas (p. ej. 100, 200, 400).
"""

# Placeholder — el desarrollo es posterior.

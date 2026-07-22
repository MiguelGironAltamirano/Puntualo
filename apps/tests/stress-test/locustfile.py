"""
Prueba de estrés — punto de quiebre del backend (más allá de 50 usuarios).

Nivel:   Sistema
Tipo:    No Funcional (Rendimiento)
Técnica: Caja Negra
Objetivo: subir la carga por etapas hasta encontrar el punto donde el servicio
          se degrada (latencia p95 dispara / aparecen errores 5xx).

Complementa a apps/tests/load-test/ (carga nominal, 50 usuarios). Reutiliza las
mismas tareas de solo-lectura sobre endpoints PÚBLICOS (GET), así que es seguro
correrlo contra la VM: no escribe datos ni requiere credenciales.

Prioridad MoSCoW: Won't have (por ahora) — implementado y listo para ejecutar.

Uso (headless, etapas automáticas, reporte HTML + CSV):
    locust -f locustfile.py \
        --host https://puntualo.duckdns.org \
        --headless --html results/reporte_estres.html --csv results/estres

    El `StagesShape` controla usuarios y duración por etapa; NO hace falta pasar
    --users/--run-time (los ignora la shape). Salidas en results/ (crear la carpeta).

Interpretación esperada: identificar la etapa donde p95 supera ~3 s o la tasa de
error deja de ser 0%, y reportarlo como el punto de quiebre observado (trazable a
R6 — saturación de BD bajo carga, ver 05_riesgos_defectos_seguridad.md).
"""

import random

from locust import HttpUser, LoadTestShape, between, task

# IDs de profesores reales, sembrados desde /evaluations al arrancar.
PROFESSOR_IDS: list[str] = []


class StressReaderUser(HttpUser):
    """Visitante anónimo navegando contenido público (mismas tareas que carga)."""

    wait_time = between(1, 4)

    def on_start(self) -> None:
        """Siembra IDs de profesor desde el endpoint público /evaluations."""
        if not PROFESSOR_IDS:
            with self.client.get(
                "/evaluations?page=1&page_size=50",
                name="/evaluations [seed]",
                catch_response=True,
            ) as resp:
                if resp.ok:
                    try:
                        for it in resp.json().get("items", []):
                            pid = it.get("professor_id")
                            if pid and pid not in PROFESSOR_IDS:
                                PROFESSOR_IDS.append(str(pid))
                    except Exception:
                        pass

    # ---- Tareas ponderadas (números = frecuencia relativa) ----

    @task(5)
    def list_evaluations(self) -> None:
        page = random.randint(1, 3)
        self.client.get(
            f"/evaluations?page={page}&page_size=20",
            name="/evaluations [list]",
        )

    @task(4)
    def professor_comments(self) -> None:
        if not PROFESSOR_IDS:
            return
        pid = random.choice(PROFESSOR_IDS)
        self.client.get(
            f"/professors/{pid}/comments?page=1&page_size=20",
            name="/professors/{id}/comments",
        )

    @task(3)
    def list_courses(self) -> None:
        self.client.get("/courses?page=1&page_size=20", name="/courses")

    @task(2)
    def catalogs_universities(self) -> None:
        self.client.get("/catalogs/universities", name="/catalogs/universities")

    @task(2)
    def hashtags(self) -> None:
        self.client.get("/hashtags", name="/hashtags")

    @task(1)
    def health(self) -> None:
        self.client.get("/health/db", name="/health/db")


class StagesShape(LoadTestShape):
    """Escalonado de carga: sube usuarios por etapas hasta el punto de quiebre.

    Cada etapa sostiene la carga ~2 min. Si el servicio se degrada antes, se ve en
    las gráficas de latencia/errores del reporte. El escalón final (400 usuarios)
    es deliberadamente agresivo para la VM (pool de 14 conexiones).
    """

    stages = [
        {"duration": 120, "users": 50, "spawn_rate": 10},
        {"duration": 240, "users": 100, "spawn_rate": 10},
        {"duration": 360, "users": 200, "spawn_rate": 20},
        {"duration": 480, "users": 400, "spawn_rate": 40},
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        return None

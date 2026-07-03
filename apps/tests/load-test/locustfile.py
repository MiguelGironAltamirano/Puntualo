"""
Prueba de carga - Puntualo backend (50 usuarios concurrentes)

Solo ejercita endpoints PÚBLICOS de lectura (GET) que responden 200 sin
autenticación. No escribe datos ni requiere credenciales, por lo que es
seguro correrlo contra la VM.

NOTA: /professors (lista, búsqueda, detalle) NO es público — exige login
(devuelve 401), por eso NO se incluye. Los IDs de profesor para visitar
sus comentarios se obtienen del endpoint público /evaluations.

Ejecutar SIEMPRE desde apps/tests/load-test/ usando el .venv del root del repo.

Uso (modo UI web):
    locust -f locustfile.py --host https://puntualo.duckdns.org
    # luego abre http://localhost:8089 y pon Users=50, Ramp up=5

Uso (headless, 50 users, 3 min, reporte HTML + CSV):
    locust -f locustfile.py \
        --host https://puntualo.duckdns.org \
        --users 50 --spawn-rate 5 --run-time 3m \
        --headless --html results/reporte.html --csv results/resultados

    Salidas:
      results/reporte.html        -> reporte visual (SÍ se versiona)
      results/resultados_*.csv    -> data cruda (ignorada por git)
"""

import random

from locust import HttpUser, between, task

# IDs de profesores reales, sembrados desde /evaluations al arrancar.
PROFESSOR_IDS: list[str] = []


class PublicReaderUser(HttpUser):
    """Simula un visitante anónimo navegando el contenido público."""

    # Think time de un usuario real: 1-4 s entre acciones.
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

"""Hook de resumen IA (Tarea 4.4).

Tarea 6 lo llama post-commit desde `evaluation_service.create`. Cuando el flag
IA_SUMMARY_HOOK_ENABLED está encendido, encola la generación del resumen. El
scheduler Beat (enqueue_pending_summaries) actúa como red de respaldo, así que
si el broker está caído aquí no se pierde nada.
"""
import logging

from app.core.config import settings
from app.tasks.nlp_tasks import generate_professor_summary

logger = logging.getLogger(__name__)


class SummaryTrigger:
    """Verifica si toca regenerar el resumen IA del profesor."""

    async def maybe_dispatch(self, professor_id: str) -> None:
        if not settings.IA_SUMMARY_HOOK_ENABLED:
            return
        # El guard de umbral/staleness vive en generate_and_store / find_stale.
        # Aquí solo encolamos; la task decide si genera o hace skip.
        generate_professor_summary.delay(professor_id)
        logger.info("summary_trigger.enqueued | professor_id=%s", professor_id)

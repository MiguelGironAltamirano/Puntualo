"""Hook de resumen IA — stub para Tarea 10 (cuerpo real en 10).

Tarea 6 lo llama post-commit desde `evaluation_service.create`. Por ahora es
un no-op si el feature flag esta apagado. Tarea 10 implementa la comparacion
contra `IA_SUMMARY_THRESHOLD` y el dispatch de la task celery cuando 4.4 este
lista.
"""
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class SummaryTrigger:
    """Verifica si toca regenerar el resumen IA del profesor."""

    async def maybe_dispatch(self, professor_id: str) -> None:
        if not settings.IA_SUMMARY_HOOK_ENABLED:
            return
        # Tarea 10: comparar contadores + dispatch generate_ai_summary.delay(...)
        logger.info(
            "summary_trigger.skipped_no_task_yet | professor_id=%s", professor_id
        )

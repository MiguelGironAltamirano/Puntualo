from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "puntualo",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.include = [
    "app.tasks.professor_validation_tasks",
    "app.tasks.score_recalculation_tasks",
    "app.tasks.nlp_tasks",
    "app.tasks.embeddings_tasks",
]

celery_app.conf.update(
    task_acks_late=True,
    task_track_started=True,
    timezone="UTC",
    worker_concurrency=3,  # Supabase transaction pooler: acotamos workers para no saturar conexiones
    beat_schedule={
        "nlp-enqueue-pending-summaries": {
            "task": "nlp.enqueue_pending_summaries",
            "schedule": float(settings.NLP_SUMMARY_BEAT_SECONDS),
        },
        "chat-enqueue-stale-embeddings": {
            "task": "chat.enqueue_stale_embeddings",
            "schedule": float(settings.EMBEDDINGS_BEAT_SECONDS),
        },
    },
)

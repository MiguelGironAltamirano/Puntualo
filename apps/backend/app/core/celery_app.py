from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "puntualo",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.autodiscover_tasks(["app.tasks"])

celery_app.conf.update(
    task_acks_late=True,
    task_track_started=True,
    timezone="UTC",
)

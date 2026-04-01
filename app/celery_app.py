from celery import Celery
from app.config import config

celery_app = Celery(
    "file_processor",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_track_started=True,
    result_expires=config.TASK_TTL,
    task_time_limit=3600,
    task_default_queue="file_processing"
)
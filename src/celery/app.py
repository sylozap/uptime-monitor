from celery import Celery
from src.core.config import settings

app = Celery(
    "uptime-monitor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["src.celery.tasks.monitor_checks"],
)

app.conf.update(
    accept_content=["json"],
    beat_schedule={
        "schedule-monitor-checks-every-minute": {
            "task": "src.celery.tasks.schedule_checks",
            "schedule": 60.0,
        },
    },
    enable_utc=True,
    result_serializer="json",
    task_serializer="json",
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_soft_time_limit=70,
    task_time_limit=90,
    timezone="UTC",
    worker_prefetch_multiplier=1,
)

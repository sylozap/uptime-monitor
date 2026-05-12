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
    timezone="UTC",
)

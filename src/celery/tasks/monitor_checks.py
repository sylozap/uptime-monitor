import uuid

from src.celery.app import app
from src.celery.loop import run_async
from src.database.core import async_session_maker
from src.services.factories import create_monitor_check_service
from src.services.monitor_scheduler_service import MonitorSchedulerService


@app.task(
    name="src.celery.tasks.check_monitor_task",
    autoretry_for=(ConnectionError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def check_monitor_task(monitor_id: str) -> None:
    try:
        monitor_uuid = uuid.UUID(monitor_id)
    except ValueError:
        return

    async def run_task():
        async with async_session_maker() as session:
            service = create_monitor_check_service(session)
            await service.check_monitor(monitor_uuid)

    run_async(run_task())


@app.task(name="src.celery.tasks.schedule_checks")
def schedule_checks() -> int:
    service = MonitorSchedulerService(async_session_maker)

    async def run_schedule():
        return await service.schedule_due_checks(_enqueue_monitor_check)

    return run_async(run_schedule())


def _enqueue_monitor_check(monitor_id: uuid.UUID) -> None:
    check_monitor_task.delay(str(monitor_id))  # type: ignore

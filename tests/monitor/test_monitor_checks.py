import asyncio
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.celery.tasks import monitor_checks
from src.integrations.url_checker import PingResult
from src.models.check_log import CheckLog
from src.models.incident import Incident
from src.repositories.check_log_repository import CheckLogRepository
from src.repositories.incident_repository import IncidentRepository
from src.repositories.monitor_repository import MonitorRepository
from src.services.incident_service import IncidentService
from src.services.monitor_check_service import MonitorCheckService
from src.services.monitor_scheduler_service import MonitorSchedulerService
from tests.monitor.helpers import create_monitor_in_db, create_user_in_db


def create_check_service(
    db_session: AsyncSession,
    ping_url: Any,
) -> MonitorCheckService:
    monitor_repository = MonitorRepository(db_session)
    check_log_repository = CheckLogRepository(db_session)
    incident_repository = IncidentRepository(db_session)
    incident_service = IncidentService(incident_repository)

    return MonitorCheckService(
        session=db_session,
        monitor_repository=monitor_repository,
        check_log_repository=check_log_repository,
        incident_service=incident_service,
        ping_url=ping_url,
    )


async def get_check_logs(db_session: AsyncSession) -> list[CheckLog]:
    result = await db_session.execute(select(CheckLog).order_by(CheckLog.id))
    return list(result.scalars().all())


async def get_incidents(db_session: AsyncSession) -> list[Incident]:
    result = await db_session.execute(select(Incident).order_by(Incident.started_at))
    return list(result.scalars().all())


async def test_check_monitor_updates_monitor_and_creates_check_log(
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session)
    monitor = await create_monitor_in_db(
        db_session,
        user_id=user.id,
        check_interval=120,
        timeout=5,
        expected_status=204,
    )
    ping_calls: list[tuple[str, dict[str, Any]]] = []

    async def fake_ping(url: str, **kwargs: Any) -> PingResult:
        ping_calls.append((url, kwargs))
        return PingResult(is_available=True, status_code=204, response_time=42)

    service = create_check_service(db_session, fake_ping)

    await service.check_monitor(monitor.id)

    await db_session.refresh(monitor)
    check_logs = await get_check_logs(db_session)
    incidents = await get_incidents(db_session)

    assert ping_calls == [
        ("https://example.com", {"timeout": 5, "expected_status": 204})
    ]
    assert monitor.last_status is True
    assert monitor.last_status_code == 204
    assert monitor.last_checked_at is not None
    assert monitor.next_check_at == monitor.last_checked_at + timedelta(seconds=120)
    assert len(check_logs) == 1
    assert check_logs[0].monitor_id == monitor.id
    assert check_logs[0].response_time == 42
    assert check_logs[0].status_code == 204
    assert check_logs[0].is_available is True
    assert incidents == []


async def test_check_monitor_creates_incident_for_unavailable_monitor(
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session)
    monitor = await create_monitor_in_db(db_session, user_id=user.id)

    async def fake_ping(url: str, **kwargs: Any) -> PingResult:
        return PingResult(
            is_available=False,
            status_code=500,
            response_time=88,
            error_type="unexpected_status",
        )

    service = create_check_service(db_session, fake_ping)

    await service.check_monitor(monitor.id)

    await db_session.refresh(monitor)
    check_logs = await get_check_logs(db_session)
    incidents = await get_incidents(db_session)

    assert monitor.last_status is False
    assert monitor.last_status_code == 500
    assert len(check_logs) == 1
    assert check_logs[0].is_available is False
    assert len(incidents) == 1
    assert incidents[0].monitor_id == monitor.id
    assert incidents[0].error_type == "unexpected_status"
    assert incidents[0].ended_at is None


async def test_check_monitor_closes_open_incident_when_monitor_recovers(
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session)
    monitor = await create_monitor_in_db(db_session, user_id=user.id)
    results = iter(
        [
            PingResult(
                is_available=False,
                status_code=None,
                response_time=100,
                error_type="timeout",
            ),
            PingResult(is_available=True, status_code=200, response_time=31),
        ]
    )

    async def fake_ping(url: str, **kwargs: Any) -> PingResult:
        return next(results)

    service = create_check_service(db_session, fake_ping)

    await service.check_monitor(monitor.id)
    await service.check_monitor(monitor.id)

    await db_session.refresh(monitor)
    check_logs = await get_check_logs(db_session)
    incidents = await get_incidents(db_session)

    assert monitor.last_status is True
    assert monitor.last_status_code == 200
    assert len(check_logs) == 2
    assert len(incidents) == 1
    assert incidents[0].error_type == "timeout"
    assert incidents[0].ended_at is not None


async def test_check_monitor_ignores_inactive_monitor(db_session: AsyncSession):
    user = await create_user_in_db(db_session)
    monitor = await create_monitor_in_db(
        db_session,
        user_id=user.id,
        is_active=False,
    )

    async def fake_ping(url: str, **kwargs: Any) -> PingResult:
        raise AssertionError("inactive monitor should not be checked")

    service = create_check_service(db_session, fake_ping)

    await service.check_monitor(monitor.id)

    await db_session.refresh(monitor)
    check_logs = await get_check_logs(db_session)

    assert monitor.last_checked_at is None
    assert check_logs == []


async def test_scheduler_reserves_and_enqueues_due_monitors(
    db_session: AsyncSession,
):
    user = await create_user_in_db(db_session)
    due_monitor = await create_monitor_in_db(
        db_session,
        user_id=user.id,
        check_interval=90,
    )
    future_monitor = await create_monitor_in_db(
        db_session,
        user_id=user.id,
        url="https://future.example.com",
    )
    now = datetime.now(UTC)
    due_monitor.next_check_at = now - timedelta(seconds=1)
    future_monitor.next_check_at = now + timedelta(minutes=10)
    await db_session.commit()

    session_maker = async_sessionmaker(
        bind=db_session.bind,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    service = MonitorSchedulerService(session_maker)
    enqueued_monitor_ids: list[uuid.UUID] = []

    scheduled_count = await service.schedule_due_checks(enqueued_monitor_ids.append)

    await db_session.refresh(due_monitor)
    await db_session.refresh(future_monitor)

    assert scheduled_count == 1
    assert enqueued_monitor_ids == [due_monitor.id]
    assert due_monitor.last_scheduled_at is not None
    assert due_monitor.next_check_at == due_monitor.last_scheduled_at + timedelta(
        seconds=90
    )
    assert future_monitor.last_scheduled_at is None


def test_check_monitor_task_ignores_invalid_uuid(monkeypatch):
    was_called = False

    def fake_run_async(coro: Any) -> None:
        nonlocal was_called
        was_called = True

    monkeypatch.setattr(monitor_checks, "run_async", fake_run_async)

    monitor_checks.check_monitor_task.run("not-a-uuid")

    assert was_called is False


def test_check_monitor_task_runs_monitor_check(monkeypatch):
    monitor_id = uuid.uuid4()
    checked_monitor_ids: list[uuid.UUID] = []

    class FakeSessionContext:
        async def __aenter__(self) -> str:
            return "session"

        async def __aexit__(self, *args: Any) -> None:
            return None

    class FakeSessionMaker:
        def __call__(self) -> FakeSessionContext:
            return FakeSessionContext()

    class FakeMonitorCheckService:
        async def check_monitor(self, checked_monitor_id: uuid.UUID) -> None:
            checked_monitor_ids.append(checked_monitor_id)

    def fake_create_monitor_check_service(session: str) -> FakeMonitorCheckService:
        assert session == "session"
        return FakeMonitorCheckService()

    def fake_run_async(coro: Any) -> None:
        asyncio.run(coro)

    monkeypatch.setattr(monitor_checks, "async_session_maker", FakeSessionMaker())
    monkeypatch.setattr(
        monitor_checks,
        "create_monitor_check_service",
        fake_create_monitor_check_service,
    )
    monkeypatch.setattr(monitor_checks, "run_async", fake_run_async)

    monitor_checks.check_monitor_task.run(str(monitor_id))

    assert checked_monitor_ids == [monitor_id]


def test_schedule_checks_returns_scheduler_result(monkeypatch):
    class FakeSchedulerService:
        def __init__(self, session_maker: Any) -> None:
            assert session_maker is monitor_checks.async_session_maker

        async def schedule_due_checks(self, enqueue_check: Any) -> int:
            assert enqueue_check is monitor_checks._enqueue_monitor_check
            return 3

    def fake_run_async(coro: Any) -> int:
        return asyncio.run(coro)

    monkeypatch.setattr(
        monitor_checks,
        "MonitorSchedulerService",
        FakeSchedulerService,
    )
    monkeypatch.setattr(monitor_checks, "run_async", fake_run_async)

    assert monitor_checks.schedule_checks.run() == 3


def test_enqueue_monitor_check_sends_uuid_string(monkeypatch):
    monitor_id = uuid.uuid4()
    enqueued_monitor_ids: list[str] = []

    def fake_delay(enqueued_monitor_id: str) -> None:
        enqueued_monitor_ids.append(enqueued_monitor_id)

    monkeypatch.setattr(monitor_checks.check_monitor_task, "delay", fake_delay)

    monitor_checks._enqueue_monitor_check(monitor_id)

    assert enqueued_monitor_ids == [str(monitor_id)]

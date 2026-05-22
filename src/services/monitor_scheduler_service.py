import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.repositories.monitor_repository import MonitorRepository


class MonitorSchedulerService:
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        self.session_maker = session_maker

    async def schedule_due_checks(
        self, enqueue_check: Callable[[uuid.UUID], None]
    ) -> int:
        now = datetime.now(UTC)
        monitor_ids: list[uuid.UUID] = []

        async with self.session_maker() as session, session.begin():
            monitor_repository = MonitorRepository(session)
            monitors = await monitor_repository.get_due_monitors_for_update(now)

            for monitor in monitors:
                await monitor_repository.reserve_for_check(monitor, now)
                monitor_ids.append(monitor.id)

        for monitor_id in monitor_ids:
            enqueue_check(monitor_id)

        return len(monitor_ids)

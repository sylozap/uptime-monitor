import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.monitor import Monitor
from src.schemas.monitor import MonitorCreate, MonitorFilterParams


class MonitorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_monitor(
        self, user_id: uuid.UUID, monitor: MonitorCreate
    ) -> Monitor:
        db_monitor = Monitor(user_id=user_id, **monitor.model_dump(mode="json"))
        self.session.add(db_monitor)
        await self.session.flush()

        return db_monitor

    async def get_monitors(
        self, user_id: uuid.UUID, filters: MonitorFilterParams
    ) -> list[Monitor]:

        query = (
            select(Monitor)
            .where(Monitor.user_id == user_id)
            .order_by(Monitor.created_at, Monitor.id)
            .limit(filters.limit)
            .offset(filters.offset)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_monitor_by_id(
        self, id: uuid.UUID, user_id: uuid.UUID
    ) -> Monitor | None:
        query = select(Monitor).where(Monitor.id == id, Monitor.user_id == user_id)
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def update_monitor(
        self, monitor: Monitor, update_data: dict[str, Any]
    ) -> Monitor:
        for key, value in update_data.items():
            setattr(monitor, key, value)

        await self.session.flush()
        return monitor

    async def delete_monitor(self, monitor: Monitor) -> None:
        await self.session.delete(monitor)

    async def get_active_by_id_for_update(
        self, monitor_id: uuid.UUID
    ) -> Monitor | None:

        query = (
            select(Monitor)
            .where(Monitor.id == monitor_id, Monitor.is_active.is_(True))
            .with_for_update()
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def get_due_monitors_for_update(self, now: datetime) -> list[Monitor]:

        query = (
            select(Monitor)
            .where(
                or_(Monitor.next_check_at.is_(None), Monitor.next_check_at <= now),
            )
            .order_by(Monitor.next_check_at, Monitor.created_at, Monitor.id)
            .with_for_update(skip_locked=True)
        )

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def reserve_for_check(self, monitor: Monitor, now: datetime) -> None:

        monitor.last_scheduled_at = now

        monitor.next_check_at = now + timedelta(seconds=monitor.check_interval)

        await self.session.flush()

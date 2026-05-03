import uuid
from typing import Any

from sqlalchemy import select
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
        await self.session.commit()
        await self.session.refresh(db_monitor)

        return db_monitor

    async def get_monitors(
        self, user_id: uuid.UUID, filter_query: MonitorFilterParams
    ) -> list[Monitor]:

        limit = filter_query.limit
        offset = filter_query.offset

        query = (
            select(Monitor)
            .where(Monitor.user_id == user_id)
            .order_by(Monitor.created_at, Monitor.id)
            .limit(limit)
            .offset(offset)
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

        await self.session.commit()
        await self.session.refresh(monitor)
        return monitor

    async def delete_monitor(self, monitor: Monitor) -> None:
        await self.session.delete(monitor)
        await self.session.commit()

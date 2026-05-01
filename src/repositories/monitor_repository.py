import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.monitor import Monitor
from src.schemas.monitor import MonitorIn


class MonitorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_monitor(self, user_id: uuid.UUID, monitor: MonitorIn) -> Monitor:

        db_monitor = Monitor(user_id=user_id, **monitor.model_dump(mode="json"))

        self.session.add(db_monitor)
        await self.session.commit()
        await self.session.refresh(db_monitor)

        return db_monitor

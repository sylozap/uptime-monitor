import uuid

from src.models.monitor import Monitor
from src.repositories.monitor_repository import MonitorRepository
from src.schemas.monitor import MonitorFilterParams, MonitorIn


class MonitorService:
    def __init__(self, monitor_repository: MonitorRepository) -> None:
        self.monitor_repository = monitor_repository

    async def create_monitor(self, user_id: uuid.UUID, monitor: MonitorIn) -> Monitor:
        new_monitor = await self.monitor_repository.create_monitor(
            user_id=user_id, monitor=monitor
        )
        return new_monitor

    async def get_monitors(
        self, user_id: uuid.UUID, filter_query: MonitorFilterParams
    ) -> list[Monitor]:

        monitors = await self.monitor_repository.get_monitors(
            user_id=user_id, filter_query=filter_query
        )

        return monitors

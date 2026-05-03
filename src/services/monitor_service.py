import uuid

from src.core.exceptions import MonitorNotFoundError
from src.models.monitor import Monitor
from src.repositories.monitor_repository import MonitorRepository
from src.schemas.monitor import MonitorFilterParams, MonitorIn, MonitorUpdate


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

    async def get_monitor_by_id(self, id: uuid.UUID, user_id: uuid.UUID) -> Monitor:

        monitor = await self.monitor_repository.get_monitor_by_id(
            id=id, user_id=user_id
        )

        if monitor is None:
            raise MonitorNotFoundError()

        return monitor

    async def update_monitor(
        self, id: uuid.UUID, user_id: uuid.UUID, fields_to_update: MonitorUpdate
    ) -> Monitor:
        monitor = await self.monitor_repository.get_monitor_by_id(
            id=id, user_id=user_id
        )
        if not monitor:
            raise MonitorNotFoundError()

        update_data = fields_to_update.model_dump(exclude_unset=True, mode="json")

        if not update_data:
            return monitor

        updated_monitor = await self.monitor_repository.update_monitor(
            monitor=monitor, update_data=update_data
        )

        return updated_monitor

    async def delete_monitor(self, id: uuid.UUID, user_id: uuid.UUID) -> None:
        monitor_to_delete = await self.monitor_repository.get_monitor_by_id(
            id=id, user_id=user_id
        )

        if not monitor_to_delete:
            raise MonitorNotFoundError()

        await self.monitor_repository.delete_monitor(monitor=monitor_to_delete)

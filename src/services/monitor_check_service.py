import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.integrations.url_checker import PingResult, ping_url
from src.repositories.check_log_repository import CheckLogRepository
from src.repositories.monitor_repository import MonitorRepository
from src.services.incident_service import IncidentService


@dataclass(frozen=True)
class MonitorCheckConfig:
    id: uuid.UUID
    url: str
    timeout: int
    expected_status: int


class MonitorCheckService:
    def __init__(
        self,
        session: AsyncSession,
        monitor_repository: MonitorRepository,
        check_log_repository: CheckLogRepository,
        incident_service: IncidentService,
        ping_url: Callable[..., Awaitable[PingResult]] = ping_url,
    ) -> None:
        self.session = session
        self.ping_url = ping_url
        self.monitor_repository = monitor_repository
        self.check_log_repository = check_log_repository
        self.incident_service = incident_service

    async def check_monitor(self, monitor_id: uuid.UUID) -> None:
        monitor_config = await self._get_monitor_check_config(monitor_id)
        if monitor_config is None:
            return

        result = await self.ping_url(
            monitor_config.url,
            timeout=monitor_config.timeout,
            expected_status=monitor_config.expected_status,
        )

        await self._save_check_result(monitor_config.id, result)
        await self.session.commit()

    async def _get_monitor_check_config(
        self, monitor_id: uuid.UUID
    ) -> MonitorCheckConfig | None:

        monitor = await self.monitor_repository.get_active_by_id_for_update(monitor_id)

        if monitor is None:
            return None

        return MonitorCheckConfig(
            id=monitor.id,
            url=monitor.url,
            timeout=monitor.timeout,
            expected_status=monitor.expected_status,
        )

    async def _save_check_result(
        self, monitor_id: uuid.UUID, result: PingResult
    ) -> None:
        checked_at = datetime.now(UTC)

        monitor = await self.monitor_repository.get_active_by_id_for_update(monitor_id)
        if monitor is None:
            return

        await self.check_log_repository.create(
            monitor_id=monitor.id,
            response_time=result.response_time,
            status_code=result.status_code,
            is_available=result.is_available,
        )

        monitor.last_status = result.is_available
        monitor.last_status_code = result.status_code
        monitor.last_checked_at = checked_at
        monitor.next_check_at = checked_at + timedelta(seconds=monitor.check_interval)

        await self.incident_service.apply_check_result(
            monitor_id=monitor.id,
            result=result,
            checked_at=checked_at,
        )

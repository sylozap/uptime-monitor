import uuid
from datetime import datetime

from src.integrations.url_checker import PingResult
from src.repositories.incident_repository import IncidentRepository


class IncidentService:
    def __init__(self, incident_repository: IncidentRepository) -> None:
        self.incident_repository = incident_repository

    async def apply_check_result(
        self,
        *,
        monitor_id: uuid.UUID,
        result: PingResult,
        checked_at: datetime,
    ) -> None:
        open_incidents = await self.incident_repository.get_open_by_monitor_id(
            monitor_id
        )

        if not result.is_available and not open_incidents:
            await self.incident_repository.create(
                monitor_id=monitor_id,
                started_at=checked_at,
                error_type=result.error_type or "unknown",
            )
            return

        if result.is_available:
            for incident in open_incidents:
                incident.ended_at = checked_at

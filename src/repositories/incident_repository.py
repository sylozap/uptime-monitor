import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.incident import Incident


class IncidentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_open_by_monitor_id(self, monitor_id: uuid.UUID) -> list[Incident]:
        result = await self.session.execute(
            select(Incident).where(
                Incident.monitor_id == monitor_id,
                Incident.ended_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def create(
        self,
        *,
        monitor_id: uuid.UUID,
        started_at: datetime,
        error_type: str,
    ) -> Incident:
        incident = Incident(
            monitor_id=monitor_id,
            started_at=started_at,
            error_type=error_type,
        )
        self.session.add(incident)
        await self.session.flush()
        return incident

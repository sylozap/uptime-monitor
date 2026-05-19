import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.check_log import CheckLog


class CheckLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        monitor_id: uuid.UUID,
        response_time: int,
        status_code: int | None,
        is_available: bool,
    ) -> CheckLog:
        check_log = CheckLog(
            monitor_id=monitor_id,
            response_time=response_time,
            status_code=status_code,
            is_available=is_available,
        )
        self.session.add(check_log)
        await self.session.flush()
        return check_log

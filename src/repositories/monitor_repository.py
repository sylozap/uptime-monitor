from sqlalchemy.ext.asyncio import AsyncSession


class MonitorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

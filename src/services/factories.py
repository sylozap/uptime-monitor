# В новом файле src/services/factories.py
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.check_log_repository import CheckLogRepository
from src.repositories.incident_repository import IncidentRepository
from src.repositories.monitor_repository import MonitorRepository
from src.services.incident_service import IncidentService
from src.services.monitor_check_service import MonitorCheckService


def create_monitor_check_service(session: AsyncSession) -> MonitorCheckService:
    monitor_repository = MonitorRepository(session)
    check_log_repository = CheckLogRepository(session)
    incident_repository = IncidentRepository(session)
    incident_service = IncidentService(incident_repository)

    return MonitorCheckService(
        session=session,
        monitor_repository=monitor_repository,
        check_log_repository=check_log_repository,
        incident_service=incident_service,
    )

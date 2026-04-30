from typing import Annotated

from fastapi import Depends

from src.repositories.dependencies import MonitorRepositoryDep, UserRepositoryDep
from src.services.auth_service import AuthService
from src.services.monitor_service import MonitorService


async def get_auth_service(user_repository: UserRepositoryDep):
    return AuthService(user_repository)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_monitor_service(monitor_repository: MonitorRepositoryDep):
    return MonitorService(monitor_repository)


MonitorServiceDep = Annotated[MonitorService, Depends(get_monitor_service)]

from typing import Annotated

from fastapi import Depends

from src.repositories.dependencies import get_monitor_repository, get_user_repository
from src.repositories.monitor_repository import MonitorRepository
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
from src.services.monitor_service import MonitorService


async def get_auth_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
):
    return AuthService(user_repository)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_monitor_service(
    monitor_repository: Annotated[MonitorRepository, Depends(get_monitor_repository)],
):
    return MonitorService(monitor_repository)


MonitorServiceDep = Annotated[MonitorService, Depends(get_monitor_service)]

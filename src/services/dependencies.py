from typing import Annotated

from fastapi import Depends

from src.repositories.dependencies import get_user_repository
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService


async def get_auth_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
):
    return AuthService(user_repository)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

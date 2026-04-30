from typing import Annotated

from fastapi import Depends

from src.database.dependencies import SessionDep
from src.repositories.user_repository import UserRepository


async def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]

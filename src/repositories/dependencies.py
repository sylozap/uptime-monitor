from src.database.dependencies import SessionDep
from src.repositories.user_repository import UserRepository


async def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)

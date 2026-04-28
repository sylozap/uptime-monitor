import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.core.exceptions import InactiveUserError, InvalidTokenError
from src.core.security import decode_token
from src.models.user import User
from src.repositories.dependencies import get_user_repository
from src.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:

    payload = decode_token(token)

    if payload is None:
        raise InvalidTokenError()

    if payload.get("type") != "access":
        raise InvalidTokenError()

    user_id = payload.get("sub")

    if user_id is None:
        raise InvalidTokenError()

    user = await user_repository.get_by_id(uuid.UUID(user_id))

    if user is None:
        raise InvalidTokenError()

    if not user.is_active:
        raise InactiveUserError()

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]

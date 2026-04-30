from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.core.exceptions import InactiveUserError, InvalidTokenError
from src.core.security import decode_token
from src.core.utils import parse_uuid
from src.models.user import User
from src.repositories.dependencies import UserRepositoryDep
from src.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repository: UserRepositoryDep,
) -> User:

    payload = decode_token(token)

    if payload is None:
        raise InvalidTokenError()

    if payload.get("type") != "access":
        raise InvalidTokenError()

    user_id = payload.get("sub")

    if user_id is None:
        raise InvalidTokenError()

    user = await user_repository.get_by_id(parse_uuid(user_id, InvalidTokenError))

    if user is None:
        raise InvalidTokenError()

    if not user.is_active:
        raise InactiveUserError()

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]

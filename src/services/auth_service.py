from sqlalchemy.exc import IntegrityError

from src.core.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UserAlreadyExistsError,
)
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from src.core.utils import parse_access_token_user_id
from src.repositories.user_repository import UserRepository
from src.schemas.token import Token
from src.schemas.user import UserIn


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def register_user(self, user: UserIn):
        normalized_email = user.email.lower()

        user_with_existing_email = await self.user_repository.get_by_email(
            normalized_email
        )

        if user_with_existing_email:
            raise UserAlreadyExistsError()

        hashed_password = get_password_hash(user.password)
        try:
            new_user = await self.user_repository.create_user(
                email=normalized_email,
                hashed_password=hashed_password,
            )
        except IntegrityError as exc:
            raise UserAlreadyExistsError() from exc

        return new_user

    async def login_user(self, email: str, password: str) -> Token:
        normalized_email = email.lower()
        user = await self.user_repository.get_by_email(normalized_email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InactiveUserError()

        access_token = create_access_token(user_id=str(user.id))
        refresh_token = create_refresh_token(user_id=str(user.id))

        return Token(access_token=access_token, refresh_token=refresh_token)

    async def refresh_token(self, refresh_token: str) -> Token:
        payload: dict | None = decode_token(refresh_token)

        if payload is None:
            raise InvalidRefreshTokenError()

        if payload.get("type") != "refresh":
            raise InvalidRefreshTokenError()

        user_id = payload.get("sub")

        if user_id is None:
            raise InvalidRefreshTokenError()

        user = await self.user_repository.get_by_id(parse_access_token_user_id(user_id))

        if user is None:
            raise InvalidRefreshTokenError()

        if not user.is_active:
            raise InactiveUserError()

        return Token(
            access_token=create_access_token(user_id=str(user.id)),
            refresh_token=create_refresh_token(user_id=str(user.id)),
        )

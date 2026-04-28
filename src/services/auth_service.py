from src.core.exceptions import AuthorizationError, UserAlreadyExistsError
from src.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
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
            raise UserAlreadyExistsError(message="User with this email already exists")

        hashed_password = get_password_hash(user.password)

        new_user = await self.user_repository.create_user(
            email=normalized_email,
            hashed_password=hashed_password,
        )

        return new_user

    async def login_user(self, email: str, password: str) -> Token:
        normalized_email = email.lower()
        user = await self.user_repository.get_by_email(normalized_email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthorizationError(message="Invalid username or password")

        access_token = create_access_token(user_id=str(user.id))
        refresh_token = create_refresh_token(user_id=str(user.id))

        return Token(access_token=access_token, refresh_token=refresh_token)

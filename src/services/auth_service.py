from src.core.exceptions import UserAlreadyExistsError
from src.core.security import get_password_hash
from src.repositories.user_repository import UserRepository
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

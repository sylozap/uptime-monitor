from fastapi import status


class BaseAppError(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "Internal server error"
    code: str = "internal_error"
    headers: dict[str, str] | None = None

    def __init__(self, message: str | None = None, code: str | None = None) -> None:
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

        super().__init__(self.message)


class UserAlreadyExistsError(BaseAppError):
    status_code = status.HTTP_409_CONFLICT
    message = "User with this email already exists"
    code = "user_already_exists"


class InvalidCredentialsError(BaseAppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid email or password"
    code = "invalid_credentials"


class InvalidTokenError(BaseAppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Could not validate credentials"
    code = "invalid_token"
    headers = {"WWW-Authenticate": "Bearer"}


class InvalidRefreshTokenError(BaseAppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid refresh token"
    code = "invalid_refresh_token"
    headers = {"WWW-Authenticate": "Bearer"}


class InactiveUserError(BaseAppError):
    status_code = status.HTTP_403_FORBIDDEN
    message = "User account is inactive"
    code = "inactive_user"


class MonitorNotFoundError(BaseAppError):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Monitor not found"
    code = "monitor_not_found"

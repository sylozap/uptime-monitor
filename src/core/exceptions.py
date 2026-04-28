class BaseAppError(Exception):
    def __init__(self, message: str):
        self.message = message


class UserAlreadyExistsError(BaseAppError):
    pass


class AuthorizationError(BaseAppError):
    pass

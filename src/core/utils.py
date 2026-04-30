import uuid

from src.core.exceptions import BaseAppError


def parse_uuid(user_id: str, error_cls: type[BaseAppError]) -> uuid.UUID:
    try:
        return uuid.UUID(user_id)
    except (TypeError, ValueError) as exc:
        raise error_cls() from exc

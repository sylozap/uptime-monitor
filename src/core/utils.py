import uuid

from src.core.exceptions import BaseAppError


def parse_uuid(value: str, error_cls: type[BaseAppError]) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except (TypeError, ValueError) as exc:
        raise error_cls() from exc

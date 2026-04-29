import uuid

from src.core.exceptions import InvalidTokenError


def parse_uuid(user_id: str) -> uuid.UUID:
    try:
        return uuid.UUID(user_id)
    except (TypeError, ValueError) as exc:
        raise InvalidTokenError() from exc

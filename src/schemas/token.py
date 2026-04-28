import uuid

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105


class TokenData(BaseModel):
    user_id: uuid.UUID

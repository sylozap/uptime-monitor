import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BaseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    email: EmailStr = Field(max_length=255)


class UserIn(BaseUser):
    password: str = Field(min_length=6, max_length=30)


class UserOut(BaseUser):
    id: uuid.UUID
